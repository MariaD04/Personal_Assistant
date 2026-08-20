import os
import json
import re

from aiogram import types
from typing import List, Dict, Any
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from DeepSeekR1 import DeepSeekAPI
from RAG import ask_question
from config import *
from database import UserMessagesDB


load_dotenv()

llm = DeepSeekAPI(os.environ["DEEP_API_TOKEN"])


def clean_json_string(raw_str: str) -> str:
    """
    Преобразует строку определенного формата в строку, содержащую чистый JSON

    Args:
        raw_str (str): строку формата:
        ```json
        {...}
        ```
    Returns:
        str: строку, содержащую чистый JSON внутри.
    """
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, raw_str, re.DOTALL | re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
        print(f"[clean_json_string] Удалена обёртка. Результат:\n{cleaned}")
        return cleaned
    else:
        print("[clean_json_string] Обёртка не найдена, возвращаем строку как есть.")
        return raw_str.strip()


class GraphState(TypedDict):
    """
    Определение структуры состояния графа

    Attributes:
        user (Message): объект сообщения принимаемый на входе телеграмм-ботом
        message (str): текст сообщения
        response (str): сообщение для обратной связи пользователю
        status (str): текущий статус обработки сообщения
        next_node (str): узел выполнения, следующий за текущим
        collected_info (Dict[str, Any]): список информации из сообщения пользователя для созранения в базу данных
    """
    user: types.Message
    message: str
    response: str
    status: str
    next_node: str
    collected_info: Dict[str, Any]


def classify_message(state: GraphState) -> Dict[str, Any]:
    """
    Классификация входящего сообщения

    Args:
        state (GraphState): текущее состояние графа

    Returns:
        Dict: словарь обновленного состояния графа

    """
    message = state["message"]
    response = llm.classify(text=message).lower()

    if "спам" in response:
        print("Сообщение определено как спам")
        return {"status": "spam", "next_node": "END", "response": "Пожалуйста, не присылайте бессмысленные сообщения"}
    elif "заявка" in response:
        print("Сообщение определено как заявка")
        return {"status": "application", "next_node": "collect_info"}
    else:
        print("Сообщение определено как вопрос")
        return {"status": "question", "next_node": "retrieve"}


def retrieve(state: GraphState) -> Dict[str, Any]:
    """
    Поиск информации по вопросу

    Args:
        state (GraphState): текущее состояние графа

    Returns:
        Dict: словарь обновленного состояния графа"""

    text = state["message"]
    response = ask_question(text)
    return {
        "next_node": END,
        "response": response
    }

def collect_info(state: GraphState) -> Dict[str, Any]:
    """
    Собирает контактную информацию из сообщения пользователя

    Args:
        state (GraphState): текущее состояние графа

    Returns:
        Dict: словарь обновленного состояния графа
    """
    print("collect_info")
    collected_json_str = llm.collect_info(state["message"])
    print(f"collected_json_str (repr): {repr(collected_json_str)}")

    cleaned_json = clean_json_string(collected_json_str)
    print(f"Очищенный JSON-стринг:\n{cleaned_json}")

    try:
        collected_data = json.loads(cleaned_json)
        print(f"Распарсенные данные: {collected_data}")
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
        collected_data = {}

    return {
        "response": f"Благодарим за обращение, в ближайшее время с вами свяжутся!",
        "next_node": "save_to_db",
        "collected_info": collected_data
    }


async def save_to_db(state: GraphState) -> Dict[str, Any]:
    """
    Сохраняет информацию в базу данных

    Args:
        state (GraphState): текущее состояние графа

    Returns:
        Dict: словарь обновленного состояния графа
    """
    print("save_to_db")
    db = UserMessagesDB(DSN)
    await db.connect()
    await db.create_table()

    contact_info = state.get("collected_info", {}).get("contact_info")
    fio = state.get("collected_info", {}).get("fio")
    product = state.get("collected_info", {}).get("product")
    await db.save_message(state["user"], contact_info, fio, product)

    return {
        "status": "completed",
        "next_node": END
    }


workflow = StateGraph(GraphState)

workflow.add_node("classify", classify_message)
workflow.add_node("retrieve", retrieve)
workflow.add_node("collect_info", collect_info)
workflow.add_node("save_to_db", save_to_db)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    lambda state: state["next_node"],
    {
        "retrieve": "retrieve",
        "collect_info": "collect_info",
        "END": END
    }
)

workflow.add_edge("retrieve", END)
workflow.add_edge("collect_info", "save_to_db")
workflow.add_edge("save_to_db", END)

graph = workflow.compile()

graph_image = graph.get_graph().draw_mermaid_png()
with open("../graph_image.png", "wb") as png:
    png.write(graph_image)

async def run_agent(message: types.Message) -> str:
    """
    Асинхронный запуск агента для обработки сообщения

    Args:
        message (Message): объект сообщения от пользователя

    Returns:
        last_response (str): Ответ пользователю
    """
    inputs = {"user": message, "message": message.text}
    last_response = "Не удалось обработать запрос."

    try:
        async for output in graph.astream(inputs):
            if output:
                last_node = list(output.keys())[0]
                last_response = output[last_node].get("response", last_response)

        return last_response

    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return "Произошла ошибка при обработке запроса"