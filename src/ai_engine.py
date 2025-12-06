import os
import google.generativeai as genai
from typing import Type, Dict, List, Any
from pydantic import BaseModel

from .db_models import ColumnMappingResult, SqlQueryResult
from .logger import get_logger_with_trace_id

# In a real Cloudflare Worker, these would be set as environment variables or secrets.
# For local development, they can be loaded from a .env file or set directly.
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
AI_GATEWAY_URL = os.environ.get("AI_GATEWAY_URL") # e.g., "https://gateway.ai.cloudflare.com/v1/ACCOUNT_ID/GATEWAY/google-ai-studio"

log = get_logger_with_trace_id(__name__)

class AIEngine:
    """
    A wrapper for the Google Generative AI SDK, configured to route
    requests through the Cloudflare AI Gateway and produce structured,
    Pydantic-validated outputs.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        if not AI_GATEWAY_URL:
            log.warning("AI_GATEWAY_URL not set. Connecting directly to Google AI.")
            # In a real scenario, you might want to raise an error here
            # if the gateway is a hard requirement.
            genai.configure(api_key=GOOGLE_API_KEY)
        else:
            # The Python SDK uses a client_options dictionary to set the api_endpoint
            genai.configure(
                api_key=GOOGLE_API_KEY,
                client_options={"api_endpoint": AI_GATEWAY_URL}
            )
        
        self.model = genai.GenerativeModel(model_name)
        log.info(f"AI Engine initialized for model '{model_name}'")

    def _generate_structured_content(self, prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        """
        Generates content from a prompt and validates it against a Pydantic model.
        """
        log.info(f"Generating structured content for model {response_model.__name__}")
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_model.model_json_schema()
                )
            )
            # The response text is a JSON string that needs to be parsed
            # and then validated by the Pydantic model.
            return response_model.model_validate_json(response.text)
        except Exception as e:
            log.error(f"Failed to generate or validate structured content: {e}", exc_info=True)
            raise

    def map_columns_to_schema(self, raw_columns: List[str], target_model: Type[BaseModel], dataset_id: str) -> ColumnMappingResult:
        """
        Uses AI to map a list of raw column names to the fields of a target Pydantic schema.
        """
        prompt = f"""
        You are a Data Engineering Agent. Your task is to map the raw column names from a source CSV file
        to the fields of a target database schema, which is represented by a Pydantic model.

        Dataset ID: {dataset_id}

        Raw Columns from CSV:
        {raw_columns}

        Target Pydantic Schema:
        {target_model.model_json_schema(indent=2)}

        Instructions:
        1. Analyze the raw column names and the target schema fields.
        2. For each raw column, find the best matching field in the target schema.
        3. The mapping should be based on semantic meaning, not just exact name matches.
        4. If a raw column does not have a clear match, you can map it to `None` or a field you deem appropriate with a justification.
        5. Provide the output in the required JSON format. The 'original' field must be an exact string from the raw columns list.
        """
        return self._generate_structured_content(prompt, ColumnMappingResult)

    def generate_schema_from_models(self, models_module) -> Dict[str, Any]:
        """
        Generates a schema dictionary from a module containing Pydantic models.
        """
        schema = {"tables": []}
        for name, obj in vars(models_module).items():
            if isinstance(obj, type) and issubclass(obj, BaseModel) and name.startswith("Raw"):
                table_name = name  # Or convert to snake_case if needed, but models map to tables usually
                # Actually, Drizzle schema uses specific table names.
                # Assuming the Pydantic model name corresponds to the table name or we use a mapping.
                # For now, let's use the class name as the table name, or better, infer it.
                # In schema.ts, table names are snake_case usually, e.g. raw_hdb_resale_prices.
                # Pydantic model: RawHdbResalePrices.
                # Let's try to convert CamelCase to snake_case for the table name.
                import re
                table_name_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
                
                columns = {}
                for field_name, field in obj.model_fields.items():
                    # Map Pydantic types to SQL types roughly
                    outer_type = field.annotation
                    # Handle Optional[T]
                    if hasattr(outer_type, "__origin__") and outer_type.__origin__ is Optional:
                        type_args = outer_type.__args__
                        if type_args:
                            outer_type = type_args[0]
                    
                    sql_type = "TEXT"
                    if outer_type is int:
                        sql_type = "INTEGER"
                    elif outer_type is float:
                        sql_type = "REAL"
                    elif outer_type is bool:
                        sql_type = "BOOLEAN"
                    
                    columns[field_name] = sql_type

                schema["tables"].append({
                    "name": table_name_snake,
                    "columns": columns
                })
        return schema

    def get_sql_from_natural_language(self, user_query: str, table_schema: Dict[str, Any]) -> SqlQueryResult:
        """
        Converts a natural language user query into a D1-compatible SQL query.
        """
        prompt = f"""
        You are a SQL generation agent. Your task is to convert a user's question in plain English
        into a valid SQL query that can be executed on a Cloudflare D1 database (SQLite).

        User's Question:
        "{user_query}"

        Table Schema:
        {json.dumps(table_schema, indent=2)}

        Instructions:
        1. Analyze the user's question and the provided table schema.
        2. Generate a D1-compatible SQL query that answers the user's question.
        3. Pay attention to column names and data types in the schema.
        4. Provide a brief, clear explanation of the generated SQL query.
        5. Return the result in the required JSON format.
        """
        return self._generate_structured_content(prompt, SqlQueryResult)

if __name__ == '__main__':
    # Example Usage (requires GOOGLE_API_KEY to be set in the environment)
    
    # Mock Pydantic model for demonstration
    class MockHdbResale(BaseModel):
        town: str
        flat_type: str
        resale_price: float
        transaction_date: str

    # 1. Initialize the engine
    ai_engine = AIEngine()

    # 2. Example: Map Columns
    raw_cols = ["TOWN", "flat type", "price", "date of sale"]
    try:
        mapping_result = ai_engine.map_columns_to_schema(raw_cols, MockHdbResale, "hdb-resale-mock")
        print("--- Column Mapping Result ---")
        print(mapping_result.model_dump_json(indent=2))
    except Exception as e:
        print(f"An error occurred during column mapping: {e}")

    # 3. Example: Text-to-SQL
    schema = {
        "name": "rawHdbResalePrices",
        "columns": {
            "town": "TEXT",
            "flatType": "TEXT",
            "resalePrice": "REAL",
            "year": "INTEGER"
        }
    }
    query = "Show me the average resale price for 4-room flats in Bedok for the year 2023"
    try:
        sql_result = ai_engine.get_sql_from_natural_language(query, schema)
        print("\n--- Text-to-SQL Result ---")
        print(sql_result.model_dump_json(indent=2))
    except Exception as e:
        print(f"An error occurred during SQL generation: {e}")
