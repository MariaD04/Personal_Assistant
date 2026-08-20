import requests

class DeepSeekAPI:
    """
    Класс, реализующий подключение и запросы к сервису DeepSeek
    """
    def __init__(self, api_key: str):
        """
        Инициализирует объект подключения к DeepSeek

        Args:
            api_key (str):  API-ключ подключения к сервису

        Returns:
            None
        """
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "deepseek/deepseek-r1:free"

    def ask(self, text):
        """
        Реализует обычный запрос к DeepSeek

        Args:
            text (str): входной промпт для модели DeepSeek

        Returns:
             str: ответ модели
        """
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(self.api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            else:
                return "No response from model"
        else:
            return f"Error {response.status_code}: {response.text}"

    def classify(self, text):
        """
        Реализует запрос к DeepSeek для классификации сообщения

        Args:
            text (str): входной текст пользователя

        Returns:
            str: ответ модели
        """
        prompt = (
            f"Проанализируй следующий текст и классифицируй его по одной из меток: заявка, вопрос или спам.\n"
            f"ВАЖНО, что эти сообщения адресуются конкретной компании и нерелевантные сообщения должны уходить "
            f"в спам\n"
            f"К вопросам должны относиться только те сообщения, где пользователь хочет что-то узнать по тематике "
            f"компании\n"
            f"К заявкам относятся сообщения, где видно, что пользователь хочет что-то купить, как-то проинвестировать "
            f"или принести иную прбыль компании\n"
            f"Текст:\n\"\"\"\n{text}\n\"\"\"\n"
            "Ответь только одним словом — одной меткой, без пояснений и дополнительного текста."
        )

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                # Уберём лишние пробелы и перейдём на нижний регистр (по необходимости)
                label = choices[0].get("message", {}).get("content", "").strip()
                return label
            else:
                return "Нет ответа от модели"
        else:
            return f"Ошибка {response.status_code}: {response.text}"

    def collect_info(self, text):
        """
        Реализует запрос к DeepSeek для извлечения информации из сообщения

        Args:
            text (str): входной текст пользователя

        Returns:
            str: ответ модели
        """
        prompt = (
            f"Следующий текст является заявкой, которая потенциально должна принести компании прибыль\n"
            f"Проанализируй текст и пойми какие данные из списка присутствуют в тексте\n"
            f"Список: ФИО, продукт или товар, который автор сообщения хочет приобрести, контактные данные\n"
            f"Текст:\n\"\"\"\n{text}\n\"\"\"\n"
            f"Ответь JSON в формате {{\"contact_info\": контактные данные, \"fio\": фио клиента, "
            f"\"product\": продукт, который хотят приобрести}}."
            f"Никакий других данных в ответе быть не должно, только JSON, который можно распарсить\n"
            f"Если каких-то данных нет в тексте, то на их месте пришли None\n"
            f"Дополнительно проверь данные на валидность, чтобы номер соответствовал реальному номеру, "
            f"ФИО было адекватным и не придуманным, данные о продукте заноси в именительном падеже "
            f"с указанием количества, если оно присутствует"
        )

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                label = choices[0].get("message", {}).get("content", "").strip()
                return label
            else:
                return "Нет ответа от модели"
        else:
            return f"Ошибка {response.status_code}: {response.text}"