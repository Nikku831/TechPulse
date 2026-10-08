from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import sys
sys.path.append('/Users/lta/Desktop/llm-universe/project')
from qa_chain.model_to_llm import model_to_llm
import re

class Chat_QA_chain_self:
    """
    Question-answering chain with history
    - model: Name of the model being called
    - temperature: Temperature coefficient, controls the randomness of generation
    - top_k: Returns the top k similar documents from retrieval
    - chat_history: History records, input as a list, defaults to an empty list
    - history_len: Controls the number of recent conversations to retain
    - file_path: Path where the files for building the database are located
    - persist_path: Persistence path of the vector database
    - appid: Spark
    - api_key: Parameter that needs to be passed for Spark, Baidu Wenxin, OpenAI, and Zhipu
    - Spark_api_secret: Spark secret key
    - Wenxin_secret_key: Wenxin secret key
    - embeddings: Embedding model being used
    - embedding_key: Secret key for the embedding model being used (Zhipu or OpenAI)
    """
    def __init__(self,model:str, temperature:float=0.0, top_k:int=4, chat_history:list=[], file_path:str=None, persist_path:str=None, appid:str=None, api_key:str=None, Spark_api_secret:str=None,Wenxin_secret_key:str=None, embedding = "openai",embedding_key:str=None):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.chat_history = chat_history
        #self.history_len = history_len
        self.file_path = file_path
        self.persist_path = persist_path
        self.appid = appid
        self.api_key = api_key
        self.Spark_api_secret = Spark_api_secret
        self.Wenxin_secret_key = Wenxin_secret_key
        self.embedding = embedding
        self.embedding_key = embedding_key



        
    
    def clear_history(self):
        "Clear History"
        return self.chat_history.clear()

    
    def change_history_length(self,history_len:int=1):
        """
        Save the history records of the specified number of conversation turns
        Input parameters:
        - history_len: Controls the number of the most recent history_len conversation turns to retain
        - chat_history: Current conversation history
        Output: Returns the most recent history_len conversation turns
        """
        n = len(self.chat_history)
        return self.chat_history[n-history_len:]

 
    def answer(self, question:str=None,temperature = None, top_k = 4):
        """
        Core method, calls the question-answering chain
        arguments:
        - question: User's question
        """
        
        if len(question) == 0:
            return "", self.chat_history
        
        if len(question) == 0:
            return ""
        
        if temperature == None:
            temperature = self.temperature
        llm = model_to_llm(self.model, temperature, self.appid, self.api_key, self.Spark_api_secret,self.Wenxin_secret_key)

        #self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


        qa = ConversationalRetrievalChain.from_llm(
            llm = llm,
            
        )
        
        #print(self.llm)
        result = qa({"question": question,"chat_history": self.chat_history})       #result里有question、chat_history、answer
        answer =  result['answer']
        answer = re.sub(r"\\n", '<br/>', answer)
        self.chat_history.append((question,answer))

        return self.chat_history  
        
















