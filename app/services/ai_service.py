
import ollama
import json

def extract_document_details(document_text: str):

    prompt = f"""
    You are an intelligent document understanding system.

    Analyze the provided document.

    Your tasks:

    1. Identify the document type.
    2. Identify its category and subcategory.
    3. Extract ALL relevant information present
       in the document.
    4. Create field names dynamically based on
       the actual content.
    5. Do not use predefined fields.
    6. Do not invent missing information.
    7. Include confidence scores where possible.
    8. Include page references when available.
    9. Generate a concise document summary.

    Return valid JSON using this structure:

    {{
        "document_type": "",
        "category": "",
        "subcategory": "",
        "extracted_fields": {{}},
        "summary": "",
        "important_details": [],
        "full_text": ""
    }}

    Document content:
    {document_text}
    """

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    return json.loads(
        response["message"]["content"]
    )
