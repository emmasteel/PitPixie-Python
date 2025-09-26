import json
import csv
import os

INPUT_JSON = "outputs/batch_responses.json"
OUTPUT_CSV = "outputs/batch_responses.csv"

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    responses = data.get("responses", [])

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["prompt", "answer", "references"])
        for resp in responses:
            prompt = resp.get("prompt", "")
            answer = resp.get("answer", "")
            # Join references as a semicolon-separated string
            references = resp.get("references", [])
            references_str = "; ".join(references)
            writer.writerow([prompt, answer, references_str])

    print(f"CSV written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()