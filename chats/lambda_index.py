import os
import pickle
from llama_index.readers.file import FlatReader
from pathlib import Path

from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import VectorStoreIndex

from llama_index.core.node_parser import (
    UnstructuredElementNodeParser,
)

from django.conf import settings

def init():
    reader = FlatReader()
    file_path = Path(settings.BASE_DIR) / 'chats' / 'data' / 'test.html'
    qr_2023 = reader.load_data(file_path)

    node_parser = UnstructuredElementNodeParser()

    ## loads the pickle document
    if not os.path.exists("qr_2023_nodes.pkl"):
        qr_2023_raw_nodes = node_parser.get_nodes_from_documents(qr_2023)
        pickle.dump(qr_2023_raw_nodes, open("qr_2023_nodes.pkl", "wb"))

    qr_2023_raw_nodes = node_parser.get_nodes_from_documents(qr_2023)

    base_nodes_qr_2023, node_mappings_qr_2023 = node_parser.get_base_nodes_and_mappings(
        qr_2023_raw_nodes
    )

    vector_index = VectorStoreIndex(base_nodes_qr_2023)
    vector_retriever = vector_index.as_retriever(similarity_top_k=10)
    vector_query_engine = vector_index.as_query_engine(similarity_top_k=10)


    recursive_retriever = RecursiveRetriever(
        "vector",
        retriever_dict={"vector": vector_retriever},
        node_dict=node_mappings_qr_2023,
        #verbose=True
    )
    query_engine = RetrieverQueryEngine.from_args(recursive_retriever)
    return query_engine

def query_lambda_index(query_prompt):
    query_engine = init()
    response = query_engine.query(query_prompt)
    return str(response)
