# my_ai_lib/sql_validator.py

import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function, Token, Parenthesis, Comparison, Statement
from sqlparse.tokens import Keyword, Whitespace, DML, Wildcard, Number
from typing import Dict, Any, List




class SQLValidationException(Exception):
    """Кастомное исключение для ошибок валидации SQL."""
    pass

class SQLValidator:
    def __init__(self, db_schema: Dict[str, Any], max_limit: int = 30):
        """
        Инициализирует валидатор SQL, адаптированный под ваш формат db_schema.

        :param db_schema: Словарь со схемой БД. Ожидается, что он будет в формате,
                          содержащем 'database_name', 'tables', 'forbidden_tables' и 'forbidden_attributes'.
                          Пример: {"database_name": "restaurant_db", "tables": {...}, "forbidden_tables": [...], "forbidden_attributes": [...]}
        :param max_limit: Максимальное допустимое значение для LIMIT.
        """
        self.db_schema = db_schema
        self.max_limit = max_limit

        self.allowed_tables_and_columns: Dict[str, List[str]] = {}
        
        forbidden_tables_lower = {f.lower() for f in db_schema.get("forbidden_tables", [])}
        forbidden_attributes_lower = {f.lower() for f in db_schema.get("forbidden_attributes", [])}

        tables_data = db_schema.get("tables", {})
        
        for table_name, table_info in tables_data.items():
            table_name_lower = table_name.lower()
            
            if table_name_lower in forbidden_tables_lower:
                continue 

            allowed_cols_for_table = []
            columns_data = table_info.get("columns", {}) 
            
            for col_name, col_info in columns_data.items(): 
                col_name_lower = col_name.lower()
                full_attr_name = f"{table_name_lower}.{col_name_lower}"

                if full_attr_name not in forbidden_attributes_lower:
                    allowed_cols_for_table.append(col_name_lower)
            
            if allowed_cols_for_table:
                self.allowed_tables_and_columns[table_name_lower] = allowed_cols_for_table

        self.forbidden_keywords = {
            'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'MERGE',
            'CREATE', 'ALTER', 'DROP', 'RENAME',
            'GRANT', 'REVOKE',
            'COMMIT', 'ROLLBACK', 'SAVEPOINT',
            'UNION', 'UNION ALL',
            'WITH RECURSIVE',
            'EXEC', 'EXECUTE', 'CALL',
            'OFFSET',
            'CROSS JOIN', # Добавлено явно, хотя sqlparse может его токенизировать иначе
        }

        self.forbidden_functions = {
            'LOAD_FILE', 'PG_READ_FILE', 'OUTFILE',
            'PG_SLEEP', 'BENCHMARK',
            'CURRENT_USER', 'VERSION', 'DATABASE_NAME', 'USER', 'SCHEMA', 'CONNECTION_ID',
            'RAND', 'UUID'
        }

        self.forbidden_system_tables = {
            'INFORMATION_SCHEMA', 'PG_CATALOG', 'MYSQL.USER', 'SQLITE_MASTER',
            'SYSOBJECTS', 'SYS.TABLES', 'SYS.COLUMNS', # Пример для других БД
            'PG_STAT_STATEMENTS', # Пример для Postgres
        }

    def _check_forbidden_tokens(self, parsed_statement):
        """Проверяет наличие запрещенных ключевых слов и токенов, включая комментарии."""
        for token in parsed_statement.tokens:
            if token.is_group:
                self._check_forbidden_tokens(token) # Рекурсивно проверяем группы
            elif token.ttype in Keyword:
                if token.normalized in self.forbidden_keywords:
                    raise SQLValidationException(
                        f"Forbidden keyword or operation: '{token.normalized}'."
                    )
            elif str(token) == ';': # Символ разделителя команд
                raise SQLValidationException("Multiple SQL commands are forbidden (';' character).")
            # Проверка на комментарии (sqlparse обычно удаляет комментарии или классифицирует их как Whitespace,
            # но явная проверка не помешает для надежности)
            elif token.is_whitespace and (token.value.strip().startswith('--') or token.value.strip().startswith('/*')):
                raise SQLValidationException("SQL comments are forbidden.")

    def _find_select_columns_and_check_wildcard(self, parsed_statement, involved_tables):
        """
        Находит список колонок в SELECT-операторе и проверяет на 'SELECT *'.
        Вызывается только один раз для корневого Statement.
        """
        select_found = False
        for i, token in enumerate(parsed_statement.tokens):
            if token.ttype is Keyword and token.normalized == 'SELECT':
                select_found = True
                # Ищем следующий значимый токен (пропускаем пробелы)
                j = i + 1
                while j < len(parsed_statement.tokens) and parsed_statement.tokens[j].is_whitespace:
                    j += 1
                
                if j < len(parsed_statement.tokens):
                    column_list_token = parsed_statement.tokens[j]
                    
                    if column_list_token.ttype == Wildcard:
                        raise SQLValidationException(f"Query 'SELECT *' is not allowed. Specify concrete columns.")
                    elif isinstance(column_list_token, IdentifierList):
                        for identifier in column_list_token.get_identifiers():
                            if identifier.ttype == Wildcard:
                                raise SQLValidationException(f"Query 'SELECT *' is not allowed. Specify concrete columns.")
                            self._validate_single_identifier(identifier, involved_tables)
                    elif isinstance(column_list_token, Identifier):
                        if column_list_token.ttype == Wildcard:
                            raise SQLValidationException(f"Query 'SELECT *' is not allowed. Specify concrete columns.")
                        self._validate_single_identifier(column_list_token, involved_tables)
                    elif isinstance(column_list_token, Function):
                        # Если это функция (как COUNT(*)), проверяем её аргументы
                        # '*' внутри COUNT(*) разрешен, но другие идентификаторы должны быть проверены
                        for sub_token_in_func in column_list_token.tokens:
                            if sub_token_in_func.ttype == Wildcard:
                                continue # '*' inside aggregate functions is allowed
                            if sub_token_in_func.is_group or isinstance(sub_token_in_func, Identifier) or isinstance(sub_token_in_func, IdentifierList):
                                self._check_table_and_column_access_recursive(sub_token_in_func, involved_tables)
                break 
        
        if not select_found and parsed_statement.get_type() == 'SELECT':
             # Should not happen with properly parsed SELECT statements, but a fallback
             pass 

    def _check_table_and_column_access_recursive(self, current_token, involved_tables):
        """
        Рекурсивная часть для обхода токенов и проверки доступа к таблицам/колонкам.
        """
        if current_token.is_group:
            if isinstance(current_token, Function):
                for sub_token in current_token.tokens:
                    if sub_token.ttype == Wildcard:
                        continue 
                    if sub_token.is_group or isinstance(sub_token, Identifier) or isinstance(sub_token, IdentifierList):
                        self._check_table_and_column_access_recursive(sub_token, involved_tables)
            else:
                for sub_token in current_token.tokens:
                    self._check_table_and_column_access_recursive(sub_token, involved_tables)
        elif isinstance(current_token, Identifier) or isinstance(current_token, IdentifierList):
            for identifier in current_token.get_identifiers():
                self._validate_single_identifier(identifier, involved_tables)


    def _validate_single_identifier(self, identifier: Identifier, involved_tables: set):
        """Вспомогательная функция для валидации одиночного идентификатора (таблицы или колонки)."""

        full_name_lower = identifier.normalized.lower()

        if identifier.is_alias and '.' not in identifier.normalized:
            return

        # Проверка на системные таблицы/схемы
        if '.' in full_name_lower:
            parts = full_name_lower.split('.')
            schema_or_table_part = parts[0]
            if schema_or_table_part in self.forbidden_system_tables:
                raise SQLValidationException(f"Access to system schema or table is forbidden: '{schema_or_table_part}'.")
        
        if full_name_lower in self.forbidden_system_tables:
            raise SQLValidationException(f"Access to system table is forbidden: '{full_name_lower}'.")

        table_name_for_identifier = None
        column_name_lower = None

        if identifier.is_field or (identifier.is_group and any(t.is_field for t in identifier.tokens)):
            
            # Find the actual field within the identifier or group
            potential_field_tokens = []
            if identifier.is_field:
                potential_field_tokens.append(identifier)
            elif identifier.is_group:
                # Iterate through tokens in the group to find an actual field
                for token_in_group in identifier.flatten(): # Use flatten to get all sub-tokens
                    if isinstance(token_in_group, Identifier) and token_in_group.is_field:
                        potential_field_tokens.append(token_in_group)
            
            for field_token in potential_field_tokens:
                column_name_lower = field_token.get_name().lower()
                if field_token.get_parent_name():
                    table_name_for_identifier = field_token.get_parent_name().normalized.lower()
                break # Only need the first field found

            if column_name_lower:
                if table_name_for_identifier:
                    if table_name_for_identifier not in self.allowed_tables_and_columns:
                        raise SQLValidationException(f"Access to table '{table_name_for_identifier}' is not allowed.")
                    if column_name_lower not in self.allowed_tables_and_columns[table_name_for_identifier]:
                        raise SQLValidationException(f"Access to column '{column_name_lower}' in table '{table_name_for_identifier}' is not allowed.")
                else: # Column without explicit table prefix, must be in one of the involved tables
                    found_in_allowed_table = False
                    for tbl_name in involved_tables:
                        if tbl_name in self.allowed_tables_and_columns and \
                           column_name_lower in self.allowed_tables_and_columns[tbl_name]:
                            table_name_for_identifier = tbl_name 
                            found_in_allowed_table = True
                            break
                    if not found_in_allowed_table:
                        raise SQLValidationException(f"Column '{column_name_lower}' is not associated with an allowed table or is invalid.")

        elif identifier.is_table:
            table_name_for_identifier = full_name_lower
            if table_name_for_identifier not in self.allowed_tables_and_columns:
                raise SQLValidationException(f"Access to table '{table_name_for_identifier}' is not allowed.")
            
        
    def _check_functions(self, parsed_statement):
        """Проверяет наличие запрещенных функций."""
        for token in parsed_statement.tokens:
            if token.is_group:
                self._check_functions(token)
            elif isinstance(token, Function):
                function_name = token.get_name().upper()
                # Special handling for COUNT(*), which is generally safe
                if function_name == 'COUNT' and any(t.ttype == Wildcard for t in token.tokens):
                    continue # COUNT(*) is allowed
                
                if function_name in self.forbidden_functions:
                    raise SQLValidationException(
                        f"Forbidden SQL function: '{token.get_name()}'."
                    )

    def _enforce_limit(self, sql_query: str) -> str:
        """
        Проверяет и принудительно устанавливает LIMIT.
        Возвращает модифицированный SQL-запрос.
        """
        parsed_statements = sqlparse.parse(sql_query)
        if not parsed_statements:
            return sql_query
        parsed = parsed_statements[0]

        if parsed.get_type() != 'SELECT':
            return sql_query

        has_limit = False
        current_limit_value = None
        
        for i, token in enumerate(parsed.tokens):
            if token.ttype is Keyword and token.normalized == 'LIMIT':
                has_limit = True
                next_token_index = i + 1
                while next_token_index < len(parsed.tokens) and parsed.tokens[next_token_index].is_whitespace:
                    next_token_index += 1
                
                if next_token_index < len(parsed.tokens) and parsed.tokens[next_token_index].ttype is Number.Integer:
                    try:
                        current_limit_value = int(parsed.tokens[next_token_index].value)
                    except ValueError:
                        pass 
                break 

        if not has_limit:
            trimmed_query = sql_query.rstrip()
            if trimmed_query.endswith(';'):
                trimmed_query = trimmed_query[:-1]
            return f"{trimmed_query} LIMIT {self.max_limit}"
        
        if current_limit_value is not None and current_limit_value > self.max_limit:
            new_query_tokens = []
            replace_next = False
            for token in parsed.tokens:
                if token.ttype is Keyword and token.normalized == 'LIMIT':
                    new_query_tokens.append(token.value)
                    new_query_tokens.append(f" {self.max_limit}")
                    replace_next = True
                elif replace_next and token.ttype is Number.Integer:
                    replace_next = False
                else:
                    new_query_tokens.append(token.value)
            return ''.join(new_query_tokens)
        
        return sql_query


    def validate_and_process_sql(self, sql_query: str) -> str:
        """
        Валидирует и обрабатывает SQL-запрос.
        :param sql_query: SQL-запрос, сгенерированный LLM.
        :return: Валидированный и, возможно, модифицированный SQL-запрос.
        :raises SQLValidationException: Если запрос не прошел валидацию.
        """
        sql_query = sql_query.strip()

        parsed_statements = sqlparse.parse(sql_query)
        if not parsed_statements:
            raise SQLValidationException("SQL query is empty or invalid.")
        if len(parsed_statements) > 1:
            raise SQLValidationException("Multiple SQL commands are forbidden.")

        parsed = parsed_statements[0]

        if not parsed.get_type() == 'SELECT':
            raise SQLValidationException("Only SELECT queries are allowed.")

        self._check_forbidden_tokens(parsed)
        self._check_functions(parsed)

        involved_tables = set()
        
        def _collect_involved_tables_recursive(current_token):
            nonlocal involved_tables
            if current_token.is_group:
                # If it's a FROM or JOIN group, get identifiers directly
                if hasattr(current_token, 'get_type') and current_token.get_type() in ['FROM', 'JOIN']:
                    for identifier in current_token.get_identifiers():
                        # Extract base table name if it's an alias like "table AS alias"
                        if hasattr(identifier, 'get_real_name'):
                            involved_tables.add(identifier.get_real_name().lower())
                        else:
                            involved_tables.add(identifier.normalized.lower())
                
                # Recursively check all sub-tokens
                for sub_token in current_token.tokens:
                    _collect_involved_tables_recursive(sub_token)
            elif isinstance(current_token, Identifier) and current_token.is_table:
                if hasattr(current_token, 'get_real_name'):
                    involved_tables.add(current_token.get_real_name().lower())
                else:
                    involved_tables.add(current_token.normalized.lower())
            
        _collect_involved_tables_recursive(parsed)

        # Проверка на SELECT * и валидация колонок в SELECT-списке
        self._find_select_columns_and_check_wildcard(parsed, involved_tables)

        # Проверка всех остальных идентификаторов (в WHERE, GROUP BY, ORDER BY)
        # Исключаем SELECT-лист, так как он уже проверен `_find_select_columns_and_check_wildcard`
        # Делаем это через обход токенов, исключая IdentifierList/Identifier сразу после SELECT
        select_list_checked = False
        for i, token in enumerate(parsed.tokens):
            if token.ttype is Keyword and token.normalized == 'SELECT':
                j = i + 1
                while j < len(parsed.tokens) and parsed.tokens[j].is_whitespace:
                    j += 1
                if j < len(parsed.tokens):
                    select_list_token = parsed.tokens[j]
                    # This token and its children are considered handled by _find_select_columns_and_check_wildcard
                    select_list_checked = True # Mark that we've passed the select list

            if select_list_checked and i > j: # Only process tokens *after* the select list
                self._check_table_and_column_access_recursive(token, involved_tables)
            elif not select_list_checked: # Process tokens before the SELECT keyword
                self._check_table_and_column_access_recursive(token, involved_tables)

        processed_sql = self._enforce_limit(sql_query)

        return processed_sql