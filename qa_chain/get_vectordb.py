import sys 
# sys.path.append("../embedding") 
# sys.path.append("../database") 

from langchain.embeddings.openai import OpenAIEmbeddings    # 调用 OpenAI 的 Embeddings 模型
import os
from embedding.zhipuai_embedding import ZhipuAIEmbeddings
from database.create_db import create_db,load_knowledge_db
from embedding.call_embedding import get_embedding

def get_vectordb(file_path:str=None, persist_path:str=None, embedding = "openai",embedding_key:str=None):
    """
    Returns the vector database object
    Input parameters:
    question:
    llm:
    vectordb: Vector database (required parameter), an object
    template: Prompt template (optional parameter). You can design your own prompt template, or use the default one.
    embedding: You can use embeddings such as ZhipuAI. If this parameter is not provided, OpenAI embeddings will be used by default. Note that the api_key must be entered correctly in this case.
    """
    embedding = get_embedding(embedding=embedding, embedding_key=embedding_key)
    if os.path.exists(persist_path): 
        contents = os.listdir(persist_path)
        if len(contents) == 0: 

            vectordb = create_db(file_path, persist_path, embedding)
            vectordb = load_knowledge_db(persist_path, embedding)
        else:
            vectordb = load_knowledge_db(persist_path, embedding)
    else: 
        vectordb = create_db(file_path, persist_path, embedding)
        vectordb = load_knowledge_db(persist_path, embedding)

    return vectordb