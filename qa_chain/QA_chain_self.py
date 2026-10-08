from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
import sys
sys.path.append("../")
from qa_chain.model_to_llm import model_to_llm
import sys
import re

class QA_chain_self():
    """
    Question-answering chain without history

    - model: Name of the model being called
    - temperature: Temperature coefficient, controls the randomness of generation
    - top_k: Returns the top k similar documents from retrieval
    - file_path: Path where the files for building the database are located
    - persist_path: Persistence path of the vector database
    - appid: Required for Spark
    - api_key: Required for all models
    - Spark_api_secret: Spark secret key
    - Wenxin_secret_key: Wenxin secret key
    - embeddings: Embedding model being used
    - embedding_key: Secret key for the embedding model being used (Zhipu or OpenAI)
    - template: Custom prompt template can be defined; if not provided, the default prompt template default_template_rq is used
    """

    # Default prompt template used to construct the prompt by combining the retrieved results with the query
    default_template_rq = """Use the following context to answer the final question. If you don't know the answer, say you don't know and do not try to make up an answer.
    Use at most three sentences. Keep the answer as concise as possible. Always say "Thank you for your question!" at the end of the answer.
    {context}
    Question: {question}
    Helpful answer:"""

    def __init__(self, model:str, temperature:float=0.0, top_k:int=4,  file_path:str=None, persist_path:str=None, appid:str=None, api_key:str=None, Spark_api_secret:str=None,Wenxin_secret_key:str=None, embedding = "openai",  embedding_key = None, template=default_template_rq):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.file_path = file_path
        self.persist_path = persist_path
        self.appid = appid
        self.api_key = api_key
        self.Spark_api_secret = Spark_api_secret
        self.Wenxin_secret_key = Wenxin_secret_key
        self.embedding = embedding
        self.embedding_key = embedding_key
        self.template = template
        self.llm = model_to_llm(self.model, self.temperature, self.appid, self.api_key, self.Spark_api_secret,self.Wenxin_secret_key)

        self.QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context","question"],
                                    template=self.template)
       
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm,
                                        retriever=self.retriever,
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt":self.QA_CHAIN_PROMPT})

    def answer(self, question:str=None, temperature = None, top_k = 4):
        """
        Core method, calls the question-answering chain
        arguments:
        - question: User's question
        """

        if len(question) == 0:
            return ""
        
        if temperature == None:
            temperature = self.temperature
            
        if top_k == None:
            top_k = self.top_k

        result = self.qa_chain({"query": question, "temperature": temperature, "top_k": top_k})
        answer = result["result"]
        answer = re.sub(r"\\n", '<br/>', answer)
        return answer   
