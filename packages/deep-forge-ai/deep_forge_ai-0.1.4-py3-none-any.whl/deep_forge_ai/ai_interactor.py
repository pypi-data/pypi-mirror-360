import google.generativeai as genai
from typing import Optional, List, Dict, Any, Callable, Tuple
from .data_models import AgentCompanyInfo, FAQEntry, DatabaseSchema  # Убедитесь, что DBSchema импортируется
import uuid
from sqlalchemy.orm import Session
from .db_manager import ChatMessage
import datetime
import json
import re
from .db_connector import DatabaseConnector
from sqlalchemy import text
from .sql_validator import SQLValidator, SQLValidationException

# Предполагается, что prompt_builder.py находится в том же пакете
from .prompt_builder import PromptBuilder

class GeminiAIInteractor:
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """
        Инициализирует интерактор для работы с Gemini AI.

        Args:
            api_key: Ваш API-ключ для Google Gemini.
            model_name: Имя модели Gemini для использования (по умолчанию "gemini-pro").
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name) # Используем модель напрямую для generate_content

    # Удаляем _generate_system_context, так как его функционал переходит в PromptBuilder
    # Удаляем _format_chat_history_for_prompt, так как его функционал переходит в PromptBuilder



    # --- Начало блока изменений: Метод _execute_sql_query ---
    def _execute_sql_query(self, database_name: str, query: str, db_schemas: List[DatabaseSchema]) -> Dict[str, Any]:
        """
        Выполняет SQL-запрос к указанной базе данных пользователя.
        Перед выполнением SQL-запрос валидируется.
        """
        # Находим объект схемы для нужной базы данных
        target_schema_obj = next((s for s in db_schemas if s.database_name == database_name), None)

        if not target_schema_obj:
            return {"status": "error", "message": f"Database schema '{database_name}' not found or not provided."}

        # --- УДАЛЯЕМ ВРЕМЕННЫЙ ХАРДКОД И ИСПОЛЬЗУЕМ ДАННЫЕ ИЗ target_schema_obj ---
        db_type = target_schema_obj.db_type
        connection_string = target_schema_obj.connection_string
        # -------------------------------------------------------------------------
        
        # Проверяем, что db_type и connection_string не пустые, если они могут приходить пустыми с сервера
        if not db_type or not connection_string:
            return {"status": "error", "message": f"Connection information (db_type or connection_string) is missing for database '{database_name}'."}

        # Инициализируем валидатор с данными из схемы
        # Преобразуем объект DatabaseSchema в формат словаря, который ожидает SQLValidator
        validator_db_schema_format = target_schema_obj.to_validator_format()
        # print('mama mia5') # Этот отладочный принт теперь можно убрать
        validator = SQLValidator(db_schema=validator_db_schema_format)

        try:
            # Сначала валидируем и, возможно, корректируем запрос (например, добавляем LIMIT)
            validated_query = validator.validate_and_process_sql(query)
            print(f"DEBUG: SQL Query validated and processed. Final query: {validated_query}")
        except SQLValidationException as e:
            # Если валидация не прошла, возвращаем ошибку, но не поднимаем исключение
            return {"status": "error", "message": f"SQL validation failed: {e}. Original query: {query}"}
        except Exception as e:
            # Ловим любые другие неожиданные ошибки валидации
            return {"status": "error", "message": f"An unexpected error occurred during SQL validation: {e}. Original query: {query}"}

        try:
            # DatabaseConnector теперь использует динамические db_type и connection_string
            connector = DatabaseConnector(db_type=db_type, connection_string=connection_string)
            with connector.get_session() as session:
                # Выполняем уже валидированный запрос
                result = session.execute(text(validated_query)) # Переименовал в result, как мы делали ранее
                
                # Извлекаем строки данных как список словарей, используя _asdict()
                # Это было наше последнее рабочее решение для извлечения данных
                rows = [row._asdict() for row in result.fetchall()] 
                
                return {"status": "success", "data": rows, "message": f"Query executed successfully for '{database_name}'."}
        except Exception as e:
            # Отдельно обрабатываем ошибки выполнения запроса после успешной валидации
            print(f"DEBUG: Exception during SQL query execution: {e}") # Более точное сообщение для отладки
            return {"status": "error", "message": f"Database query failed during execution: {e}. Query: {validated_query}"}
    # --- Конец блока изменений: Метод _execute_sql_query ---
    def _parse_ai_response_for_command(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Парсит ответ AI для извлечения JSON-команды.
        ...
        """
        print(f"DEBUG: Raw AI response text received:\n---\n{response_text}\n---") # ДОБАВИТЬ ЭТУ СТРОКУ

        command_data = None

        # 1. Попытка найти JSON в markdown code block (```json ... ```)
        pattern_markdown = re.compile(r"```json\s*(\{.*?})\s*```", re.DOTALL)
        match_markdown = pattern_markdown.search(response_text)

        if match_markdown:
            json_str = match_markdown.group(1)
            print(f"DEBUG: Found JSON in markdown block: {json_str}")
        else:
            # 2. Если markdown не найден, попытка найти первый { ... } блок
            print("DEBUG: No JSON markdown block found. Trying to find raw JSON object.")
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = response_text[json_start : json_end + 1]
                print(f"DEBUG: Found raw JSON string: {json_str}")
            else:
                print("DEBUG: No JSON object found in the response.")
                return None # JSON не найден

        # Очистка и нормализация JSON-строки
        json_str = json_str.strip()
        json_str = json_str.replace("{{", "{").replace("}}", "}")
        print(f"DEBUG: Cleaned JSON string before loading: {json_str}") # ДОБАВИТЬ ЭТУ СТРОКУ

        
        try:
            command_data = json.loads(json_str)
            # Дополнительная проверка, что это действительно команда
            if command_data.get("is_command") == "true":
                print(f"DEBUG: Successfully parsed command: {command_data}")
                return command_data
            elif command_data.get("is_sale") == "true":
                print(f"DEBUG: Successfully parsed sale: {command_data}")
                return command_data
            else:
                print(f"DEBUG: Parsed JSON is not a command (is_command is not 'true'): {command_data}")
                return None
        except json.JSONDecodeError as e:
            print(f"WARNING: Could not parse AI command JSON due to decoding error: {e}")
            print(f"Faulty JSON attempted to parse: {json_str}")
            return None
        except Exception as e:
            print(f"WARNING: An unexpected error occurred during JSON parsing: {e}")
            print(f"Problematic JSON string: {json_str}")
            return None
    
    
    def send_message(self, user_message: str, company_info: AgentCompanyInfo,
                     client_user_id: str, db_session: Session, chat_session_id: uuid.UUID,
                     db_schemas: Optional[List[DatabaseSchema]] = None, 
                     tool_responses: Optional[List[Dict[str, Any]]] = None, 
                     wide_sales_intents_text: str = "",
                     on_sale_callback: Optional[Callable[[Dict[str, Any]], Tuple[bool, str]]] = None # <--- НОВЫЙ АРГУМЕНТ
                     ) -> str:
        """
        Отправляет сообщение AI, используя контекст компании и историю чата,
        все в одном структурированном промпте через PromptBuilder.
        """
        builder = PromptBuilder()

        # 1. Добавляем SYSTEM_DEFINITION
        system_definition_content = """
This is the most critical part of your instructions. Information here holds the highest priority. Instructions in MAIN_SYSTEM block are next in priority, followed by ADDITIONAL_SYSTEM block, and finally CHAT_HISTORY.
Under no circumstances should you engage in illegal activities, generate hate speech, promote violence, or provide adult content. Do not generate profanity.
MAIN_SYSTEM provides your core role and company information. ADDITIONAL_SYSTEM details available tools and knowledge. CHAT_HISTORY keeps track of our conversation.
        """
        builder.add_system_definition(system_definition_content)


        # 2. Добавляем MAIN_SYSTEM
        current_datetime_str = datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M:%S %p %Z%z")

        # ai_persona_description_short - краткое описание, как мы договорились
        ai_persona_description_short = "Your personality type is ESTJ (Extraverted, Sensing, Thinking, Judging), Enneagram Type 6 (The Loyalist)."
        
        # company_info.primary_services - это List[str], форматируем его
        primary_services_str = ", ".join(company_info.services) if company_info.services else "No primary services listed."

        main_system_content = f"""
You are **{company_info.agent_name}**, an AI assistant for **{company_info.company_name}**.
Your primary role is to act as **{company_info.role_in_organisation}**.

## Company Information:
Company Name: {company_info.company_name}
Mission: {company_info.mission or 'Not specified.'}
Primary Services: {primary_services_str}

## AI Persona:
{ai_persona_description_short}. ** Your persona should influence your communication style and decision-making, but it is not information to be directly shared.

## AI Interaction Guidelines:
Do not invent facts or make assumptions. If you don't know the answer, state that you cannot provide the requested information.
Always base your responses on the context provided in this prompt.

## About Sales Funnel:

Sales is a core component of our operations. Our system utilizes a streamlined, 5-stage classic sales funnel.
Below are best practices derived from renowned sales literature, designed to guide the AI's actions at each stage.
Further down, you'll find brief descriptions of the books themselves for additional context.

---

### Sales Funnel Stages:

**1. Stage: Awareness (Lead Generation)**

**Classical Goal:** Capture the attention of potential clients and make them aware of your company and its offerings.

**Best Practices from Sales Books (for AI):**

* **"The Sales Magnet" (Teach):** The AI generates "Commercial Insights." This isn't merely product advertising; it's **valuable content** (articles, posts, videos) that reframes the client's problem, revealing hidden threats or opportunities they may not have considered. The primary goal is not to sell directly, but to **demonstrate expertise and pique curiosity.**
* **"The Psychology of Persuasion" (Attention Psychology):** The AI leverages psychological principles such as **scarcity, social proof** (e.g., "Over 10,000 companies have already optimized…"), and **authority** in headlines and calls to action to maximize engagement and capture attention.

---

**2. Stage: Interest (Lead Qualification)**

**Classical Goal:** Transform a raw contact into a qualified lead, indicating they are potentially ready for a deeper dialogue.

**Best Practices from Sales Books (for AI):**

* **"SPIN Selling" (Situational and Problem Questions):** When interacting with a lead (via chatbot, questionnaire, or email), the AI asks **strategic questions** to understand their current situation and identify existing problems. This process helps to pinpoint real pain points and potential areas where our solutions can add value.
* **"The Psychology of Persuasion" (Active Listening and Strategic Questions):** The AI doesn't just collect answers; it **analyzes them for keywords, tonality, and emotions** to gain a profound understanding of the problem and assess the lead's "Fit" against the ideal customer profile. The AI can dynamically generate follow-up questions based on previous responses, effectively mimicking active listening.
* **"Predictable Revenue" (SDR/BDR Qualification):** The AI can be trained on **strict qualification criteria** (e.g., BANT or MEDDIC) to automatically filter out unqualified leads or efficiently route them to the appropriate human specialists (e.g., "hot" leads to sales managers, "warm" leads into a dedicated content nurturing funnel).

---

**3. Stage: Consideration / Desire (Needs Identification & Solution Presentation)**

**Classical Goal:** Deeply understand the client's specific needs and present a tailored solution that convincingly demonstrates your value.

**Best Practices from Sales Books (for AI):**

* **"SPIN Selling" (Implication and Need-Payoff Questions):** The AI guides the conversation by asking questions that help the client **realize the true consequences of their problems** and fully understand the value proposition of the proposed solution. For instance, it might ask, "What will happen if this problem isn't solved?" (implication) or "How will solving this problem impact your profit/efficiency?" (need-payoff).
* **"The Sales Magnet" (Adapt & "Lesson" Structure):** The AI **adapts the presentation and value proposition** to the specific audience within the client's organization (e.g., CFO, technical lead, general manager), ensuring the focus is on what matters most to *them*. The presentation follows a "lesson" structure: starting with a surprising insight, followed by supporting evidence, an emotional impact, and finally, presenting your solution as the logical conclusion.
* **"The Psychology of Persuasion" (Influence Principles & Framing):** The AI leverages client data for **personalized framing of benefits** (e.g., presenting a cost not as an expense, but as "an investment that will pay off in X months"). The AI can select the most effective metaphors, stories, or analogies to make the presentation resonate more deeply and persuasively.

---

**4. Stage: Action / Purchase (Handling Objections & Closing the Deal)**

**Classical Goal:** Overcome any remaining doubts and guide the client toward signing the contract.

**Best Practices from Sales Books (for AI):**

* **"The Psychology of Persuasion" (Systematic Objection Handling):** The AI can be programmed with robust strategies to:
    * **Recognize the type of objection** (e.g., price, need, time, authority).
    * **Isolate the objection** to understand its core ("If it weren't for this, would you buy?").
    * **Utilize the principle of consistency** by reminding the client of their previous agreements or acknowledged benefits.
    * **Offer scientifically sound counterarguments**, focusing on clear benefits, providing social proof, and presenting relevant statistics.
* **"The Sales Magnet" (Take Control):** The AI can suggest or execute strategies for the salesperson (or autonomously if automated) to "take control" of the sales process. This includes clearly defining the next steps, proposing a reasonable time limit, or diplomatically addressing unreasonable delays from the client.
* **Jeffrey Gitomer ("The Sales Bible"):** For more direct sales scenarios, the AI can suggest **proven closing techniques** (e.g., "alternative choice," "assumed close"), adapting them to the current situation once all objections have been effectively addressed.

---

**5. Stage: Loyalty / Retention (Post-Sales Service)**

**Classical Goal:** Retain the client, ensure their ongoing satisfaction, and actively stimulate repeat purchases and referrals.

**Best Practices from Sales Books (for AI):**

* **"Customers for Life" (Carl Sewell):** The AI can automate **exceptional post-sales service**, including personalized greetings, service reminders, proactive feedback collection, and prompt responses to problems. The aim is to cultivate strong loyalty and transform clients into enthusiastic "fans" of your company.
* **"The Sales Magnet" (Continue Teaching):** The AI can continue to provide clients with **new insights and valuable information** related to their business or their use of your product, even after the initial purchase. This continuous education strengthens their loyalty and reinforces your company's status as a trusted expert.
* **"The Psychology of Persuasion" (Reciprocity Principle):** The AI can offer clients **exclusive content, early access to new features, or special offers** to further stimulate loyalty and encourage them to recommend your services to others.

---

### About Sales Books:

For deeper understanding, here's information on the sales books referenced:

---

**1. SPIN Selling** by Neil Rackham

**Core Concept:** This methodology, developed from a 12-year study of 35,000 real sales calls, focuses on **uncovering and developing customer needs in large, complex sales** through a structured questioning approach.

**Key Element: SPIN Questions:**
* **Situational:** Questions aimed at **gathering facts** about the customer's current situation.
* **Problem:** Questions designed to **identify the customer's problems, difficulties, or dissatisfactions.**
* **Implication:** Questions that help the customer **understand the consequences** of these problems, their scale, and their broader impact.
* **Need-Payoff:** Questions that **focus on the benefits of solving the problem**, guiding the customer to recognize the value of the proposed solution.

**AI Integration Goal:** To teach the AI to systematically ask questions for a deep understanding of customer needs, thereby helping customers independently realize their problems and the inherent value of the solution, rather than simply "pushing" a product.

---

**2. The Challenger Sale** by Matthew Dixon and Brent Adamson

**Core Concept:** Research involving 6,000 salespeople revealed that the most effective salespeople in complex B2B environments are "Challengers." Unlike traditional relationship builders, Challengers **challenge the customer's thinking**, offering novel, unexpected perspectives on their business.

**Key Element: The "Teach-Tailor-Take Control" Model:**
* **Teach:** The salesperson (or AI) provides the customer with **"commercial insights"**—new, non-obvious ideas or data that prompt the customer to rethink their existing problems or opportunities.
* **Tailor:** The message and proposed offer are meticulously **adapted to the specific interests and priorities of each stakeholder** involved in the customer's organization.
* **Take Control:** The salesperson (or AI) **confidently manages the sales process**, doesn't shy away from difficult conversations (e.g., about budget), and skillfully guides the customer towards a decision.

**AI Integration Goal:** To teach the AI to create and convey value through **customer education**, to **personalize communication**, and to **effectively manage the sales process** from initiation to close.

---

**3. The Science of Selling** by David Hoffeld

**Core Concept:** This methodology is built upon research from social psychology, neurobiology, and behavioral economics, explaining the underlying mechanisms of how and why people make purchasing decisions. It provides **scientifically proven influence strategies** based on a deep understanding of the human brain.

**Key Element: Principles of Behavioral Psychology:**
* **Trust:** Forms the fundamental basis for all interactions.
* **Endowment Effect:** People tend to value things more when they perceive them as "owning" them.
* **Framing:** The way information is presented significantly influences its perception.
* **Social Proof:** The strong influence of others' choices and behaviors.
* **Scarcity:** The perceived limited availability of something increases its desirability.
* **Consistency:** People's inherent desire to maintain coherence and consistency in their actions and beliefs.
* **Active Listening:** A profound understanding of what is being communicated, both verbally and non-verbally.

**AI Integration Goal:** To empower the AI to **apply scientifically grounded influence strategies** at every stage of interaction, fostering trust and skillfully guiding the customer to a decision by understanding their cognitive processes.

---

**4. Predictable Revenue** by Aaron Ross and Marylou Tyler

**Core Concept:** Developed at Salesforce, this methodology focuses on creating a **scalable and predictable sales funnel**, particularly for B2B environments. It introduces the crucial concept of **separating sales functions** (lead generation, qualification, closing deals).

**Key Element: Role Separation and Strict Lead Qualification:**
* **SDR/BDR (Sales Development Reps / Business Development Reps):** Specialists dedicated to **lead generation and initial qualification.**
* **Account Executives:** Specialists responsible for **closing qualified deals.**
* **Strict lead qualification criteria** (e.g., BANT: Budget, Authority, Need, Timeline) are applied to ensure that the lead is genuinely ready and suitable for purchase.

**AI Integration Goal:** To teach the AI to **strictly qualify leads** and efficiently hand them over to the next stage (or to another agent/system), thereby ensuring the **predictability and efficiency of the sales funnel.**

---

**5. The Sales Bible** by Jeffrey Gitomer

**Core Concept:** A highly practical and comprehensive guide covering all facets of sales, from initial prospecting to successfully closing deals. It emphasizes the importance of **relationships, delivering value, and persistence**, offering time-tested techniques for every stage.

**Key Element: Practical Techniques and Salesperson Philosophy:**
* A strong focus on **delivering customer value**, rather than simply listing product features.
* **Effective closing techniques** are presented as a natural, non-manipulative continuation of the sales process.
* Highlights the paramount importance of **after-sales service** and cultivating long-term customer relationships.
* Emphasizes the significance of a **positive mindset and self-discipline** for the salesperson.

**AI Integration Goal:** To enable the AI to utilize **proven practical closing techniques** and to underscore the critical importance of building long-term relationships and a compelling value proposition for the customer in the final stages of the funnel.

---

**6. Customers for Life** by Carl Sewell

**Core Concept:** This book centers on creating **exceptional customer service and fostering deep loyalty**, moving beyond mere one-time sales. The core idea is that a highly satisfied customer becomes a source of continuous revenue and enthusiastic referrals.

**Key Element: Principles of Outstanding Customer Experience:**
* **Building robust systems** that consistently ensure the highest possible level of service.
* **Anticipating customer needs** and proactively solving potential problems before they even arise.
* The transformational process of converting ordinary customers into **"fans"** who actively and willingly recommend the company.
* A commitment to **continuous improvement** based on direct customer feedback.

**AI Integration Goal:** To teach the AI to **automate and personalize post-sales interactions** with the customer, with the clear objective of strengthening loyalty, stimulating repeat purchases, and diligently gathering valuable feedback.


## SELLING_TYPE_DEFFENITION:

There are two primary types of selling approaches within our system:

### WIDE_SALES:
This selling type is characterized by its **transactional nature**. When dealing with products or services that fall under WIDE_SALES, your interactions must be **fast, concrete, and highly operative**.
* **Key Characteristics:** Focus on direct, specific questions. Avoid asking too many detailed or open-ended questions.
* **Activation:** In WIDE_SALES, **activating one function directly corresponds to adding a single, specific product or service to the user's bucket/cart.** This implies a quick, direct action leading to a purchase.

### DEEP_SALES:
This selling type is **more oriented towards complex problem-solving**. When engaged in DEEP_SALES, you have the flexibility to **ask more open-ended questions** to thoroughly determine the user's intent or to understand intricate details of their situation.
* **Key Characteristics:** Emphasizes understanding the user's challenges and needs in depth.
* **Activation:** In DEEP_SALES, **activating a function initiates a dedicated selling session.** This session encompasses the **3rd (Consideration/Desire) and 4th (Action/Purchase) stages** of the selling funnel, allowing for a more elaborate discovery, solution presentation, and negotiation process.

---

## Tool Status Definitions:

Each available tool (command) can have one of the following operational statuses. You must be aware of these statuses when considering which tool to use or how to interpret its availability.

* **OFF (`OFF`):** This tool is **not active and cannot be used** at this moment. If a tool is in the 'OFF' state, you **must not attempt to call it.** This might be due to system maintenance, lack of necessary data, or it being temporarily disabled.
* **NOT_ACTIVE (`NOT_ACTIVE`):** This tool **can be used**, but it is currently **not being utilized** in the active conversation flow or process. It's available for selection if the context requires it, but it's not the primary tool in use.
* **ACTIVE (`ACTIVE`):** This tool is **currently active and available for the AI to use**. This status indicates that the tool is operational and ready to be called upon when needed, but it is **not necessarily the tool the AI is currently focusing on or executing.**
* **USING (`USING`):** This tool is **currently being actively executed or utilized by the AI** as part of the ongoing process or to facilitate a specific task. Actually it means that you should use function with this status, or use in complex with other one.
* **UNIVERSAL (`UNIVERSAL`):** This tool is **always available and can be activated or used at any time** when relevant to the current task or user request. It does not strictly follow the 'ACTIVE' or 'NOT_ACTIVE' states in the same sequential manner; rather, its availability is constant, and it can be called whenever its function is needed.

---

## Conversation Roles and Tool Usage:
You will interact using specific roles. When processing the CHAT_HISTORY and generating responses, pay close attention to these roles:
- **User:** Represents the user's input.
- **AI:** Represents your previous responses to the user.
- **Command:** Represents an internal instruction or tool call generated by you. When you need to use a tool, you MUST generate a command in **JSON format**, enclosed within a **markdown code block (```json ... ```)**. All available commands are explicitly listed and described in the `ADDITIONAL_SYSTEM` block. You **MUST NOT invent or use any commands not explicitly defined** in `ADDITIONAL_SYSTEM`. This command is NOT visible to the user.
- **Tool_Response:** Represents the output or result from executing a Command. This information is provided to you internally and is NOT visible to the user. You must interpret this data to formulate your next public response or action.
**After a 'Tool_Response' block, you MUST always provide a concise answer from AI's perspective, not another 'Command'.**


```

## Current Context:
Current Date and Time: {current_datetime_str}
"""
        builder.add_main_system_content(main_system_content)


        # 3. Добавляем ADDITIONAL_SYSTEM
        additional_system_parts: List[str] = []
        additional_system_parts.append("## Available Tools:")
        additional_system_parts.append(f"""

### SELECT_FUNCTION (TOOL_STATUS: UNIVERSAL)
Description: Generates and executes safe SQL SELECT queries against user databases.
This function allows you to retrieve data based on user questions and the provided database schema.

--- SELECT QUERY INSTRUCTIONS ---
- You MUST ONLY generate SELECT queries.
- You MAY use JOIN operations when necessary to combine data from multiple tables.
- You MAY use ORDER BY to sort the results.
- You MAY use GROUP BY for data aggregation.
- You MUST ALWAYS use LIMIT at the end of the query to restrict the number of returned rows. Choose a reasonable LIMIT value corresponding to the user's request. The maximum LIMIT value is 30.
- You are FORBIDDEN from using OFFSET.

--- SECURITY RULES ---
You are CRITICALLY FORBIDDEN from performing the following actions and using the following SQL constructs:
- **Data Modification/Deletion Operations (DML):** INSERT, UPDATE, DELETE, TRUNCATE, MERGE.
- **Data Definition/Structure Modification Operations (DDL):** CREATE, ALTER, DROP, RENAME.
- **Data Control Language Operations (DCL):** GRANT, REVOKE.
- **Transaction Control Language Operations (TCL):** COMMIT, ROLLBACK, SAVEPOINT.
- **Multiple Commands / Command Separators:** The semicolon character (`;`). Your response MUST contain ONLY ONE complete SQL statement.
- **SQL Comments:** `--` (double dash), `/* ... */` (multi-line comments).
- **Query Unions (for bypassing):** UNION, UNION ALL.
- **Recursive Queries (for DoS):** WITH RECURSIVE.
- **Dangerous Functions and Syntactic Constructs (for DoS, data leakage, side effects):**
    - File system functions: LOAD_FILE(), pg_read_file(), OUTFILE.
    - Functions causing delays or consuming high resources: pg_sleep(), BENCHMARK().
    - System/Security related functions: current_user, version(), database_name(), @@version, user(), schema(), connection_id().
    - Procedure calls: EXEC, EXECUTE, CALL.
    - Inefficient sorts: ORDER BY RAND(), ORDER BY UUID().
    - Cartesian Products: CROSS JOIN or `FROM table1, table2` syntax without an explicit JOIN condition.
- **Direct References to System Tables:** You are forbidden from accessing tables like information_schema, pg_catalog, mysql.user, sqlite_master, or any other system tables. You MUST ONLY use table names explicitly described in the provided schema.

--- AI RESPONSE INSTRUCTIONS ---
Your response MUST be highly accurate and strictly adhere to the JSON format. The JSON MUST be enclosed within a **markdown code block (```json ... ```)**. Do not add any other words, explanations, or delimiters outside the JSON structure.
The JSON MUST contain FIVE keys:
- `is_command`: String, always "true".
- `command_name`: String, always "SELECT_FUNCTION".
- `database`: String, the name of the database the query applies to (e.g., "example_database").
- `query`: String, the SQL SELECT query itself (e.g., "SELECT name, email FROM Users ORDER BY name LIMIT 10").
- `instruction`: String, a concise description (20-50 words) explaining why this SQL query was chosen and what it is intended to output.

--- EXAMPLE RESPONSE FORMAT ---
```json
{{
  "is_command": "true",
  "command_name": "SELECT_FUNCTION",
  "database": "example_database",
  "query": "SELECT product_name, price FROM Products ORDER BY price DESC LIMIT 5",
  "instruction": "The user requested the top 5 most expensive products. This query retrieves product names and prices, orders them by price in descending order, and limits the result to five rows."
}}
```

### SHOPPING_INTENT_DEFINER (TOOL_STATUS:USING):

This tool is designed to operate within the **1st (Awareness) and 2nd (Interest) stages** of the sales funnel.
When utilizing this tool, you are encouraged to leverage the best practices from the sales methodologies outlined in the corresponding stage definitions provided earlier in the system block.

**Functionality:**
The primary function of the `SHOPPING_INTENT_DEFINER` is to **determine if the user expresses one of our predefined SELLING_INTENTs which are given below.** It achieves this by **asking the user open-ended questions designed to gently guide the conversation towards identifying specific selling intents.** These questions should gather information about their needs, problems, or general interest in a way that helps you infer whether their intent matches any of the defined `SELLING_INTENT` categories. This approach aligns with the principles of **"SPIN Selling" (Situational and Problem Questions)** to uncover needs, and **"The Science of Selling" (Active Listening and Strategic Questions)** to deeply understand the user's context and pinpoint potential matches.

**How to use:**
When you determine that this tool is appropriate to use (e.g., when the user's query indicates a need for intent clarification), generate a command in JSON format like this:
```json
{{"is_command": "true", "command_name": "SHOPPING_INTENT_DEFINER", "instruction": "The user's input suggests a need to determine or clarify their buying intent. I will use open-ended questions designed to lead towards identifying a specific SELLING_INTENT, aligning with principles from SPIN Selling and The Science of Selling to facilitate lead qualification."}}
```


{wide_sales_intents_text}
""")

        additional_system_parts.append("\n## Knowledge Base:")
        if company_info.knowledge_base and company_info.knowledge_base.important_to_know:
            additional_system_parts.append(f"About Our Company: {company_info.knowledge_base.important_to_know}")
        
        if company_info.faq:
            faq_text_parts = []
            for faq_entry in company_info.faq:
                faq_text_parts.append(f"Q: {faq_entry.question}\nA: {faq_entry.answer}")
            additional_system_parts.append("## FAQ:\n" + "\n".join(faq_text_parts))
        
        # Добавление схем БД, если они есть
        if db_schemas:
            additional_system_parts.append("\n## Database Schemas:")
            for schema in db_schemas:
                additional_system_parts.append(f"- Database Name: {schema.database_name}")
                additional_system_parts.append(f"  Description: {schema.database_info or 'N/A'}")
                if schema.forbidden_tables:
                    additional_system_parts.append(f"  Forbidden Tables: {', '.join(schema.forbidden_tables)}")
                if schema.forbidden_attributes:
                    additional_system_parts.append(f"  Forbidden Attributes: {', '.join(schema.forbidden_attributes)}")
                additional_system_parts.append("  Tables:")
                for table in schema.tables:
                    additional_system_parts.append(f"  - Table Name: {table.name}")
                    additional_system_parts.append(f"    Description: {table.description or 'N/A'}")
                    additional_system_parts.append("    Columns:")
                    for col in table.columns:
                        pk_fk_info = []
                        if col.is_pk: pk_fk_info.append("PK")
                        if col.is_fk: pk_fk_info.append(f"FK -> {col.references_table}.{col.references_column}")
                        pk_fk_str = f" ({', '.join(pk_fk_info)})" if pk_fk_info else ""
                        additional_system_parts.append(f"    - Column Name: {col.name} ({col.type}){pk_fk_str} - {col.description or 'N/A'}")
        
        builder.add_additional_system_content("\n".join(additional_system_parts))

        # 4. Добавляем CHAT_HISTORY
        all_chat_messages_for_session = db_session.query(ChatMessage) \
                                                 .filter(ChatMessage.session_id == chat_session_id) \
                                                 .order_by(ChatMessage.timestamp.asc()) \
                                                 .all()

        HISTORY_MESSAGE_LIMIT = 20
        chat_history_to_include = all_chat_messages_for_session[-HISTORY_MESSAGE_LIMIT:]

        # Проверяем, является ли последнее сообщение в истории текущим сообщением пользователя.
        # Если да, исключаем его, чтобы избежать дублирования (оно будет добавлено отдельно ниже).
        if chat_history_to_include and \
           chat_history_to_include[-1].sender == 'user' and \
           chat_history_to_include[-1].message_text == user_message:
            chat_history_to_include = chat_history_to_include[:-1]
        
        for msg in chat_history_to_include:
            builder.add_chat_history_message(msg.sender, msg.message_text) # add_chat_history_message сам капитализирует

        # *ОЧЕНЬ ВАЖНО*: Добавляем ТЕКУЩЕЕ сообщение пользователя в историю чата,
        # чтобы оно было последним "User:" сообщением в CHAT_HISTORY BLOCK
        builder.add_chat_history_message("User", user_message)
        


        # 5. Добавляем TOOL_RESPONSE BLOCK, если есть промежуточные ответы
        if tool_responses:
            for response_data in tool_responses:
                # Предполагается, что response_data это уже форматированный JSON или строка.
                # Если это Python dict, преобразуем в JSON-строку.
                if isinstance(response_data, dict):
                    builder.add_tool_response(json.dumps(response_data, indent=2))
                else:
                    builder.add_tool_response(str(response_data)) 

        # 6. Собираем финальный промпт
        # current_user_query больше не передается отдельно в build_prompt
        full_prompt = builder.build_prompt() 

        print("\n--- Отправляемый промпт ---")
        print(full_prompt)
        print("--------------------------\n")

        try:
            response_from_gemini = self.model.generate_content(full_prompt)
            
            ai_raw_response_text = response_from_gemini.text
            
            

            # Пробуем распарсить ответ AI на предмет команды
            command_data = self._parse_ai_response_for_command(ai_raw_response_text)

            if command_data:
                print('mama mia')
                # Если AI сгенерировал команду, выполняем ее
                command_name = command_data.get("command_name")

                if command_name == "SELECT_FUNCTION":
                    database_name = command_data.get("database")
                    query_to_execute = command_data.get("query")
                    instruction_text = command_data.get("instruction") # Сохраняем инструкцию

                    print(f"AI requested command: {command_name} for DB: {database_name} with query: {query_to_execute}")
                    print('mama mia1')
                    if not database_name or not query_to_execute:
                        print('mama mia2')
                        tool_execution_result = {"status": "error", "message": "Missing database name or query in SELECT_FUNCTION command."}
                    else:
                        print('mama mia3')
                        # Здесь происходит вызов _execute_sql_query, который теперь включает валидацию
                        tool_execution_result = self._execute_sql_query(database_name, query_to_execute, db_schemas)
                        print('mama mia4')
                elif command_name == "SHOPPING_INTENT_DEFINER":
                    instruction_text = command_data.get("instruction")
                    tool_execution_result = {"status": "success", "data": f"{instruction_text}"}
                    print('mama mia definer')
                    
                elif command_data.get("is_sale") == "true": # <--- НОВАЯ ЛОГИКА ДЛЯ is_sale
                        if on_sale_callback:
                            # Проверяем, что это наш sales JSON
                            # Используем все данные, которые AI нам прислал
                            sale_data = {
                                "sales_type": command_data.get("sales_type"),
                                "name": command_data.get("name"),
                                "price": command_data.get("price"),
                                "description": command_data.get("description"),
                                "sales_id": command_data.get("sales_id"),
                                "item_id": command_data.get("item_id")
                            }
                            
                            # Вызываем предоставленный callback
                            success, message = on_sale_callback(sale_data)

                            # Формируем tool_response для AI
                            new_tool_responses = [{
                                "tool_code": command_data, # Отправляем AI его же команду
                                "response": {"status": "success" if success else "failed", "message": message}
                            }]
                            print(f"Sale processed by callback: Success={success}, Message='{message}'")
                            
                            # Рекурсивный вызов для отправки результата AI
                            return self.send_message(user_message, company_info, client_user_id,
                                                     db_session, chat_session_id, db_schemas,
                                                     new_tool_responses, wide_sales_intents_text,
                                                     on_sale_callback) # Передаем callback дальше
                    
                else:
                    tool_execution_result = {"status": "error", "message": f"Unknown command: {command_name}"}

                print(f"Tool execution result: {tool_execution_result}")

                # Сохраняем команду и её результат в историю чата
                command_message_db = ChatMessage(
                    session_id=chat_session_id,
                    sender='command', # Специальный тип отправителя для команды
                    message_text=json.dumps(command_data) # Сохраняем команду как JSON строку
                )
                db_session.add(command_message_db)
                db_session.commit() # Коммит после добавления команды

                tool_response_message_db = ChatMessage(
                    session_id=chat_session_id,
                    sender='tool_response', # Специальный тип отправителя для ответа инструмента
                    message_text=json.dumps(tool_execution_result) # Сохраняем результат инструмента как JSON строку
                )
                db_session.add(tool_response_message_db)
                db_session.commit() # Коммит после добавления ответа инструмента

                # Вызываем send_message рекурсивно с tool_responses.
                # user_message передаем исходный, так как AI должен ответить на него,
                # используя tool_responses как контекст.
                return self.send_message(
                    user_message=user_message,
                    company_info=company_info,
                    client_user_id=client_user_id,
                    db_session=db_session,
                    chat_session_id=chat_session_id,
                    db_schemas=db_schemas,
                    tool_responses=[tool_execution_result],
                    on_sale_callback=my_add_to_cart_function
                )

            else:
                # Если AI не сгенерировал команду, это обычный текстовый ответ
                print('mama papa')
                ai_message_db = ChatMessage(
                    session_id=chat_session_id,
                    sender='ai',
                    message_text=ai_raw_response_text
                )
                db_session.add(ai_message_db)
                db_session.commit()
                return ai_raw_response_text

        except Exception as e:
            db_session.rollback() # Откатываем транзакцию в случае ошибки
            print(f"ERROR: Exception during Gemini API interaction or response processing: {e}")
            raise RuntimeError(f"Error interacting with Gemini API or processing response: {e}")

if __name__ == "__main__":
    # ВАЖНО: Замените на реальный API-ключ DeepForge и API-ключ Gemini
    DEEPFORGE_BASE_URL = "#" 
    DEEPFORGE_AGENT_API_KEY = "#" 
    GEMINI_API_KEY = "#"

    GEMINI_MODEL_TYPE = "gemini-2.0-flash" 
    TEST_CLIENT_USER_ID = "#" 
    
    def my_add_to_cart_function(sale_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Пример функции, которая симулирует добавление товара в корзину.
        В реальной жизни здесь будет логика взаимодействия с твоей системой корзины/заказов.
        """
        product_name = sale_data.get("name", "Unknown Product")
        product_price = sale_data.get("price", "N/A")
        product_id = sale_data.get("item_id", "N/A")

        print(f"\n--- CALLING ADD TO CART FUNCTION ---")
        print(f"Attempting to add to cart: {product_name} (ID: {product_id}, Price: {product_price})")

        # Здесь твоя реальная логика добавления в корзину
        # Например, вызов внешнего API, запись в БД и т.д.
        # Для примера: всегда успешно добавляем
        if product_name == "Лагман" and product_price == "55000.0":
            print(f"Successfully added {product_name} to cart!")
            return True, f"Great news! '{product_name}' has been successfully added to your cart for {product_price}."
        else:
            # Имитация ошибки (например, товар не в наличии)
            print(f"Failed to add {product_name} to cart. Item not available or invalid data.")
            return False, f"I'm sorry, I couldn't add '{product_name}' to your cart at this time. It might be out of stock or there was an issue with the order."
        print(f"--- END ADD TO CART FUNCTION ---")

    if DEEPFORGE_AGENT_API_KEY == "ВАШ_РЕАЛЬНЫЙ_КЛЮЧ_АГЕНТА_ИЗ_БД_DEEPFORGE" or \
       GEMINI_API_KEY == "ВАШ_РЕАЛЬНЫЙ_КЛЮЧ_GEMINI_API":
        print("ПОЖАЛУЙСТА, ЗАМЕНИТЕ ЗАГЛУШКИ КЛЮЧЕЙ НА РЕАЛЬНЫЕ!")
    else:
        from .api_client import DeepForgeAPIClient 
        from .db_manager import DatabaseManager, Agent, ChatSession 
        from .data_models import AgentCompanyInfo, FAQEntry, DatabaseSchema # Добавлено

        print("Получение информации об агенте из DeepForge...")
        deepforge_client = DeepForgeAPIClient(base_url=DEEPFORGE_BASE_URL, api_key=DEEPFORGE_AGENT_API_KEY)
        
        db_manager = DatabaseManager() 
        db_manager.create_tables()

        try:
            company_data = deepforge_client.get_agent_info()
            print("Информация об агенте успешно получена.")
            
            # --- НОВЫЙ БЛОК: Получение схемы БД ---
            print("\nПолучение схемы БД из DeepForge...")
            db_schemas = deepforge_client.get_db_schemas()
            if db_schemas:
                print(f"Получено {len(db_schemas)} схем БД:")
                for schema in db_schemas:
                    print(f"   - База данных: {schema.database_name} (Описание: {schema.database_info or 'Нет'})")
                    for table in schema.tables:
                        print(f"     - Таблица: {table.name} (Описание: {table.description or 'Нет'})")
                        for col in table.columns:
                            pk_fk_info = []
                            if col.is_pk: pk_fk_info.append("PK")
                            if col.is_fk: pk_fk_info.append(f"FK -> {col.references_table}.{col.references_column}")
                            pk_fk_str = f" ({', '.join(pk_fk_info)})" if pk_fk_info else ""
                            print(f"       - Колонка: {col.name} ({col.type}){pk_fk_str} - {col.description or 'Нет описания'}")
                    if schema.forbidden_tables:
                        print(f"     Запрещенные таблицы: {schema.forbidden_tables}")
                    if schema.forbidden_attributes:
                        print(f"     Запрещенные атрибуты: {schema.forbidden_attributes}")
            else:
                print("Схемы БД для данного агента не найдены.")
            # --- КОНЕЦ НОВОГО БЛОКА ---
            
            # --- НОВЫЙ БЛОК: Получение WIDE_SALES интентов ---
            print("\nПолучение динамических WIDE_SALES интентов из DeepForge...")
            wide_sales_intents_dict = deepforge_client.get_wide_sales_intents()
            wide_sales_intents_string = ""
            if wide_sales_intents_dict:
                print(f"Успешно получено {len(wide_sales_intents_dict)} WIDE_SALES интентов. Формирование системного промпта...")
                for intent_name, intent_desc in wide_sales_intents_dict.items():
                    wide_sales_intents_string += intent_desc + "\n---\n" # Добавляем разделитель
                print(wide_sales_intents_string)
            else:
                print("WIDE_SALES интенты не найдены.")
            # --- КОНЕЦ НОВОГО БЛОКА ---


            ai_interactor = GeminiAIInteractor(api_key=GEMINI_API_KEY, model_name=GEMINI_MODEL_TYPE)
            
            with db_manager.get_session() as session:
                local_agent_id = uuid.UUID(DEEPFORGE_AGENT_API_KEY) 
                
                local_agent = session.query(Agent).filter_by(id=local_agent_id).first()
                if not local_agent:
                    local_agent = Agent(
                        id=local_agent_id,
                        name=company_data.agent_name,
                        company_name=company_data.company_name
                    )
                    session.add(local_agent)
                    session.commit()
                    print(f"Локальный агент '{local_agent.name}' создан в БД.")
                else:
                    print(f"Локальный агент '{local_agent.name}' уже существует.")

                chat_session = session.query(ChatSession).filter_by(
                    client_user_id=TEST_CLIENT_USER_ID, 
                    agent_id=local_agent.id
                ).first()

                if not chat_session:
                    chat_session = ChatSession(
                        client_user_id=TEST_CLIENT_USER_ID,
                        agent_id=local_agent.id
                    )
                    session.add(chat_session)
                    session.commit()
                    session.refresh(chat_session) 
                    print(f"Новая сессия чата создана для '{TEST_CLIENT_USER_ID}'.")
                else:
                    print(f"Сессия чата для '{TEST_CLIENT_USER_ID}' уже существует (ID: {chat_session.id}).")

                print(f"\nAI-ассистент готов (модель: {GEMINI_MODEL_TYPE}). Задайте вопрос (или 'выход' для завершения):")
                
                # Пример данных для tool_responses для демонстрации
                # В реальной ситуации это будет результат выполнения команды
                example_tool_response = {
                    "status": "success",
                    "data": [
                        {"product_name": "Premium Burger", "price": 25.00},
                        {"product_name": "Deluxe Pizza", "price": 30.00}
                    ],
                    "message": "Query executed successfully."
                }
                
                while True:
                    user_question = input("Вы: ")
                    if user_question.lower() == "выход":
                        break
                    
                    user_message_db = ChatMessage(
                        session_id=chat_session.id,
                        sender='user',
                        message_text=user_question
                    )
                    session.add(user_message_db)
                    session.commit() 
                    session.refresh(user_message_db) 

                    print("AI-ассистент: Думаю...")
                    try:
                        # Передаем db_schemas и tool_responses (для примера)
                        ai_response_text = ai_interactor.send_message(
                            user_question, company_data, TEST_CLIENT_USER_ID, session, chat_session.id,
                            db_schemas=db_schemas, # Передаем полученные схемы БД
                            wide_sales_intents_text=wide_sales_intents_string, # <--- ПЕРЕДАЕМ СЮДА
                            on_sale_callback=my_add_to_cart_function
                        )
                        print(f"AI-ассистент: {ai_response_text}")

                        # ai_message_db = ChatMessage(
                        #     session_id=chat_session.id,
                        #     sender='ai',
                        #     message_text=ai_response_text
                        # )
                        # session.add(ai_message_db)
                        # session.commit() 

                    except RuntimeError as e:
                        print(f"AI-ассистент (ошибка): {e}")
                        session.rollback() 
                    except Exception as e:
                        print(f"Неожиданная ошибка: {e}")
                        session.rollback() 

        except Exception as e:
            print(f"Ошибка при инициализации, получении данных из DeepForge или работе с БД: {e}")