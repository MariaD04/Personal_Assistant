import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import WINES_DIR, REGIONS_DIR


def load_documents_from_folder(folder_path: str):
    """
    Загружает файлы из folder_path

    Args:
        folder_path (str): путь к папке с файлами

    Returns:
         documents (Array): массив загруженных документов
    """
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "source": file_path,
                                "title": os.path.splitext(filename)[0]
                            }
                        )
                    )
            except Exception as e:
                print(f"Ошибка при загрузке файла {filename}: {str(e)}")
    return documents

print("Загрузка документов...")
wine_docs = load_documents_from_folder(WINES_DIR)
region_docs = load_documents_from_folder(REGIONS_DIR)
all_docs = wine_docs + region_docs

print(f"Всего документов: {len(all_docs)}")
print(f"Из них вин: {len(wine_docs)}, регионов: {len(region_docs)}")

print("Разбиение документов на чанки...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(all_docs)
print(f"Всего чанков: {len(all_splits)}")

print("Создание эмбеддингов...")
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'},
)

vector_store = Chroma(
    collection_name="wine_knowledge_base",
    embedding_function=embeddings,
    persist_directory="./wine_knowledge_db",
)

print("Добавление документов")
ids = vector_store.add_documents(all_splits)
print(f"Всего добавлено векторов: {len(ids)}")
print("Готово! Векторная база успешно создана.")
