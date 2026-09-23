"""
Part 2 -- Gemini measurement.

Google Gemini Developer API version.

API key:
    GEMINI_API_KEY in .env

Run:
    python part2_measure.py
        Count tokens only.

    python part2_measure.py --call
        Count tokens and make real requests.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from google import genai

from texts import CORPUS, LANGUAGES


load_dotenv()

OUTPUT_PATH = Path(__file__).with_name("measurements.json")

MODEL_ID = "gemini-3.6-flash"

MAX_OUTPUT_TOKENS = 2048


def create_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found in .env"
        )

    return genai.Client(api_key=api_key)


def count_plain_text_tokens(
    client: genai.Client,
    text: str,
) -> int:
    """
    Count tokens for a plain text string.
    """
    response = client.models.count_tokens(
        model=MODEL_ID,
        contents=text,
    )

    return int(response.total_tokens)


def count_request_tokens(
    client: genai.Client,
    system_prompt: str,
    complaint: str,
) -> int:
    """
    Count the approximate token cost of the actual request.

    Gemini Developer API's count_tokens endpoint does not accept
    system_instruction in the same way as generate_content.

    Therefore we construct the same logical request as text:
        SYSTEM PROMPT
        + COMPLAINT
    """

    combined = (
        "SYSTEM INSTRUCTION:\n"
        + system_prompt
        + "\n\n"
        + "USER:\n"
        + complaint
    )

    return count_plain_text_tokens(client, combined)


def generate_answer(
    client: genai.Client,
    system_prompt: str,
    complaint: str,
):
    """
    Make one real Gemini request.
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=complaint,
        config={
            "system_instruction": system_prompt,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "temperature": 0,
        },
    )

    return response


def main() -> int:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--call",
        action="store_true",
        help="send real Gemini requests",
    )

    args = parser.parse_args()

    print(f"Gemini model: {MODEL_ID}")

    try:
        client = create_client()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # ---------------------------------------------------------
    # 1. Count every corpus item
    # ---------------------------------------------------------

    token_counts: Dict[str, Dict[str, int]] = {}

    print("\nCounting tokens...")
    print("(No generated answers yet.)\n")

    for item_name, versions in CORPUS.items():

        token_counts[item_name] = {}

        for lang in LANGUAGES:

            try:
                tokens = count_plain_text_tokens(
                    client,
                    versions[lang],
                )

                token_counts[item_name][lang] = tokens

            except Exception as exc:

                print(
                    f"Token counting failed for "
                    f"{item_name}/{lang}: {exc}",
                    file=sys.stderr,
                )

                return 1

        print(
            f"  {item_name:<15}"
            + "  ".join(
                f"{lang}={token_counts[item_name][lang]}"
                for lang in LANGUAGES
            )
        )

    # ---------------------------------------------------------
    # 2. Count actual request
    # ---------------------------------------------------------

    request_tokens: Dict[str, int] = {}

    print("\nActual request token counts:")
    print("(system prompt + complaint)\n")

    for lang in LANGUAGES:

        try:

            request_tokens[lang] = count_request_tokens(
                client,
                CORPUS["system_prompt"][lang],
                CORPUS["complaint"][lang],
            )

        except Exception as exc:

            print(
                f"Request token counting failed for "
                f"{lang}: {exc}",
                file=sys.stderr,
            )

            return 1

    print(
        "  request        "
        + "  ".join(
            f"{lang}={request_tokens[lang]}"
            for lang in LANGUAGES
        )
    )

    # ---------------------------------------------------------
    # 3. Real model calls
    # ---------------------------------------------------------

    results = {}

    if args.call:

        print(
            "\nSending real requests to Gemini..."
        )

        for lang in LANGUAGES:

            print(f"\n[{lang}]")

            system_prompt = CORPUS["system_prompt"][lang]
            complaint = CORPUS["complaint"][lang]

            try:

                response = generate_answer(
                    client,
                    system_prompt,
                    complaint,
                )

                print("\n--- ANSWER ---")

                if response.text:
                    print(response.text)
                else:
                    print("[empty response]")

                print("\n--- USAGE ---")

                usage = response.usage_metadata

                if usage:

                    input_tokens = int(
                        usage.prompt_token_count or 0
                    )

                    output_tokens = int(
                        usage.candidates_token_count or 0
                    )

                    thinking_tokens = int(
                        getattr(
                            usage,
                            "thoughts_token_count",
                            0,
                        )
                        or 0
                    )

                    print(
                        f"input tokens:  {input_tokens}"
                    )

                    print(
                        f"output tokens: {output_tokens}"
                    )

                    print(
                        f"thinking tokens: {thinking_tokens}"
                    )

                    results[lang] = {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "thinking_tokens": thinking_tokens,
                    }

                else:

                    print(
                        "WARNING: usage metadata unavailable."
                    )

            except Exception as exc:

                print(
                    f"Gemini request failed: {exc}",
                    file=sys.stderr,
                )

                return 1

    # ---------------------------------------------------------
    # 4. Save measurements.json
    # ---------------------------------------------------------

    measurements = {
        "provider": "Google Gemini",
        "model": MODEL_ID,
        "token_counts": token_counts,
        "request_tokens": request_tokens,
        "one_request_billed": (
            results if results else None
        ),
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            measurements,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\nWrote {OUTPUT_PATH.name}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())