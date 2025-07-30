from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pytz import timezone
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
import sys
import time
import json
import os
import logging
import re
import pandas as pd
from .utils import (
    execute_run_databricks,
    execute_run_postgres,
    DbConnections
)

class RuleManager:
    def __init__(
        self,
        *,
        spark: Optional[SparkSession] = None,
        dbutils=None,
        http_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        self.spark = spark
        self.dbutils = dbutils
        self.http_path = http_path

        self.server_hostname = (
            spark.conf.get("spark.databricks.workspaceUrl")
            if spark else None
        )

        self.access_token = (
            dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            if dbutils else None
        )

        self.databricks_client = WorkspaceClient()

        self.config: Dict[str, Any] = {}
        self.template: Dict[str, Any] = {}
        self.rules: Dict[str, List[Dict[str, Any]]] = {}
        self.execution_id: Optional[int] = None
        self.job_start_time: Optional[float] = None

        if base_dir:
            self.base_dir = base_dir
        elif os.getenv("BRV_BASE_DIR"):
            self.base_dir = os.getenv("BRV_BASE_DIR")
        else:
            self.base_dir = os.getcwd()
    
    def resolve_relative_path(self, raw_path: str) -> str:
        """
        Resolves a given relative or absolute file path using the base_dir.
        """
        raw_path = raw_path.strip().lstrip("/\\")
        return os.path.abspath(os.path.join(self.base_dir, raw_path))

    def load_config(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def split_config_object(self):
        if 'RULES' in self.config:
            self.template = {k: v for k, v in self.config.items() if k != 'RULES'}
            self.rules = {'RULES': self.config['RULES']}
            return self.template, self.rules
        else:
            self.logger.warning("Array 'RULES' not found in rule object.")
            return self.template, None

    def run_exe(self, s: str) -> int:
        # Use consistent hashing and ensure non-negative number
        return abs(hash(s)) % (sys.maxsize + 1)

    def init_other_variables(self):
        # Use UTC date to avoid timezone issues
        hash_string = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d%H%M%S")
        self.execution_id = self.run_exe(hash_string)
        self.job_start_time = time.time()

    def set_system_variables(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        self.init_other_variables()
        hash_string = f"{rule['TEAM_NAME']}{rule['DOMAIN_NAME']}{rule['RULE_CATEGORY_NAME']}{rule['RULE_ID']}"
        unique_rule_identifier = self.run_exe(hash_string)
        rule['EXECUTION_ID'] = self.execution_id
        rule['UNIQUE_RULE_IDENTIFIER'] = unique_rule_identifier
        rule['UNIQUE_TIMESTAMP'] = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return rule

    def get_file_text(self, file_path: str, is_local: bool = False) -> str:
        """Read file content from local filesystem or Databricks workspace.
        
        Args:
            file_path: Path to the file
            is_local: Whether the file is local or in Databricks workspace
            
        Returns:
            str: File contents
            
        Raises:
            FileNotFoundError: If local file not found
            Exception: For other errors
        """
        if is_local:
            try:
                # First, try to find SQL templates in the package directory
                package_dir = os.path.dirname(os.path.abspath(__file__))
                possible_paths = [
                    os.path.join(package_dir, 'sql_templates', file_path),  # Package sql_templates
                    os.path.join(os.getcwd(), 'sql_templates', file_path),  # Current directory sql_templates
                    os.path.join(self.base_dir, 'sql_templates', file_path),  # Base directory sql_templates
                ]

                # Add user-specified templates path if available
                if hasattr(self, 'sql_templates_path'):
                    possible_paths.insert(0, os.path.join(self.sql_templates_path, file_path))

                for path in possible_paths:
                    if os.path.exists(path):
                        full_path = path
                        break
                else:
                    raise FileNotFoundError(f"SQL template not found: {file_path}")

                self.logger.info(f"Reading local file: {full_path}")
                try:
                    with open(full_path, 'r', encoding='utf-8') as file:
                        return file.read()
                except UnicodeDecodeError:
                    self.logger.warning(f"UTF-8 decoding failed, retrying with latin-1 for file: {full_path}")
                    with open(full_path, 'r', encoding='latin-1') as file:
                        return file.read()

            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {str(e)}")
                raise
        else:
            # Download file content from Databricks workspace
            try:
                with self.databricks_client.workspace.download(file_path) as f:
                    return f.read().decode("utf-8")
            except Exception as e:
                self.logger.error(f"Error downloading from Databricks: {str(e)}")
                raise

    def set_dynamic_context_values(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process RULE_DYNAMIC_CONTEXT to load dynamic key-value pairs from SQL file.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with dynamic context values
        """
        dynamic_context_path = rule.get('RULE_DYNAMIC_CONTEXT')
        
        if not dynamic_context_path:
            print("DEBUG: No RULE_DYNAMIC_CONTEXT found in rule")
            self.logger.debug("No RULE_DYNAMIC_CONTEXT found in rule, skipping dynamic context processing")
            return rule
            
        try:
            print(f"DEBUG: Found RULE_DYNAMIC_CONTEXT: {dynamic_context_path}")
            self.logger.info(f"Processing dynamic context from: {dynamic_context_path}")
            
            # Remove leading slash if present and normalize path
            if dynamic_context_path.startswith('/'):
                dynamic_context_path = dynamic_context_path[1:]
            
            print(f"DEBUG: Normalized path: {dynamic_context_path}")
            
            # Get SQL content from the context file
            context_sql = self.get_file_text(dynamic_context_path, is_local=True)
            context_sql = context_sql.replace(';', '').strip()
            
            print(f"DEBUG: Context SQL loaded: {context_sql[:100]}...")  # First 100 chars
            self.logger.info(f"Executing dynamic context SQL: {context_sql}")
            
            # Execute SQL based on engine type
            engine_type = rule.get('ENGINE_TYPE', '').lower()
            print(f"DEBUG: Engine type: {engine_type}")
            
            if engine_type == 'databricks':
                result = execute_run_databricks(context_sql, True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            elif engine_type == 'postgres':
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()
                result = execute_run_postgres(context_sql, engine, True)
            else:
                raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")
            
            print(f"DEBUG: SQL execution result: {result}")
            
            # Convert result to DataFrame for easier processing
            if isinstance(result, list) and result and isinstance(result[0], list):
                raw_result = result[0]

                if len(raw_result) >= 2:
                    columns = raw_result[0]        # First item is header: ('value', 'key')
                    rows = raw_result[1:]          # Remaining are actual rows
                    context_df = pd.DataFrame(rows, columns=columns)
                else:
                    print("DEBUG: No rows returned in dynamic SQL.")
                    self.logger.warning("No data rows found in dynamic context SQL result.")
                    return rule
            else:
                print("DEBUG: Unexpected format from execute_run_postgres:", result)
                self.logger.error("Unexpected result format from execute_run_postgres")
                return rule
            
            print(f"DEBUG: DataFrame shape: {context_df.shape}")
            print(f"DEBUG: DataFrame columns: {list(context_df.columns)}")
            print(f"DEBUG: DataFrame head:\n{context_df.head()}")
            
            if context_df.empty:
                print("DEBUG: Context DataFrame is empty!")
                self.logger.warning("Dynamic context query returned no results")
                return rule
            
            # Ensure we have the expected columns (value, key)
            if 'value' not in context_df.columns or 'key' not in context_df.columns:
                print(f"DEBUG: Missing required columns. Available: {list(context_df.columns)}")
                self.logger.error("Dynamic context query must return 'value' and 'key' columns")
                return rule
            
            # Process each row and add dynamic values to rule
            dynamic_values_added = 0
            print("DEBUG: Processing context values...")
            
            for idx, row in context_df.iterrows():
                key = str(row['key']).strip()
                value = str(row['value']).strip()
                
                print(f"DEBUG: Row {idx}: key='{key}', value='{value}'")
                
                if key and value:
                    # Add the key-value pair to the rule
                    rule[key] = value
                    dynamic_values_added += 1
                    print(f"DEBUG: Successfully added: {key} = {value}")
                    self.logger.info(f"Added dynamic context: {key} = {value}")
            
            print(f"DEBUG: Total dynamic values added: {dynamic_values_added}")
            self.logger.info(f"Successfully added {dynamic_values_added} dynamic context values to rule")
            
                        
        except FileNotFoundError as e:
            print(f"DEBUG: File not found error: {str(e)}")
            self.logger.error(f"Dynamic context file not found: {dynamic_context_path}. Error: {str(e)}")
        except Exception as e:
            print(f"DEBUG: General error: {str(e)}")
            self.logger.error(f"Error processing dynamic context: {str(e)}")
            # Don't raise the exception to allow rule processing to continue
        
        return rule
    
    def format_sql_result(self,sql_result):
        if not sql_result:
            return {"info": "No result (DDL/DML executed successfully)"}

        headers = sql_result[0]  # first tuple is header
        data_rows = sql_result[1:]  # rest are data

        # Convert each data row tuple to dict using headers
        formatted = [dict(zip(headers, row)) for row in data_rows]
        return formatted
        
    
    def set_custom_template(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Add SQL template paths to the rule based on engine type.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with SQL template paths and formatted SQL results
        """
        custom_template_path = rule.get('SQL_TEMPLATE_PATH') or rule.get('JOB_SCRIPTS', '')
        if not custom_template_path:
            print("DEBUG: No SQL_TEMPLATE_PATH found in rule")
            self.logger.debug("No SQL_TEMPLATE_PATH found in rule, skipping adding SQL template")
            return rule

        try:
            print(f"DEBUG: Found SQL_TEMPLATE_PATH: {custom_template_path}")
            self.logger.info(f"Processing SQL template from: {custom_template_path}")
            
            # Remove leading slash if present and normalize path
            if custom_template_path.startswith('/'):
                custom_template_path = custom_template_path[1:]

            print(f"DEBUG: Normalized path: {custom_template_path}")

            # Read the SQL content from the file
            template_sql_content = self.get_file_text(self.resolve_relative_path(custom_template_path), is_local=True)
            template_sql_content = template_sql_content.strip()

            # Store the SQL CONTENT, not the file path
            if 'CODE_SNIPPETS' in rule:
                print("DEBUG: Found CODE_SNIPPETS in rule, injecting snippets into template")
                self.logger.info("Injecting code snippets into SQL template")
                template_sql_content = self.inject_snippets_into_template(rule, template_sql_content)
                rule['CUSTOM_TEMPLATE_SQL'] = template_sql_content
            else:
                print("DEBUG: No CODE_SNIPPETS found in rule, using raw template SQL")
                self.logger.info("Using raw SQL template without snippets")
                rule['CUSTOM_TEMPLATE_SQL'] = template_sql_content

            print(f"DEBUG: SQL content loaded: {template_sql_content[:100]}...")  # First 100 chars
            self.logger.info(f"Executing SQL Template: {template_sql_content}")

            # Check if SQL content is empty
            if not template_sql_content:
                print("DEBUG: Template SQL content is empty")
                self.logger.warning("SQL template content is empty, skipping execution")
                return rule

        except FileNotFoundError as e:
            print(f"DEBUG: File not found error: {str(e)}")
            self.logger.error(f"SQL template file not found: {custom_template_path}. Error: {str(e)}")
        except Exception as e:
            print(f"DEBUG: General error: {str(e)}")
            self.logger.error(f"Error processing SQL template: {str(e)}")    
        
        return rule


    def set_business_rule_check_templates(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Load SQL templates based on engine type.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with SQL templates
        """
        engine_type = rule.get('ENGINE_TYPE', '').lower()
        
        # First try package sql_templates directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(package_dir, 'sql_templates')
        
        if engine_type == 'databricks':
            paths = {
                'bookmark_sql_text': os.path.join('common', 'bookmark_select.sql'),
                'result_sql_txt': os.path.join('business_rule_check', 'result.sql'),
                'update_bookmark_sql_text': os.path.join('common', 'bookmark_update.sql'),
                'unique_rule_mapping_sql': os.path.join('common', 'unique_rule_mapping.sql'),
            }
        elif engine_type == 'postgres':
            paths = {
                'bookmark_sql_text': os.path.join('common', 'bookmark_select_postgres.sql'),
                'result_sql_txt': os.path.join('business_rule_check', 'result_postgres.sql'),
                'update_bookmark_sql_text': os.path.join('common', 'bookmark_update_postgres.sql'),
                'unique_rule_mapping_sql': os.path.join('common', 'unique_rule_mapping_postgres.sql'),
            }
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        for key, path in paths.items():
            rule[key] = self.get_file_text(path, is_local=True)

        return rule

    def set_bookmark_value(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        try:
            rule['BOOKMARK_COLUMN'] = rule.get('BOOKMARK_COLUMN', 'TEMP_COL_FOR_BOOKMARK')
            rule['BOOKMARK_START_DATE'] = rule.get('DEFAULT_BOOKMARK_START_DATE', '1970-01-01')
            self.logger.info(f"Default bookmark start date: {rule['BOOKMARK_START_DATE']}")

            if rule['BOOKMARK_COLUMN'] == 'TEMP_COL_FOR_BOOKMARK':
                return self._handle_temp_bookmark(rule)

            return self._handle_actual_bookmark(rule)

        except Exception as e:
            self.logger.error(f"Error setting bookmark value: {str(e)}")
            raise

    def _handle_temp_bookmark(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule.update({
            'SKIP_BOOKMARKING': True,
            'NEED_BOOKMARK_UPDATE': False,
            'BOOKMARK_END_DATE': '2099-01-01'
        })
        return rule

    def _handle_actual_bookmark(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule.update({
            'SKIP_BOOKMARKING': False,
            'NEED_BOOKMARK_UPDATE': True,
            'BOOKMARK_END_DATE': rule.get('BOOKMARK_END_DATE', rule['BOOKMARK_START_DATE'])
        })

        if 'bookmark_sql_text' not in rule:
            return rule

        return self._process_bookmark_sql(rule)

    def _process_bookmark_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule['bookmark_sql_text'] = self.replace_common_variables(rule['bookmark_sql_text'], rule)
        engine_type = rule.get('ENGINE_TYPE', '').lower()

        if engine_type == 'databricks':
            result = execute_run_databricks(rule['bookmark_sql_text'], True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(rule['bookmark_sql_text'], engine, True)
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        # Expecting result to be list with at least two elements (date range)
        if isinstance(result, list) and len(result) > 1 and len(result[1]) > 1:
            rule['BOOKMARK_START_DATE'] = result[1][0]
            rule['BOOKMARK_END_DATE'] = result[1][1]
            if rule['BOOKMARK_END_DATE'] < rule['BOOKMARK_START_DATE']:
                rule['BOOKMARK_END_DATE'] = rule['BOOKMARK_START_DATE']
        else:
            rule['BOOKMARK_END_DATE'] = (datetime.now(timezone('UTC')) - timedelta(days=1)).date().isoformat()

        return rule

    def get_dataframe(self, result: Any) -> pd.DataFrame:
        df = pd.DataFrame()
        if result:
            result_df = pd.DataFrame(result)
            if len(result_df) > 0:
                df_header = result_df.iloc[0]
                result_df = result_df[1:]
                result_df.columns = df_header
                df = result_df.reset_index(drop=True)
        return df

    def process_fail_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        fail_sql_path = rule.get('FAIL_SQL')
        
        if not fail_sql_path:
            rule['STATUS'] = True
            rule['FAIL_RECORD_COUNT'] = 0
            rule['FAILED_KEYS'] = ''
            return rule

        rule['STATUS'] = False
        fail_sql_path = os.path.normpath(os.path.join(self.base_dir, fail_sql_path))
        self.logger.info(f"Reading fail SQL file from: {fail_sql_path}")

        try:
            rule['FAILED_QUERY'] = self.get_file_text(str(fail_sql_path), is_local=True).replace(';', '')
        except Exception as e:
            self.logger.error(f"Error reading fail SQL file: {e}")
            rule['FAILED_QUERY'] = ''
            rule['FAIL_RECORD_COUNT'] = 0
            rule['FAILED_KEYS'] = ''
            return rule

        pass_sql_path = rule.get('PASS_SQL', '')
        if pass_sql_path:
            pass_sql_path = os.path.normpath(os.path.join(self.base_dir, pass_sql_path))
            try:
                rule['PASS_QUERY'] = self.get_file_text(str(pass_sql_path), is_local=True).replace(';', '')
            except Exception as e:
                self.logger.error(f"Error reading pass SQL file: {e}")
                rule['PASS_QUERY'] = ''
        else:
            rule['PASS_QUERY'] = ''

        rule['FAILED_QUERY'] = self.replace_common_variables(rule['FAILED_QUERY'], rule)

        engine_type = rule.get('ENGINE_TYPE', '').lower()
        if engine_type == 'databricks':
            fail_df_result = execute_run_databricks(rule['FAILED_QUERY'], True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            fail_df_result = execute_run_postgres(rule['FAILED_QUERY'], engine, True)
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        fail_df = self.get_dataframe(fail_df_result)
        fail_df_count = fail_df.shape[0]
        rule['FAIL_RECORD_COUNT'] = fail_df_count

        if rule['FAIL_RECORD_COUNT'] == 0 and rule['PASS_QUERY'] == '':
            rule['STATUS'] = True

        try:
            fail_df_keys = fail_df.head(10).to_json(orient="records")
            fail_df_keys_parsed = json.loads(fail_df_keys)
            rule['FAILED_KEYS'] = json.dumps(fail_df_keys_parsed, indent=4)
        except Exception as e:
            self.logger.error(f"Error converting failed keys to JSON: {e}")
            rule['FAILED_KEYS'] = '{}'

        return rule
    
    def process_pass_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        if rule['PASS_QUERY'] != '':
            engine_type = rule.get('ENGINE_TYPE', '').lower()
            if engine_type == 'databricks':
                pass_df_result = execute_run_databricks(rule['PASS_QUERY'], True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            else:
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()
                pass_df_result = execute_run_postgres(rule['PASS_QUERY'], engine, True)
                
            pass_df = self.get_dataframe(pass_df_result)
            pass_df_count = pass_df.shape[0]
            rule['PASS_RECORD_COUNT'] = pass_df_count
                
            if (rule['PASS_RECORD_COUNT'] + rule['FAIL_RECORD_COUNT']) == 0:
                rule['PASS_PERCENTAGE'] = 0
            else:
                rule['PASS_PERCENTAGE'] = round(
                    (rule['PASS_RECORD_COUNT'] / (rule['PASS_RECORD_COUNT'] + rule['FAIL_RECORD_COUNT'])) * 100, 2
                )
                
            if int(rule['PASS_PERCENTAGE']) >= int(rule['PASS_THRESHOLD']):
                rule['STATUS'] = True
                rule['REMARKS'] = 'Percentage of records passed test is {}. Threshold: {}.'.format(
                    rule['PASS_PERCENTAGE'], rule['PASS_THRESHOLD']
                )
            elif rule['PASS_PERCENTAGE'] == 0:
                rule['REMARKS'] = 'Both passed records count and failed records count are zero'
            else:
                rule['REMARKS'] = 'Percentage of records passed test is {}. Threshold: {}. Some failed keys are: {}'.format(
                    rule['PASS_PERCENTAGE'], rule['PASS_THRESHOLD'], rule['FAILED_KEYS']
                )
        elif not rule['STATUS']:
            rule['PASS_PERCENTAGE'] = 100
            rule['PASS_RECORD_COUNT'] = 0
            rule['REMARKS'] = '{} number of records failed the test. Some failed keys are: {}'.format(
                rule['FAIL_RECORD_COUNT'], rule['FAILED_KEYS']
            )
        else:
            rule['PASS_PERCENTAGE'] = 100
            rule['PASS_RECORD_COUNT'] = 0
            rule['REMARKS'] = 'No record has failed the test'
        
        return rule

    def replace_common_variables(self,sql_str, rule):
        """
        Replaces placeholders in sql_str with corresponding values from the rule dictionary.
        Any placeholder in the format <PLACEHOLDER_NAME> will be dynamically replaced.
        """
        final_sql = sql_str
        for key, value in rule.items():
            placeholder = f'<{key}>'
            final_sql = final_sql.replace(placeholder, str(value))
        return final_sql


    def set_business_rule_check_final_queries(self, rule: dict) -> dict:
        rule['unique_rule_mapping_sql'] = self.replace_common_variables(rule.get('unique_rule_mapping_sql', ''), rule)
        rule['result_sql_txt'] = self.replace_common_variables(rule.get('result_sql_txt', ''), rule)
        rule['update_bookmark_sql_text'] = self.replace_common_variables(rule.get('update_bookmark_sql_text', ''), rule)
        return rule

    def set_custom_template_queries(self, rule: dict) -> dict:
        #rule['SNIPPET_SQL'] = rule.get('SNIPPET_SQL', '')
        rule['CUSTOM_TEMPLATE_SQL'] = self.replace_common_variables(rule.get('CUSTOM_TEMPLATE_SQL', ''), rule)
        
        return rule


    def extract_snippet_blocks(self, sql_text: str) -> Dict[str, str]:
        """
        Extracts SQL code blocks from a snippet file using markers like:
            #START <TAG>
            ...SQL code...
            #END <TAG>
        Returns a dict: { "TAG": "…sql code…" }
        """
        pattern = r"#START\s+(#EXEC\s+)?<(?P<tag>[^>]+)>\s*(?P<code>.*?)#END\s+<\2>"
        #pattern = r"#START\s+<(?P<tag>[^>]+)>\s*(?P<code>.*?)#END\s+<\1>"
        matches = re.finditer(pattern, sql_text, re.DOTALL | re.IGNORECASE)
        blocks = {}
        for match in matches:
            exec_flag = bool(match.group(1))
            tag = match.group("tag").strip()
            code = match.group("code").strip()
            blocks[tag] = {"code": code, "exec": exec_flag}
        return blocks

    def execute_sql_scalar(self, sql_text: str, engine_type: str) -> Any:
        """
        Runs the given SQL as a scalar query and returns the first cell.
        Handles Databricks or Postgres.
        """
        engine_type = engine_type.lower()

        if engine_type == "databricks":
            # Databricks: must return rows
            result = execute_run_databricks(sql_text, retrieve_result=True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            # Expecting: [ [ (col_names), row1, row2, ... ] ]
            if result and isinstance(result, list) and len(result) > 0:
                rows = result[0][1:]  # skip header
                if rows:
                    return rows[0][0]
            return None

        else:
            # Postgres: use your helper
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(sql_text, engine, retrieve_result=True)
            if result and isinstance(result, list) and len(result) > 0:
                rows = result[0][1:]  # skip header
                if rows:
                    return rows[0][0]
            return None



    def assign_snippet_blocks_to_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assigns values from SQL snippet blocks into the rule dictionary.
        For example:
            #START <SCHEMA>
            seacomp
            #END <SCHEMA>
        becomes rule["SCHEMA"] = "seacomp"

        Args:
            rule: Rule dictionary containing CODE_SNIPPETS.

        Returns:
            Updated rule with direct assignments from snippet blocks.
        """
        snippet_blocks = {}
        engine_type = rule.get("ENGINE_TYPE", "postgres")

        # Safely get and sort CODE_SNIPPETS
        snippets = sorted(rule.get("CODE_SNIPPETS", []), key=lambda x: x.get("order", 0))

        for snippet_info in snippets:
            path = snippet_info.get("path")
            if not path:
                continue
            try:
                resolved_path = self.resolve_relative_path(path)
                with open(resolved_path, 'r') as f:
                    sql_text = f.read()
                    blocks = self.extract_snippet_blocks(sql_text)
                    for tag, block_info in blocks.items():
                        if block_info["exec"]:
                            sql_to_run = self.replace_common_variables(block_info["code"], rule)
                            result = self.execute_sql_scalar(sql_to_run, engine_type)
                            snippet_blocks[tag] = result.strip() if isinstance(result, str) else (str(result).strip() if result else "")
                        else:
                            snippet_blocks[tag] = block_info["code"] 
                   
            except FileNotFoundError:
                print(f"DEBUG: Snippet file not found: {path} -- Skipping.")
                self.logger.warning(f"Snippet file not found: {path} -- Skipping.")

        # Update rule with block values
        rule.update(snippet_blocks)
        return rule


    def inject_snippets_into_template(self, rule: Dict[str, Any], template_sql: str) -> str:
        """
        Replaces placeholders in template_sql with snippets defined in rule["CODE_SNIPPETS"].
        Placeholders are:
        - #START <TAG>...#END <TAG>
        - or <TAG>
        """
        snippet_blocks = {}

        # Sort snippets by 'order'
        snippets = sorted(rule.get("CODE_SNIPPETS", []), key=lambda x: x["order"])

        for snippet_info in snippets:
            path = snippet_info["path"]
            try:
                resolved_path = self.resolve_relative_path(path)
                with open(resolved_path, 'r') as f:
                    sql_text = f.read()
                    blocks = self.extract_snippet_blocks(sql_text)
                    snippet_blocks.update(blocks)
            except FileNotFoundError as e:
                print(f"Snippet file not found: {path} -- Skipping.")

        # Replace placeholders in template_sql
        for tag, block_info in snippet_blocks.items():
            code = block_info["code"] 

            # Replace full block if exists
            block_pattern = rf"#START <{tag}>.*?#END <{tag}>"
            if re.search(block_pattern, template_sql, re.DOTALL):
                template_sql = re.sub(block_pattern, code, template_sql, flags=re.DOTALL)
            else:
                # Replace tag placeholder like <TAG>
                template_sql = template_sql.replace(f"<{tag}>", code)

        return template_sql

   
    def exec_business_rule_check_final_queries(self, rule):
        """Execute final SQL queries based on engine type (databricks or postgres)."""
        print("Executing final queries")
        engine_type = rule.get("ENGINE_TYPE").lower()
        print("exec_business_rule_check_final_queries", engine_type)
        
        try:
            def clean_sql(sql):
                if not sql:
                    return ""
                # Remove trailing semicolons, quotes, commas and normalize whitespace
                cleaned = sql.strip().rstrip(';').rstrip("'").rstrip(",").strip()
                return cleaned

            # Clean all SQL queries
            rule["unique_rule_mapping_sql"] = clean_sql(rule.get("unique_rule_mapping_sql", ""))
            rule["result_sql_txt"] = clean_sql(rule.get("result_sql_txt", ""))
            rule["update_bookmark_sql_text"] = clean_sql(rule.get("update_bookmark_sql_text", ""))

            if engine_type == 'databricks':
                print("Running Databricks...")
                execute_run_databricks(rule["unique_rule_mapping_sql"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
                execute_run_databricks(rule["result_sql_txt"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
                if rule.get('NEED_BOOKMARK_UPDATE', False):
                    execute_run_databricks(rule["update_bookmark_sql_text"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)

            else:  # Assume Postgres
                print("Running Postgres...")
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()

                try:
                    execute_run_postgres(rule["unique_rule_mapping_sql"], engine, False)
                except Exception as e:
                    print(f"Error executing unique_rule_mapping_sql: {str(e)}")

                try:
                    execute_run_postgres(rule["result_sql_txt"], engine, False)
                except Exception as e:
                    print(f"Error executing result_sql_txt: {str(e)}")

                if rule.get('NEED_BOOKMARK_UPDATE', False):
                    try:
                        execute_run_postgres(rule["update_bookmark_sql_text"], engine, False)
                    except Exception as e:
                        print(f"Error executing update_bookmark_sql_text: {str(e)}")

        except Exception as e:
            print(f"Error executing final queries: {str(e)}")
            raise

        return rule

    def exec_custom_template_check_final_queries(self, rule):
        engine_type = rule.get("ENGINE_TYPE", "").lower()
        if engine_type == 'databricks':
            print("Running Databricks...")
            try:
                execute_run_databricks(rule["CUSTOM_TEMPLATE_SQL"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            except Exception as e:
                print(f"Error executing CUSTOM_TEMPLATE_SQL on Databricks: {str(e)}")

        else:  # Assume Postgres
            print("Running Postgres...")
            with open(f"generated_{rule['RULE_NAME']}.sql", "w") as f:
                f.write(rule["CUSTOM_TEMPLATE_SQL"])
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            try:
                execute_run_postgres(rule["CUSTOM_TEMPLATE_SQL"], engine, False,load_script=True)
            except Exception as e:
                print(f"Error executing CUSTOM_TEMPLATE_SQL on Postgres: {str(e)}")

        return rule


    def business_rule_check(self) -> Dict[str, List[Dict[str, Any]]]:
        results = []
        if self.template.get("RULE_CATEGORY_NAME") == 'BUSINESS_RULE_CHECK':
            for idx, rule in enumerate(self.rules.get("RULES", [])):
                
                rule = {**self.template, **rule}
                rule = self.set_system_variables(rule)
                rule = self.set_dynamic_context_values(rule)
                rule = self.set_business_rule_check_templates(rule)
                rule = self.set_bookmark_value(rule)
                rule = self.process_fail_sql(rule)
                rule = self.process_pass_sql(rule)
                rule = self.set_business_rule_check_final_queries(rule)

                rule = self.exec_business_rule_check_final_queries(rule)

                self.rules["RULES"][idx] = rule
                self.logger.info(json.dumps(rule, indent=2))

                rule_name = rule.get('RULE_NAME', 'Unknown')
                rule_id = rule.get('RULE_ID', 'Unknown')

                results.append({
                "RULE_ID": rule_id,
                "RULE_NAME": rule_name,
                "DOMAIN_NAME": rule.get('DOMAIN_NAME'),
                "TABLES_CHECKED": rule.get('TABLES_CHECKED'),
                "TEAM_NAME": rule.get('TEAM_NAME'),
                "SEVERITY": rule.get('SEVERITY'),
                "RULE_CATEGORY": rule.get('RULE_CATEGORY'),
                "STATUS": rule.get('STATUS'),
                "QUERY": rule.get('FAILED_QUERY'),
                "FAIL_RECORD_COUNT": rule.get('FAIL_RECORD_COUNT'),
                "PASS_RECORD_COUNT": rule.get('PASS_RECORD_COUNT'),
                "COMMENTS": rule.get('COMMENTS'),
                "REMARKS": rule.get('REMARKS'),
                "TIME": rule.get('TIME', datetime.now(timezone('UTC')).isoformat())
                })

                if rule.get('STOP_ON_FAIL_STATUS')=='TRUE':  # for checking as per user input
                    self.logger.warning(f"Rule {rule_name} (ID: {rule_id}) failed with STOP_ON_FAIL_STATUS=TRUE. Stopping execution of remaining rules.")
                     
                    if not rule.get('STATUS'): # for checking as per rule status
                        self.logger.warning(f"Rule {rule_name} (ID: {rule_id}) failed STATUS is FALSE.")         
                        break
                  
        elif self.template.get("RULE_CATEGORY_NAME") == 'CUSTOM_TEMPLATE_RULE':
            for idx, rule in enumerate(self.rules.get("RULES", [])):
                rule = {**self.template, **rule}
                rule = self.set_system_variables(rule)
                rule = self.set_dynamic_context_values(rule)
                rule = self.assign_snippet_blocks_to_rule(rule)
                rule = self.set_custom_template(rule)
                rule = self.set_bookmark_value(rule)
                rule = self.set_custom_template_queries(rule)
                rule = self.exec_custom_template_check_final_queries(rule)

        print(json.dumps({"RULES": results}, indent=2))
        return results