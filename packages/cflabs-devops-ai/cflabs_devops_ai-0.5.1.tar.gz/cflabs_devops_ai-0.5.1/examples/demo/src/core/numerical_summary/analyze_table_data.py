from typing import List, Dict, Any
from src.utils.logger import get_logger, time_function, log_function_call
from openai import OpenAI
import pandas as pd
from sqlalchemy import inspect, text
from src.models.file_model import FileModel
import traceback

logger = get_logger("AnalyzeTableData")

class AnalyzeTableData:
    def __init__(self, openai_client: OpenAI, database_name: str):
        self.openai_client = openai_client
        self.database_name = database_name

    @time_function
    @log_function_call
    def get_table_data(self) -> List[FileModel]:
        """
        Get all available tables from the database for the specified database name.
        """
        try:
            from src.database import get_db_session
            from src.models.file_model import FileModel, FileStatusEnum
            from sqlalchemy import and_
            
            # Get database session
            db_session = next(get_db_session())
            
            # Get all files from the database with proper filtering
            logger.info(f"Getting all files from the database: {self.database_name}")
            files = db_session.query(FileModel).filter(
                and_(
                    FileModel.ingested_db_name == self.database_name,
                    FileModel.status == FileStatusEnum.AVAILABLE,
                    FileModel.ingested_table_name.isnot(None)
                )
            ).all()
            logger.info(f"Found {len(files)} available files in the database: {self.database_name}")
            
            if not files:
                logger.warning(f"No available files found in database: {self.database_name}")
                return []

            return files
            
        except Exception as e:
            logger.error(f"Error in getting tables from the database: {e}")
            return []

    @time_function
    @log_function_call
    def get_table_data_and_description(self, table: FileModel, db_session, num_rows: int = 10) -> Dict[str, Any]:
        """
        Get table data and column descriptions using FileModel and database connection.
        """
        try:
            from sqlalchemy import text, inspect
            from src.database import engine
            
            table_name = table.ingested_table_name
            database_name = self.database_name
            
            logger.info(f"Getting data and description for table: {table_name} in database: {database_name}")
            
            # Get table schema information using database name as schema
            inspector = inspect(engine)
            
            # Try to get columns with schema first
            try:
                columns_info = inspector.get_columns(table_name, schema=database_name)
                logger.info(f"Found table {table_name} in schema {database_name}")
            except Exception as schema_error:
                logger.warning(f"Could not find table {table_name} in schema {database_name}, trying without schema: {schema_error}")
                # Fallback: try without schema
                try:
                    columns_info = inspector.get_columns(table_name)
                    logger.info(f"Found table {table_name} without schema")
                except Exception as no_schema_error:
                    logger.error(f"Could not find table {table_name} in any schema: {no_schema_error}")
                    return None
            
            # Create column descriptions
            column_info = {}
            for col in columns_info:
                column_info[col['name']] = {
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True),
                    'default': col.get('default', None),
                    'primary_key': col.get('primary_key', False),
                    'autoincrement': col.get('autoincrement', False)
                }
            
            # Get sample data (limit to 1000 rows for performance)
            # Use fully qualified table name if schema is available
            try:
                if database_name:
                    query = text(f"SELECT * FROM {database_name}.{table_name} LIMIT {num_rows}")
                    logger.info(f"Executing query: SELECT * FROM {database_name}.{table_name} LIMIT {num_rows}")
                else:
                    query = text(f"SELECT * FROM {table_name} LIMIT {num_rows}")
                    logger.info(f"Executing query: SELECT * FROM {table_name} LIMIT {num_rows}")
                    
                result = db_session.execute(query)
                
                # Convert to pandas DataFrame
                df = pd.DataFrame(result.fetchall())
                if not df.empty:
                    df.columns = result.keys()
                    logger.info(f"Retrieved {len(df)} rows and {len(df.columns)} columns from table {table_name}")
                else:
                    logger.warning(f"Table {table_name} returned empty result set")
                    
            except Exception as query_error:
                logger.error(f"Error executing query for table {table_name}: {query_error}")
                # Try alternative approach without schema
                try:
                    query = text(f"SELECT * FROM {table_name} LIMIT {num_rows}")
                    logger.info(f"Trying alternative query: SELECT * FROM {table_name} LIMIT {num_rows}")
                    result = db_session.execute(query)
                    df = pd.DataFrame(result.fetchall())
                    if not df.empty:
                        df.columns = result.keys()
                        logger.info(f"Retrieved {len(df)} rows using alternative query")
                    else:
                        logger.warning(f"Alternative query for table {table_name} returned empty result set")
                except Exception as alt_query_error:
                    logger.error(f"Alternative query also failed for table {table_name}: {alt_query_error}")
                    return None
            
            return {
                'data': df,
                'columns': column_info,
                'total_columns': len(columns_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting table data and description for {table.ingested_table_name}: {traceback.format_exc()}")
            return None

    @time_function
    @log_function_call
    def analyze_table_data(self, table: FileModel, kpis: List[str]) -> Dict[str, Any]:
        """
        Analyze a single table and extract KPI-related data.
        input: table: FileModel, kpis: List[str]
        output: Dict[str, Any]
        """
        try:
            logger.info(f"Analyzing table: {table.ingested_table_name}")
            
            # Get database session
            from src.database import get_db_session
            db_session = next(get_db_session())
            
            # Get table data using the ingested table name from FileModel
            if not table.ingested_table_name:
                logger.error(f"No ingested table name found for file: {table.name}")
                return None
                
            # Get table schema and data
            table_data = self.get_table_data_and_description(table, db_session, num_rows=10)
            if not table_data:
                logger.error(f"Could not retrieve data for table: {table.ingested_table_name}")
                return None
                
            df = table_data['data']
            column_info = table_data['columns']
            
            if df.empty:
                logger.warning(f"Table {table.ingested_table_name} is empty")
                return None
            
            # Calculate basic statistics
            numerical_stats = {}
            numerical_columns = df.select_dtypes(include=['number']).columns
            
            for col in numerical_columns:
                numerical_stats[col] = {
                    'count': int(df[col].count()),
                    'mean': float(df[col].mean()) if df[col].dtype != 'object' else None,
                    'std': float(df[col].std()) if df[col].dtype != 'object' else None,
                    'min': float(df[col].min()) if df[col].dtype != 'object' else None,
                    'max': float(df[col].max()) if df[col].dtype != 'object' else None,
                    'sum': float(df[col].sum()) if df[col].dtype != 'object' else None
                }
            
            # Get column names for AI analysis
            column_names = list(df.columns)
            
            # Analyze the table using AI to figure out which KPIs are present in the table
            table_summary = self.analyze_table_data_with_ai(table.ingested_table_name, column_names, kpis)
            if table_summary is None or table_summary == "not_present":
                logger.warning(f"No table summary found for table: {table.ingested_table_name}")
                return None
                
            # Combine all analysis results
            result = {
                'table_name': table.ingested_table_name,
                'file_info': {
                    'luid': table.luid,
                    'original_filename': table.original_filename,
                    'name': table.name,
                    'size_bytes': table.size_bytes,
                    'project_id': table.project_id
                },
                'column_info': column_info,
                'numerical_stats': numerical_stats,
                'row_count': len(df),
                'column_count': len(df.columns),
                'ai_analysis': table_summary
            }
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing table {table.ingested_table_name}: {e}")
            return None
    
    @time_function
    @log_function_call
    def analyze_table_data_with_ai(self, table_name: str, column_names: List[str], kpis: List[str]) -> Dict[str, Any]:
        """
        Analyze a single table and extract KPI-related data using AI.
        """
        try:
            import json
            
            # System prompt for table analysis
            system_prompt = """You are a data analyst that summarizes database tables.

## Your task  
You receive:    
1. **Table Name** - the name of the table
2. **Columns** - the columns in the table
3. **Expected KPIs** - the KPIs to analyze

## Instructions
1. Analyze the table and figure out which of the Expected KPIs can be calculated from the table.
2. If you find any new KPIs that are not in the Expected KPIs, add them to the Expected KPIs and add them in the KPIs section of the output.
3. If none of the KPIs are present in the table, return "not_present"
4. Provide a brief description of what the table contains

## Output Format
Return ONLY a valid JSON object in the following format:
```json
{
    "table_name": "table1",
    "description": "Brief description of the table content",
    "kpis": [
        {"kpi": "kpi1", "column": "column1", "description": "What this KPI measures"},
        {"kpi": "kpi2", "column": "column2", "description": "What this KPI measures"}
    ]
}
```

If no KPIs are found, return:
```json
{
    "table_name": "table1",
    "description": "Brief description of the table content",
    "kpis": "not_present"
}
```"""

            # User prompt
            user_prompt = f"""Table Name: {table_name}
Columns: {', '.join(column_names)}
Expected KPIs: {', '.join(kpis)}

Please analyze this table and identify which KPIs can be calculated from the available columns."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.3,
                timeout=60
            )
            
            response_content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response - handle markdown code blocks
            try:
                # First, try to parse as-is
                return json.loads(response_content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in code block for table {table_name}: {json_match.group(1)}")
                
                # Try to find JSON object without code blocks
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON object found for table {table_name}: {json_match.group(0)}")
                
                logger.warning(f"Could not parse JSON response from AI for table {table_name}: {response_content}")
                # Return a fallback response
                return {
                    "table_name": table_name,
                    "description": "Table analysis failed",
                    "kpis": "not_present"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return None