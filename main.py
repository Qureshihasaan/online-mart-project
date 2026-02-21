import time, os
from pinecone import Pinecone
from docx import Document


# load_dotenv

# pinecone_api_key = os.getenv("PINECONE_API_KEY")

# if pinecone_api_key:
#     print(f"PineconeAPiKey: {pinecone_api_key}")

pc = Pinecone(api_key="pcsk_5YwpqR_24TdW8ouSZczSCKfqGnZ5xjj25XL9HvUBo1WaSJ4gCc4WUcRgzVsgbpcPfVt6zr")

index_name = "ai-vector-embeddings"

if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud= "aws",
        region="us-east-1",
        embed= {
            "model" : "llama-text-embed-v2",
            "field_map": {"text":"chunk_text"}
         }
    )

def add_text_document(file_path: str, namespace: str = "example_namespace"):
    ext= os.path.splitext(file_path)[1].lower()

    if ext == ".docx":
        doc= Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)

    else:
        with open(file_path, "r", encoding="utf-8", error= "ignore") as f:
            text= f.read()

    chunk_size= 500
    overlap = 100
    # chunks= [
    #     text[i : i + chunk_size]
    #     for i in range(0, len(text), chunk_size)
    # ]
    chunks=[]
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # move start forward by (chunk_size - overlap)
        start += chunk_size - overlap

    records = []

    for idx, chunk in enumerate(chunks, start=1):
        records.append({
            "_id": f"takhleeq_doc_chunk{idx}",
            "chunk_text": chunk,
            "text": chunk,
            "category": "takhleeq_kb"
        })


    dense_index = pc.Index(index_name)

    dense_index.upsert_records(namespace, records)

add_text_document("docs/Takhleeq_Chatbot_Knowledge_Base.docx" , namespace="example_namespace")




dense_index = pc.Index(index_name)

query = "What is Takhleeq?"  # <-- Set your search query here

result = dense_index.search(
    namespace="example_namespace",
    query={
        "top_k":100,
        "inputs":{
        "text": query
        }
    },
    rerank={
        "model":"bge-reranker-v2-m3",
        "top_n":100,
        "rank_fields": ["chunk_text"]
    },
)

for hit in result["result"]["hits"]:
    print(
        f'id: {hit["_id"]:<20} | '
        f'score: {round(hit["_score"], 2):<5} | '
        f'text: {hit["fields"]["chunk_text"][:120]}'
    )


add_text_document("docs/Takhleeq_Chatbot_Knowledge_Base.docx" , namespace="example_namespace")