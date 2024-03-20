import cohere
import os
from dotenv import load_dotenv
load_dotenv()
# init client
key = os.getenv("RERANK_API_KEY")
print(key, "KKKEEEYY")
co = cohere.Client(key)
def rerank_docs(query, documents, top_n, model):
    return co.rerank(
        query=query, documents=documents, top_n=top_n, model=model
    )
