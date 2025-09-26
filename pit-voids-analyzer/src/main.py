# main.py

import os
import logging          # ← add
from chat import Chat
from azure_search import query_pit_voids
from foundry_client import FoundryClient
from typing import List, Tuple
from dotenv import load_dotenv                 # ensure env is loaded
import sys
import threading
import itertools
import time

# Silence noisy INFO output from httpx / Azure SDK
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)

# -------------------------------------------------------------
# Prompt-engineering helper
# -------------------------------------------------------------
def prepare_prompt(
    question: str,
    search_results: List[Tuple[str, str]],
    history: List[Tuple[str, str]],
) -> str:
    """
    Build a prompt that passes retrieved snippets (grounding data)
    to the o3-mini model and keeps conversational context.
    """
    # previous turns
    history_lines = [
        f"User: {q}\nAssistant: {a}" for q, a in history
    ]
    history_block = "\n".join(history_lines)

    context_lines = [
        f"- [{title}] {snippet}" for title, snippet in search_results
    ] or ["No relevant context found."]
    context = "\n".join(context_lines)

    return (
        # ---- expanded system prompt ----
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

# -------------------------------------------------------------
# tiny CLI spinner ------------------------------------------------
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
        sys.stdout.write("\r" + " " * (len(self._msg) + 6) + "\r")
        sys.stdout.flush()

    def _spin(self):
        # Use a sequence of "thinking" and mining-related emojis (plus a cat!)
        for ch in itertools.cycle([
            "🤔", "🧐", "💭", "🤨", "🤓", "💡", "⛏️", "🪨", "🚧", "🦺", "⛏️", "🐾", "🐱"
        ]):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r{self._msg} {ch}")
            sys.stdout.flush()
            time.sleep(0.5)  # slower spin for better UX

# -------------------------------------------------------------
def main():
    # Load environment variables from .env
    load_dotenv()

    # Initialise clients
    foundry_endpoint = os.getenv("FOUNDARY_MODEL_ENDPOINT")
    foundry_key = os.getenv("FOUNDARY_API_KEY")
    if not all([foundry_endpoint, foundry_key]):
        raise EnvironmentError("FOUNDARY_MODEL_ENDPOINT and FOUNDARY_API_KEY must be set.")

    foundry_client = FoundryClient(api_key=foundry_key, endpoint=foundry_endpoint)
    chat = Chat(foundry_client)

    print("Welcome to PitPixie! 🕳️")
    print("You can ask questions about Pit Voids. Type 'exit' to quit.")

    history: List[Tuple[str, str]] = []   # (user, assistant) pairs

    while True:
        user_input = chat.get_user_input()
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Good-bye!")
            break

        # 1. Retrieve grounding data
        search_results = query_pit_voids(user_input, top=10)

        # 2. Compose prompt with context + conversation memory
        prompt = prepare_prompt(user_input, search_results, history)

        # 3. Send to model (show spinner while waiting)
        with _Spinner():
            response = foundry_client.get_response(prompt)

        # 4. Display
        chat.display_response(response)

        # 5. store the turn for future context
        history.append((user_input, response))

if __name__ == "__main__":
    main()