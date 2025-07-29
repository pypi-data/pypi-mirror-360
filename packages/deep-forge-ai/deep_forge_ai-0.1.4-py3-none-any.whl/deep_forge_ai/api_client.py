# my_ai_lib_project/my_ai_lib/api_client.py

import requests
import json
from .data_models import AgentCompanyInfo, DatabaseSchema, SalesModelSchema
from typing import List, Optional, Dict

class DeepForgeAPIClient:
    def __init__(self, base_url: str, api_key: str = None):
        """
        Инициализирует клиент для взаимодействия с DeepForge Server.

        Args:
            base_url: Базовый URL вашего DeepForge Server (например, "http://localhost:8000/api/v2/").
            api_key: Ключ агента (UUID) для аутентификации. Будет отправлен в заголовке Authorization: Bearer <api_key>.
        """
        self.base_url = base_url.rstrip('/') + '/' # Убедимся, что URL заканчивается слэшем
        self.headers = {}
        if api_key:
            # Заголовок Authorization для ключа агента
            self.headers['Authorization'] = f'Bearer {api_key}'
        
        self.timeout = 10 # 10 секунд для всех запросов

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Внутренний метод для выполнения HTTP-запросов и обработки общих ошибок.
        """
        url = self.base_url + endpoint
        
        try:
            response = requests.request(method, url, headers=self.headers, timeout=self.timeout, **kwargs)
            response.raise_for_status() # Вызывает исключение для HTTP ошибок 4xx/5xx
            
            return response.json()
        
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Таймаут подключения к DeepForge Server ({url}). Сервер не отвечает.") from None
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Не удалось подключиться к DeepForge Server ({url}). Убедитесь, что сервер запущен и доступен.") from None
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', 'N/A')
            response_text = getattr(e.response, 'text', '')
            raise RuntimeError(f"Ошибка запроса к DeepForge Server ({url}). Статус: {status_code}. Ответ: {response_text[:200]}...") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Сервер DeepForge вернул невалидный JSON ответ: {e}. Ответ: {response.text[:200]}...") from e
        except Exception as e:
            raise RuntimeError(f"Неожиданная ошибка при взаимодействии с DeepForge Server ({url}): {e}") from e

    def get_agent_info(self) -> AgentCompanyInfo: # <--- ИЗМЕНИЛИ ТИП ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ
        """
        Получает информацию об агенте с DeepForge Server и возвращает ее как объект Pydantic.

        Returns:
            Объект AgentCompanyInfo.
        Raises:
            ConnectionError: Проблемы с подключением или таймаут.
            RuntimeError: Общая ошибка HTTP-запроса или неожиданная ошибка.
            ValueError: Проблемы с парсингом или валидацией JSON/Pydantic.
        """
        endpoint = "agent/info/" 

        # Получаем сырой словарь от сервера
        raw_agent_info_data = self._make_request("GET", endpoint)

        # Теперь используем Pydantic для валидации и создания объекта
        try:
            # Pydantic автоматически проверит структуру и типы
            agent_company_info = AgentCompanyInfo(**raw_agent_info_data)
            return agent_company_info
        except Exception as e:
            raise ValueError(f"Ошибка при валидации данных Agent Info с помощью Pydantic: {e}. Сырые данные: {raw_agent_info_data}") from e
    
    def get_db_schemas(self) -> List[DatabaseSchema]:
        """
        Получает структурированные схемы баз данных, связанные с агентом.
        """
        # Эндпоинт, который мы согласовали: /api/v2/agent/db_schemas/
        endpoint = "agent/db_schemas/" 
        
        # Ожидаем список объектов JSON, каждый из которых представляет схему БД
        data_list = self._make_request("GET", endpoint)
        
        # Парсим каждый элемент списка в Pydantic модель DatabaseSchema
        schemas = [DatabaseSchema(**item) for item in data_list]
        return schemas
    
    def get_sales_models(self) -> List[SalesModelSchema]:
        """
        Получает структурированные схемы моделей продаж, связанные с агентом.
        """
        # Эндпоинт, который мы согласовали
        endpoint = "agent/sales-models/" 
        
        # Ожидаем список объектов JSON, каждый из которых представляет схему модели продаж
        data_list = self._make_request("GET", endpoint)
        
        # Убедимся, что data_list действительно список
        if not isinstance(data_list, list):
            raise ValueError(f"Ожидался список схем моделей продаж, получен {type(data_list).__name__}.")

        # Парсим каждый элемент списка в Pydantic модель SalesModelSchema
        try:
            sales_schemas = [SalesModelSchema(**item) for item in data_list]
            return sales_schemas
        except Exception as e:
            # Выводим первые несколько элементов для отладки, если список большой
            sample_data = data_list[:2] if data_list else '[]'
            raise ValueError(f"Ошибка при валидации данных схемы моделей продаж с помощью Pydantic: {e}. Сырые данные: {sample_data}") from e

#     def get_wide_sales_intents(self) -> Dict[str, str]:
#         """
#         Извлекает WIDE_SALES модели из DeepForge Server.
#         Формирует:
#         1. WIDE_SALES_PACK_MAP: Табличное представление всех данных.
#         2. Отдельные SELLING_INTENT для каждого элемента, с JSON-ответом,
#            содержащим только 'id', 'name', 'price', 'description'.
#         """
#         generated_prompts_parts = {}
#         sales_models = self.get_sales_models()

#         for sales_model in sales_models:
#             if sales_model.sales_type == 'WIDE_SALES' and sales_model.wide_sales_table:
#                 # Создаем маппинги "col-ID" <-> "column_name" для удобного доступа
#                 column_map_id_to_name = {col.id: col.column_name for col in sales_model.wide_sales_table.columns}
#                 column_map_name_to_id = {col.column_name: col.id for col in sales_model.wide_sales_table.columns}

#                 sales_model_base_name = sales_model.sales_name.replace(" ", "_").replace("-", "_").upper()
#                 sales_model_id_short = str(sales_model.sales_id)[:4].upper()

#                 # --- 1. Формируем WIDE_SALES_PACK_MAP (табличные данные) ---
#                 map_content_lines = []
                
#                 # Заголовок таблицы с читаемыми именами колонок
#                 header_cols = []
#                 # Собираем колонки, которые хотим видеть в таблице (все, кроме внутренних row-id)
#                 relevant_columns = [col for col in sales_model.wide_sales_table.columns if not col.id.startswith('row-')]
                
#                 for col in relevant_columns:
#                     header_cols.append(f"{col.column_name} ({col.column_type})")
                
#                 if header_cols:
#                     map_content_lines.append(f"| {' | '.join(header_cols)} |")
#                     map_content_lines.append(f"| {' | '.join(['---'] * len(header_cols))} |")

#                 # Добавляем каждую строку данных в табличном формате
#                 for i, item_row in enumerate(sales_model.wide_sales_table.rows):
#                     row_values = []
#                     for col_schema in relevant_columns: # Итерируем по отфильтрованным колонкам
#                         col_id_in_row = col_schema.id 
#                         value = item_row.get(col_id_in_row, "N/A")
                        
#                         # Ограничиваем длину строковых значений для краткости в промпте
#                         if isinstance(value, str) and len(value) > 70: # Увеличил лимит для описаний
#                             value = value[:67] + "..."
#                         row_values.append(str(value))
                    
#                     if row_values:
#                         map_content_lines.append(f"| {' | '.join(row_values)} |")

#                 map_section_text = "\n".join(map_content_lines)
#                 if not map_section_text:
#                     map_section_text = "No detailed item data available in this table."

#                 wide_sales_pack_map_name = f"WIDE_SALES_PACK_MAP_{sales_model_base_name}_{sales_model_id_short}"
#                 generated_prompts_parts[wide_sales_pack_map_name] = f"""
# ### {wide_sales_pack_map_name} (TOOL_STATUS: UNIVERSAL; SELLING_TYPE: WIDE_SALES_DATA_REFERENCE)
# Description: This table provides a comprehensive overview of all available items within the '{sales_model.sales_name}' sales model (Sales ID: {sales_model.sales_id}).
# It includes all attributes and their current values for each item. Use this data for reference when answering user questions or when preparing to use a SELLING_INTENT.

# --- Available Data Table ---

# {map_section_text}
# """
                
#                 # --- 2. Формируем отдельные SELLING_INTENT для каждого элемента ---
#                 for item_row in sales_model.wide_sales_table.rows:
#                     # Извлекаем обязательные поля для JSON-ответа
#                     product_id = item_row.get(column_map_name_to_id.get('id', ''), 'N/A')
#                     product_name = item_row.get(column_map_name_to_id.get('name', ''), 'N/A')
#                     product_price = item_row.get(column_map_name_to_id.get('price', ''), 'N/A')
#                     product_description = item_row.get(column_map_name_to_id.get('description', ''), 'N/A')

#                     # Генерируем уникальное имя интента для каждого айтема
#                     # Используем sales_name + имя айтема + ID айтема
#                     item_id_suffix_for_intent_name = str(product_id).replace("-", "").upper()
#                     item_name_cleaned = str(product_name).replace(" ", "_").replace("-", "_").replace("\"", "").upper()
                    
#                     # Для имени интента лучше использовать более короткий ID
#                     if isinstance(item_id_suffix_for_intent_name, str) and len(item_id_suffix_for_intent_name) > 8:
#                         item_id_suffix_for_intent_name = item_id_suffix_for_intent_name[-8:] # последние 8 символов ID

#                     intent_name = f"SELLING_INTENT_{sales_model_base_name}_{item_name_cleaned}_{item_id_suffix_for_intent_name}_{sales_model_id_short}"
#                     # Если имя все еще слишком длинное, усекаем его
#                     if len(intent_name) > 80: # Ограничение для имен инструментов Gemini
#                         intent_name = f"SELLING_INTENT_{item_name_cleaned}_{item_id_suffix_for_intent_name}"
#                         if len(intent_name) > 80:
#                             intent_name = f"SELLING_INTENT_{item_name_cleaned[:30]}_{item_id_suffix_for_intent_name}"


#                     # Формируем описание интента для промпта ИИ
#                     # Убираем блок "Information (Attributes & Sample Values for this item):"
#                     # и инструкции про SELECT_FUNCTION
#                     intent_description = f"""
# ### {intent_name} (TOOL_STATUS: UNIVERSAL; SELLING_TYPE: WIDE_SALES)
# Description: This tool is used to finalize the sale of **{product_name}** from the '{sales_model.sales_name}' sales model (Sales ID: {sales_model.sales_id}).
# This specific intent should be used when the user clearly expresses a desire to purchase this particular item.

# * **When to use:** When the user explicitly states their intent to buy **{product_name}**.

# * **How to use:** Respond with a JSON object to indicate the sale.
#     ```json
#     {{"is_sale": "true", "sales_type": "{sales_model.sales_type}", "name": {json.dumps(product_name)}, "price": {json.dumps(product_price)}, "description": {json.dumps(product_description)}, "sales_id": "{sales_model.sales_id}", "item_id": {json.dumps(product_id)}}}
#     ```
# """
#                     generated_prompts_parts[intent_name] = intent_description

#         return generated_prompts_parts


    def get_wide_sales_intents(self) -> Dict[str, str]:
        """
        Извлекает WIDE_SALES модели из DeepForge Server и преобразует каждую строку
        в wide_sales_table.rows в отдельный selling intent для динамического
        добавления в промпт ИИ.
        Включает все атрибуты из wide_sales_table.columns и расширяет JSON-ответ,
        используя сопоставление по 'col-id' для извлечения значений.

        Returns:
            Словарь, где ключ - это имя Selling Intent (например, SELLING_INTENT_CHEESEBURGER),
            а значение - строка с описанием инструмента для промпта ИИ.
        """
        wide_sales_intents_text = {}
        sales_models = self.get_sales_models()

        for sales_model in sales_models:
            if sales_model.sales_type == 'WIDE_SALES' and sales_model.wide_sales_table:
                # Создаем маппинг "col-ID" -> "column_name" и "column_info" для удобного доступа
                column_map = {col.id: col for col in sales_model.wide_sales_table.columns}
                column_name_to_id_map = {col.column_name: col.id for col in sales_model.wide_sales_table.columns}

                # Итерируем по каждой строке данных, каждая строка - это отдельный "продажный" айтем
                for item_row in sales_model.wide_sales_table.rows:
                    # Извлекаем основные поля для JSON-ответа
                    # Используем col-ID для доступа к данным в item_row
                    # и column_name_to_id_map для получения col-ID по column_name
                    product_name = item_row.get(column_name_to_id_map.get('name', ''), 'N/A')
                    product_price = item_row.get(column_name_to_id_map.get('price', ''), 'N/A')
                    product_description = item_row.get(column_name_to_id_map.get('description', ''), 'N/A')

                    # Генерируем уникальное имя интента для каждого айтема
                    # Используем sales_name (например, "menu_items") + имя айтема + ID айтема
                    item_id_suffix = item_row.get(column_name_to_id_map.get('id', ''), 'N/A')
                    intent_name_base = sales_model.sales_name.replace(" ", "_").replace("-", "_").upper()
                    item_name_cleaned = str(product_name).replace(" ", "_").replace("-", "_").replace("\"", "").upper()
                    
                    # Обеспечиваем, что item_id_suffix будет валидной частью имени, если он UUID-подобный
                    if isinstance(item_id_suffix, str) and len(item_id_suffix) > 4:
                        item_id_suffix = item_id_suffix[-4:].upper()
                    else:
                        item_id_suffix = str(item_id_suffix).upper() # Преобразуем в строку на всякий случай

                    # Добавляем ID продажи, чтобы избежать коллизий между разными "WIDE_SALES" таблицами
                    sales_model_id_suffix = str(sales_model.sales_id)[:4].upper()
                    intent_name = f"SELLING_INTENT_{intent_name_base}_{item_name_cleaned}_{item_id_suffix}_{sales_model_id_suffix}"
                    # Если имя слишком длинное, можно усечь его или использовать только sales_id + item_id
                    if len(intent_name) > 60: # Примерное ограничение на длину имени
                         intent_name = f"SELLING_INTENT_{item_name_cleaned}_{item_id_suffix}_{sales_model_id_suffix}"


                    # --- Формируем секцию "Information" динамически для текущего айтема ---
                    information_lines = []
                    for col_id_in_row, col_value in item_row.items():
                        # Пропускаем внутренний ID строки
                        if col_id_in_row == 'id' and 'row-' in col_value:
                            continue
                        
                        column_schema = column_map.get(col_id_in_row)
                        if column_schema:
                            col_name_readable = column_schema.column_name
                            col_info = column_schema.column_info if column_schema.column_info else "No info."
                            col_type = column_schema.column_type
                            information_lines.append(f"    - **{col_name_readable}**: {json.dumps(col_value)} (Type: {col_type}, Info: {col_info})")
                        else:
                            # Если col_id_in_row не найден в схеме колонок (например, это внутренний ID строки)
                            # или если схема колонки почему-то отсутствует (что не должно быть при валидных данных)
                            if not col_id_in_row.startswith('row-'): # Игнорируем специфичные row-id, если они попадаются как ключи
                                information_lines.append(f"    - **{col_id_in_row}**: {json.dumps(col_value)} (Unknown Type/Info)")


                    information_section = "\n".join(information_lines)
                    if not information_section:
                        information_section = "    No specific item attributes found for this item."

                    # Формируем описание интента для промпта ИИ
                    intent_description = f"""
### {intent_name} (TOOL_STATUS: UNIVERSAL; SELLING_TYPE: WIDE_SALES)

* **When to use:** When the user is **confirming a purchase** or giving a **clear command to buy** **{product_name}**. This tool should **only** be used when the user's intent to buy is explicit and confirmed, not when they are simply asking for information about the item's availability or details.

* **Information (Attributes & Sample Values for this item):**
{information_section}

* **How to use:** Respond with a JSON object to indicate the sale:
    ```json
    {{"is_sale": "true", "sales_type": "{sales_model.sales_type}", "name": "{product_name}", "price": {json.dumps(product_price)}, "description": {json.dumps(product_description)}, "sales_id": "{sales_model.sales_id}", "item_id": {json.dumps(item_id_suffix)}}}
    ```
"""
                    wide_sales_intents_text[intent_name] = intent_description

        return wide_sales_intents_text


# --- Пример использования (для тестирования модуля отдельно) ---
if __name__ == "__main__":
    DEEPFORGE_BASE_URL = "#" 
    YOUR_AGENT_API_KEY = "#" # Замените на ваш ключ

    if YOUR_AGENT_API_KEY == "ВАШ_РЕАЛЬНЫЙ_КЛЮЧ_АГЕНТА_ИЗ_БД_DEEPFORGE":
        print("ПОЖАЛУЙСТА, ЗАМЕНИТЕ 'YOUR_AGENT_API_KEY' НА РЕАЛЬНЫЙ КЛЮЧ ИЗ ВАШЕЙ БАЗЫ ДАННЫХ DEEPFORGE!")
    else:
        print(f"Попытка получить Agent Info и Sales Models с {DEEPFORGE_BASE_URL} для агента с ключом: {YOUR_AGENT_API_KEY[:8]}...")

        client = DeepForgeAPIClient(base_url=DEEPFORGE_BASE_URL, api_key=YOUR_AGENT_API_KEY)

        try:
            agent_info: AgentCompanyInfo = client.get_agent_info()
            print("\nУспешно получена информация об агенте.")
            print(f"Название компании: {agent_info.company_name}")

            print("\nПолучение схем моделей продаж...")
            sales_models_schemas: List[SalesModelSchema] = client.get_sales_models()

            if sales_models_schemas:
                print(f"Успешно получено {len(sales_models_schemas)} схем моделей продаж:")
                for sales_schema in sales_models_schemas:
                    print(f"\n  - Sales Model Name: {sales_schema.sales_name}")
                    print(f"    Type: {sales_schema.sales_type}")
                    print(f"    Info: {sales_schema.sales_info}")
                    if sales_schema.sales_type == 'WIDE_SALES' and sales_schema.wide_sales_table:
                        print(f"    Wide Sales Table: {sales_schema.wide_sales_table.name}")
                        print(f"      Columns: {[c.column_name for c in sales_schema.wide_sales_table.columns]}")
                        print(f"      Rows Count: {len(sales_schema.wide_sales_table.rows)}")
                        # Вывести первые 2 строки для примера
                        if sales_schema.wide_sales_table.rows:
                            print(f"      Sample Row: {sales_schema.wide_sales_table.rows[0]}")
                    elif sales_schema.sales_type == 'DEEP_SALES':
                        print(f"    Related DB: {sales_schema.related_db}")
                        print(f"    Deep Sales Nodes Count: {len(sales_schema.deep_sales_nodes) if sales_schema.deep_sales_nodes else 0}")
                        print(f"    Deep Sales Edges Count: {len(sales_schema.deep_sales_edges) if sales_schema.deep_sales_edges else 0}")
                        if sales_schema.deep_sales_nodes:
                            print(f"      Sample Deep Node (ID: {sales_schema.deep_sales_nodes[0].id}, Type: {sales_schema.deep_sales_nodes[0].type})")
                        if sales_schema.deep_sales_edges:
                            print(f"      Sample Deep Edge (Source: {sales_schema.deep_sales_edges[0].source}, Target: {sales_schema.deep_sales_edges[0].target})")

            else:
                print("Схемы моделей продаж для данного агента не найдены.")

        except (ConnectionError, RuntimeError, ValueError) as e:
            print(f"\nОШИБКА: {e}")
            print("Убедитесь, что:")
            print("1. DeepForge Server запущен.")
            print(f"2. URL '{DEEPFORGE_BASE_URL}agent/sales-models/' корректен.")
            print(f"3. Ключ агента '{YOUR_AGENT_API_KEY}' верен и агент/аккаунт активны.")
            print("4. Эндпоинт возвращает валидный JSON.")
            print("5. Структура возвращаемого JSON соответствует Pydantic моделям в data_models.py.")
        except Exception as e:
            print(f"\nНЕОЖИДАННАЯ ОШИБКА: {e}")