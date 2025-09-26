"""
chat.py
Simple wrapper that:
1. Reads user input from stdin.
2. Prints model responses in a chat-like format.
"""

from typing import List


class Chat:
    """Console chat interface."""

    def __init__(self, foundry_client):
        self.foundry_client = foundry_client
        self.history: List[dict[str, str]] = []  # optional message log

    # -------------------------------------------------------------
    # Public helpers expected by main.py
    # -------------------------------------------------------------
    def get_user_input(self) -> str:
        """Prompt the user and return the typed question."""
        return input("\nYou: ")

    def display_response(self, text: str) -> None:
        """Pretty-print the model reply."""
        print(f"\nPitPixie:\n{text}\n")
        # store in local history if you need it later
        self.history.append({"role": "assistant", "content": text})

    def start_chat(self):
        print("Welcome to PitPixie! 🕳️ Type 'exit' to end the chat.")
        while True:
            user_input = self.get_user_input()
            if user_input.lower() == 'exit':
                print("Ending chat. Goodbye!")
                break
            response = self.foundry_client.get_response(user_input)
            self.display_response(response)