# pdf_extractor.py
# Combined script for PDF extraction and table markdown conversion

import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

from unstructured.partition.pdf import partition_pdf
import fitz
from openai import OpenAI

# Set up OpenAI API key
def get_openai_api_key():
    load_dotenv()
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    else:
        raise ValueError("OPENAI_API_KEY not found in .env file.")

OPENAI_API_KEY = get_openai_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

filename = "/Users/rohanmunshi/Desktop/Restack-hackathon/sample-invoice.pdf"

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def get_table_description(table_content, document_context):
    prompt = f"""
    Given the following table and its context from the original document,
    provide the table in markdown format.

    Original Document Context:
    {document_context}

    Table Content:
    {table_content}

    Please provide:
    1. The table in proper markdown format.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that formats the in markdown."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def main():
    elements = partition_pdf(filename, strategy="hi_res")
    pdf_path = filename
    document_content = extract_text_from_pdf(pdf_path)
    markdown_tables = []
    for element in elements:
        if element.to_dict()['type'] == 'Table':
            table_content = element.to_dict()['text']
            result = get_table_description(table_content, document_content)
            element.text = result
            markdown_tables.append(result)
    print("Processing complete.")
    for table in markdown_tables:
        print(table)

if __name__ == "__main__":
    main()
