import os

from docx import Document
from dotenv import load_dotenv
from pinecone import Pinecone

# load_dotenv

# pinecone_api_key = os.getenv("PINECONE_API_KEY")

# if pinecone_api_key:
#     print(f"PineconeAPiKey: {pinecone_api_key}")

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not PINECONE_API_KEY:
    raise ValueError("Pinecone API key not found")

pc = Pinecone(
    api_key=PINECONE_API_KEY,
)

if not pc.has_index(PINECONE_INDEX_NAME):
    pc.create_index_for_model(
        name=PINECONE_INDEX_NAME,
        cloud="aws",
        region="us-east-1",
        embed={"model": "llama-text-embed-v2", "field_map": {"text": "chunk_text"}},
    )


def add_text_document(file_path: str, namespace: str = "example_namespace"):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".docx":
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)

    else:
        with open(file_path, "r", encoding="utf-8", error="ignore") as f:
            text = f.read()

    chunk_size = 500
    overlap = 100
    # chunks= [
    #     text[i : i + chunk_size]
    #     for i in range(0, len(text), chunk_size)
    # ]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # move start forward by (chunk_size - overlap)
        start += chunk_size - overlap

    records = []

    for idx, chunk in enumerate(chunks, start=1):
        records.append(
            {
                "_id": f"takhleeq_doc_chunk{idx}",
                "chunk_text": chunk,
                "text": chunk,
                "category": "takhleeq_kb",
            }
        )

    dense_index = pc.Index(index_name)

    dense_index.upsert_records(namespace, records)


add_text_document(
    "docs/Takhleeq_Chatbot_Knowledge_Base.docx", namespace="example_namespace"
)
