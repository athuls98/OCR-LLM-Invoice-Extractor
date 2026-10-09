import json
import requests


LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"


def extract_invoice_with_ai(text):
    prompt = f"""
Extract the invoice information from the document below.

Return ONLY valid JSON in this exact format:

{{
    "invoice_number": "",
    "invoice_date": "",
    "vendor_name": "",
    "subtotal": 0.0,
    "tax": 0.0,
    "total": 0.0,
    "currency": ""
}}

Document:

{text}
"""

    response = requests.post(
        LLM_URL,
        json={
            "model": "gemma3-12b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0
        },
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    content = result["choices"][0]["message"]["content"]

    content = content.strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()

    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    return json.loads(content)
