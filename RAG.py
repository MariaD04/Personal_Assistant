import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from DeepSeekR1 import DeepSeekAPI

load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'},  
)

vector_store = Chroma(
    collection_name="wine_knowledge_db",
    embedding_function=embeddings,
    persist_directory="./wine_knowledge_db",
)

prompt_template = ChatPromptTemplate.from_template("""
    Ты - опытный сомелье, в задачу которого входит отвечать на вопросы пользователя про вина
    и рекомендовать лучшие вина к еде. Посмотри на всю имеющуюся в твоем распоряжении информацию
    и выдай одну или несколько лучших рекомендаций. Если что-то непонятно, то лучше уточни информацию
    у пользователя. Если ты не знаешь ответ, то просто скажи "Не знаю".

    Context: {context}

    Question: {question}

    Answer in detail:""")

llm = DeepSeekAPI(api_key=os.environ["DEEP_API_TOKEN"])

def ask_question(question):
    """
    Функция для генерации ответа на вопрос с системой RAG

    Args:
        question (str): входной вопрос пользователя

    Returns:
        str: ответ модели
    """

    retrieved_docs = vector_store.similarity_search(question, k=3)
    docs_content = "\n".join([doc.page_content for doc in retrieved_docs])

    formatted_prompt = prompt_template.format(question=question, context=docs_content)

    response = llm.ask(formatted_prompt)
    return response
