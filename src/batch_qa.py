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

# --- Prompt helper (identical to main.py) ---
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
        "You are a friendly and helpful AI assistant specialised in analysing Pit-Void data.\n"
        "Think step-by-step, reference the provided context, and verify each conclusion before you state it.\n"
        "First provide a brief rationale (labelled ‘Reasoning’) then give the final answer (labelled ‘Answer’).\n"
        "Cite the document title in square brackets whenever you use information from it. "
        "If the context is insufficient, simply say you do not know.\n\n"
        f"{history_block}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

# Tiny CLI spinner (copied from main.py)
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
        # clear line
        sys.stdout.write("\r" + " " * (len(self._msg) + 4) + "\r")
        sys.stdout.flush()

    def _spin(self):
        for ch in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r{self._msg} {ch}")
            sys.stdout.flush()
            time.sleep(0.1)

def main():
    load_dotenv()
    foundry_endpoint = os.getenv("FOUNDARY_MODEL_ENDPOINT")
    foundry_key = os.getenv("FOUNDARY_API_KEY")
    if not all([foundry_endpoint, foundry_key]):
        raise EnvironmentError("FOUNDARY_MODEL_ENDPOINT and FOUNDARY_API_KEY must be set.")

    foundry_client = FoundryClient(api_key=foundry_key, endpoint=foundry_endpoint)

    # Read questions
    with open("src/questions.txt", "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()][:10]

    os.makedirs("outputs", exist_ok=True)
    history: List[Tuple[str, str]] = []

    for idx, question in enumerate(questions, 1):
        print(f"Processing Q{idx}: {question}")
        search_results = query_pit_voids(question, top=10)
        prompt = prepare_prompt(question, search_results, history)
        with _Spinner():
            response = foundry_client.get_response(prompt)
        history.append((question, response))
        # Save output as plain text
        with open(f"outputs/response_{idx:02d}.txt", "w", encoding="utf-8") as outf:
            outf.write(f"Question: {question}\n\n")
            outf.write(f"Response:\n{response}\n")

if __name__ == "__main__":
    main()