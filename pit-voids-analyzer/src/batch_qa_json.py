import os
import json
from typing import List, Tuple
from dotenv import load_dotenv
from azure_search import query_pit_voids
from foundry_client import FoundryClient
import logging
import threading
import itertools
import sys
import time

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)

def prepare_prompt(
    question: str,
    search_results: List[Tuple[str, str]],
    history: List[Tuple[str, str]],
) -> str:
    history_lines = [
        f"User: {q}\nAssistant: {a}" for q, a in history
    ]
    history_block = "\n".join(history_lines)
    context_lines = [
        f"- [{title}] {snippet}" for title, snippet in search_results
    ] or ["No relevant context found."]
    context = "\n".join(context_lines)
    return (
        "You are a specialised AI for Pit-Void analysis.\n"
        "Instructions:\n"
        "- Answer as concisely as possible. If the question asks for a quantity, only provide the number. "
        "If the question implies an area or total, only provide the final value.\n"
        "Try to limit your response to 20 words maximum.\n"
        "- Use the provided context to answer the question.\n"
        "Build on the historical context of the conversation.\n"
        "- Do not include extra explanation or reasoning unless explicitly requested, however do take the time to do extra reasoning to ensure completeness of your answer.\n"
        "- If the context is insufficient, reply with your best effort, or if you are really struggling reply 'unknown'.\n\n"
        f"{history_block}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

class _Spinner:
    def __init__(self, message: str = "Thinking"):
        self._msg = message
        self._stop = threading.Event()
        self._th = threading.Thread(target=self._spin, daemon=True)

    def __enter__(self):
        self._th.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop.set()
        self._th.join()
        sys.stdout.write("\r" + " " * (len(self._msg) + 4) + "\r")
        sys.stdout.flush()

    def _spin(self):
        for ch in itertools.cycle(["🤔", "🧐", "💭", "🤨", "🤓", "💡", "⛏️", "🪨", "🚧", "🦺", "🐱"]):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r{self._msg} {ch}")
            sys.stdout.flush()
            time.sleep(0.3)

def extract_references(search_results: List[Tuple[str, str]]) -> List[str]:
    # Extract unique document titles from the context
    return list({title for title, _ in search_results})

def main():
    load_dotenv()
    foundry_endpoint = os.getenv("FOUNDARY_MODEL_ENDPOINT")
    foundry_key = os.getenv("FOUNDARY_API_KEY")
    if not all([foundry_endpoint, foundry_key]):
        raise EnvironmentError("FOUNDARY_MODEL_ENDPOINT and FOUNDARY_API_KEY must be set.")

    foundry_client = FoundryClient(api_key=foundry_key, endpoint=foundry_endpoint)

    # Read all questions
    with open("src/questions.txt", "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    os.makedirs("outputs", exist_ok=True)
    history: List[Tuple[str, str]] = []
    responses = []

    for idx, question in enumerate(questions, 1):
        print(f"Processing Q{idx}: {question}")
        search_results = query_pit_voids(question, top=10)
        prompt = prepare_prompt(question, search_results, history)
        with _Spinner():
            answer = foundry_client.get_response(prompt)
        history.append((question, answer))
        references = extract_references(search_results)
        responses.append({
            "prompt": question,
            "answer": answer,
            "references": references
        })

    # Write all responses to a single JSON file (schema-compliant)
    output_obj = {"responses": responses}
    with open("outputs/batch_responses.json", "w", encoding="utf-8") as outf:
        json.dump(output_obj, outf, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()