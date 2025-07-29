# my_ai_lib/prompt_builder.py

from typing import List, Dict, Any, Optional

class PromptBuilder:
    """
    Класс для сборки комплексного промпта для AI-модели Gemini.
    Объединяет различные блоки информации (системные определения,
    основные системные инструкции, дополнительные системные данные,
    историю чата) в единый, структурированный промпт.
    """

    def __init__(self):
        self._system_definition_content: List[str] = []
        self._main_system_content: List[str] = []
        self._additional_system_content: List[str] = []
        self._chat_history_content: List[str] = []
        self._tool_response_content: List[str] = [] # Для промежуточных ответов инструментов

    def add_system_definition(self, content: str):
        """
        Добавляет текст в блок 'SYSTEM_DEFINITION'.
        Этот блок содержит мета-инструкции и глобальные ограничения.
        """
        self._system_definition_content.append(content)

    def add_main_system_content(self, content: str):
        """
        Добавляет текст в блок 'MAIN_SYSTEM'.
        Этот блок определяет роль AI, общие правила поведения и базовую информацию о компании/агенте.
        """
        self._main_system_content.append(content)

    def add_additional_system_content(self, content: str):
        """
        Добавляет текст в блок 'ADDITIONAL_SYSTEM'.
        Этот блок включает доступные инструменты, схемы БД, базу знаний/FAQ,
        а также детализированные инструкции по поведению в разных сценариях.
        """
        self._additional_system_content.append(content)

    def add_chat_history_message(self, sender: str, message: str):
        """
        Добавляет сообщение в блок 'CHAT_HISTORY'.
        Форматирует сообщение как 'Sender: Message'.
        """
        # Убедимся, что отправитель всегда начинается с заглавной буквы
        formatted_sender = sender.capitalize()
        self._chat_history_content.append(f"{formatted_sender}: {message}")

    def add_tool_response(self, content: str):
        """
        Добавляет текст в блок 'TOOL_RESPONSE' для промежуточных вычислений.
        """
        self._tool_response_content.append(content)

    def build_prompt(self) -> str: # <--- УБРАН current_user_query из аргументов
        """
        Собирает все добавленные блоки в финальный промпт для AI-модели.
        Текущее сообщение пользователя и "AI:" будут добавлены в CHAT_HISTORY
        в ai_interactor перед вызовом этого метода.
        """
        sections: List[str] = []

        # 1. SYSTEM_DEFINITION BLOCK
        if self._system_definition_content:
            sections.append("---")
            sections.append("# SYSTEM_DEFINITION BLOCK")
            sections.extend(self._system_definition_content)

        # 2. MAIN_SYSTEM BLOCK
        if self._main_system_content:
            sections.append("---")
            sections.append("# MAIN_SYSTEM BLOCK")
            sections.extend(self._main_system_content)

        # 3. ADDITIONAL_SYSTEM BLOCK
        if self._additional_system_content:
            sections.append("---")
            sections.append("# ADDITIONAL_SYSTEM BLOCK")
            sections.extend(self._additional_system_content)

        # 4. CHAT_HISTORY BLOCK
        if self._chat_history_content:
            sections.append("---")
            sections.append("# CHAT_HISTORY BLOCK")
            sections.extend(self._chat_history_content)

        # 5. TOOL_RESPONSE BLOCK (для промежуточных вычислений/ответов инструментов)
        # Этот блок должен быть ДО текущего запроса пользователя, если он есть
        if self._tool_response_content:
            sections.append("---")
            sections.append("# TOOL_RESPONSE BLOCK")
            sections.extend(self._tool_response_content)
            # Инструкция для AI после получения ответа инструмента
            sections.append("\nBased on the above information, provide a concise answer or command.") 

        return "\n".join(sections)