# my_ai_lib_project/my_ai_lib/data_models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid

# Модель для одного элемента FAQ (вопрос-ответ)
class FAQEntry(BaseModel):
    question: str
    answer: str

# Модель для данных из KnowledgeBaseEntry
class KnowledgeBaseData(BaseModel):
    about_organisation: Optional[str] = None
    important_to_know: Optional[str] = None
    faq: Optional[str] = None # FAQ здесь остается строкой, т.к. парсится в views.py
    additional_data: Optional[Dict[str, Any]] = None

# Модель для полной информации об агенте/компании, как возвращает наш API
class AgentCompanyInfo(BaseModel):
    company_name: str
    mission: Optional[str] = None
    primary_services: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    contact_email: Optional[str] = None
    history: Optional[str] = None
    faq: List[FAQEntry] = Field(default_factory=list) # Список объектов FAQEntry
    agent_language: str
    agent_timezone: str
    agent_name: str
    role_in_organisation: Optional[str] = None
    
    knowledge_base: Optional[KnowledgeBaseData] = None 

# --- Новые Pydantic модели для схемы БД ---
    
class ColumnSchema(BaseModel):
    name: str = Field(description="The name of the database column.")
    type: str = Field(description="The SQL data type of the column (e.g., TEXT, INTEGER, REAL, BOOLEAN).")
    description: Optional[str] = Field(default=None, description="A brief description of the column's purpose or content.")
    is_pk: bool = Field(default=False, description="True if this column is a primary key.")
    is_fk: bool = Field(default=False, description="True if this column is a foreign key.")
    references_table: Optional[str] = Field(default=None, description="The table this foreign key references, if applicable.")
    references_column: Optional[str] = Field(default=None, description="The column this foreign key references, if applicable.")

class TableSchema(BaseModel):
    name: str = Field(description="The name of the database table.")
    description: Optional[str] = Field(default=None, description="A brief description of the table's purpose or content.")
    columns: List[ColumnSchema] = Field(description="A dictionary where keys are column names and values are ColumnSchema objects.")

class DatabaseSchema(BaseModel):
    database_name: str = Field(description="The logical name of the database (e.g., 'restaurant_db', 'ecommerce_analytics').")
    database_info: Optional[str] = Field(default=None, description="A general description of the database's content and purpose.")
    tables: List[TableSchema] = Field(description="A dictionary where keys are table names and values are TableSchema objects.")
    
    db_type: str = Field(description="Type of the database (e.g., 'sqlite', 'postgresql', 'mysql').")
    connection_string: str = Field(description="Connection string for the database.")
    
    forbidden_tables: Optional[List[str]] = Field(default=None, description="List of tables that the AI is explicitly forbidden from accessing.", examples=[["admin_users", "financial_data"]])
    forbidden_attributes: Optional[List[str]] = Field(default=None, description="List of table.column pairs that the AI is explicitly forbidden from accessing (e.g., 'users.password_hash').", examples=[["users.password_hash", "orders.customer_ip"]])

    
    # НОВОЕ: Метод для преобразования в формат, ожидаемый SQLValidator
    def to_validator_format(self) -> Dict[str, Any]:
        tables_dict_for_validator = {}

        # ИЗМЕНИТЕ ЭТУ СТРОКУ:
        for table_obj in self.tables: # Теперь итерируемся напрямую по объектам TableSchema
            table_name = table_obj.name # Получаем имя таблицы из самого объекта
            columns_dict_for_validator = {}

            # Аналогично для колонок, если columns в TableSchema тоже список:
            # Вам нужно будет проверить, как определено columns в TableSchema
            # Скорее всего, там тоже List[ColumnSchema], а не Dict
            for col_obj in table_obj.columns: # Итерируемся по списку ColumnSchema
                col_name = col_obj.name # Получаем имя колонки из объекта
                columns_dict_for_validator[col_name] = {
                    "type": col_obj.type,
                    "description": col_obj.description,
                    "is_pk": col_obj.is_pk,
                    "is_fk": col_obj.is_fk,
                    "references_table": col_obj.references_table,
                    "references_column": col_obj.references_column
                }
            tables_dict_for_validator[table_name] = {
                "description": table_obj.description,
                "columns": columns_dict_for_validator
            }

        return {
            "database_name": self.database_name,
            "database_info": self.database_info,
            "tables": tables_dict_for_validator,
            "forbidden_tables": self.forbidden_tables if self.forbidden_tables is not None else [],
            "forbidden_attributes": self.forbidden_attributes if self.forbidden_attributes is not None else []
        }



# 1. Модели для Wide Sales (структура "таблицы")
class WideSalesColumn(BaseModel):
    id: str
    column_name: str
    column_info: Optional[str] = None
    column_type: str
    is_primary_key: bool = False
    is_unique: bool = False
    is_nullable: bool = True
    is_deletable: bool = True
    is_editable: bool = True

class WideSalesTable(BaseModel):
    name: str
    info: Optional[str] = None
    columns: List[WideSalesColumn]
    # rows могут быть очень динамичными, поэтому проще оставить их как Dict[str, Any]
    # или более точно, List[Dict[str, Any]] если каждая строка - это словарь
    rows: List[Dict[str, Any]] # Список словарей, где ключи - имена колонок, значения - данные

# 2. Модели для Deep Sales (структура "узлов" и "связей")
class DeepSalesVariable(BaseModel):
    id: str
    name: str
    type: str
    is_dependent: bool = False
    description: Optional[str] = None

class DeepSalesNode(BaseModel):
    id: str
    type: str
    name: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[List[DeepSalesVariable]] = None # Только для dataMiningNode

class DeepSalesEdge(BaseModel):
    source: str
    target: str
    id: str
    type: str
    source_handle: str
    target_handle: str

# 3. Основная модель для схемы модели продаж
class SalesModelSchema(BaseModel):
    sales_id: uuid.UUID # Предполагаем, что ID - это UUID
    sales_name: str
    sales_info: Optional[str] = None
    sales_type: str = Field(description="Type of sales model: 'WIDE_SALES' or 'DEEP_SALES'")
    related_db: Optional[str] = None # Только для DEEP_SALES, может быть null для WIDE_SALES

    # Эти поля будут опциональными, так как зависят от sales_type
    wide_sales_table: Optional[WideSalesTable] = None
    deep_sales_nodes: Optional[List[DeepSalesNode]] = None
    deep_sales_edges: Optional[List[DeepSalesEdge]] = None

    # Метод для получения описания модели продаж для AI (аналог to_validator_format)
    def to_ai_instruction_format(self) -> Dict[str, Any]:
        """
        Преобразует SalesModelSchema в формат, удобный для передачи в AI в качестве инструмента.
        """
        output = {
            "sales_id": str(self.sales_id),
            "sales_name": self.sales_name,
            "sales_info": self.sales_info if self.sales_info else "No additional information.",
            "sales_type": self.sales_type,
        }

        if self.sales_type == 'WIDE_SALES' and self.wide_sales_table:
            table_data = {
                "name": self.wide_sales_table.name,
                "info": self.wide_sales_table.info if self.wide_sales_table.info else "No info.",
                "columns": [col.model_dump() for col in self.wide_sales_table.columns], # Используем model_dump() для Pydantic v2
                "rows": self.wide_sales_table.rows
            }
            output["wide_sales_data"] = table_data
        elif self.sales_type == 'DEEP_SALES':
            output["related_db"] = self.related_db if self.related_db else "No related database specified."
            
            nodes_for_ai = []
            if self.deep_sales_nodes:
                for node in self.deep_sales_nodes:
                    node_info = {
                        "id": node.id,
                        "type": node.type,
                        "name": node.name if node.name else node.type,
                        "description": node.description if node.description else "No description.",
                    }
                    if node.variables:
                        node_info["variables"] = [var.model_dump() for var in node.variables]
                    nodes_for_ai.append(node_info)
            output["deep_sales_nodes"] = nodes_for_ai

            edges_for_ai = []
            if self.deep_sales_edges:
                for edge in self.deep_sales_edges:
                    edges_for_ai.append(edge.model_dump())
            output["deep_sales_edges"] = edges_for_ai
        
        return output
