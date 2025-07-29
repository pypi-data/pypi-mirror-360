#!/usr/bin/env python3
"""
Simple MCP Bridge Server for local tool execution
"""

import os
import json
import hmac
import hashlib
import logging
import asyncio
import psycopg2
import re
from decimal import Decimal
from aiohttp import web, web_request
from typing import Dict, Any, Optional

# Add Hugging Face imports
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: huggingface_hub not available. Install with: pip install huggingface_hub")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPBridgeServer:
    def __init__(self, postgres_url: str, bridge_secret: str):
        self.postgres_url = postgres_url
        self.bridge_secret = bridge_secret
        
        # Hugging Face configuration
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "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")
        self.hf_model = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        self.hf_client = None
        
        # Initialize Hugging Face client if available
        if HF_AVAILABLE and self.hf_api_key:
            try:
                self.hf_client = InferenceClient(
                    model=self.hf_model,
                    token=self.hf_api_key
                )
                logger.info(f"Initialized Hugging Face client with model: {self.hf_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Hugging Face client: {e}")
                self.hf_client = None
        else:
            logger.warning("Hugging Face client not available - using fallback pattern matching")
        
    def verify_signature(self, request_body: str, signature: str) -> bool:
        """Verify HMAC signature"""
        expected = hmac.new(
            self.bridge_secret.encode(),
            request_body.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    async def execute_tool(self, request: web_request.Request) -> web.Response:
        """Execute MCP tool endpoint"""
        try:
            # Get request body
            body = await request.text()
            data = json.loads(body)
            
            # Verify signature
            signature = request.headers.get('X-Bridge-Secret')
            if not signature or signature != self.bridge_secret:
                logger.warning("Invalid or missing bridge secret")
                return web.json_response({
                    "success": False,
                    "error": "Invalid authentication"
                }, status=401)
            
            tool_name = data.get('tool_name')
            input_data = data.get('input_data', {})
            
            logger.info(f"Executing MCP tool: {tool_name}")
            
            if tool_name == "DataValidator":
                result = await self.data_validator(input_data)
            elif tool_name == "PostgresInsert":
                result = await self.postgres_insert(input_data)
            elif tool_name == "SQLExecutor":
                result = await self.sql_executor(input_data)
            elif tool_name == "TextToSQLGenerator":
                result = await self.text_to_sql_generator(input_data)
            else:
                return web.json_response({
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }, status=400)
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def data_validator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema"""
        try:
            invoice_data = input_data.get('invoice_data', {})
            
            # Perform basic validation
            validation_errors = []
            
            # Check required fields
            required_fields = ['headerSection', 'billingDetails', 'chargesSummary']
            for field in required_fields:
                if field not in invoice_data:
                    validation_errors.append(f"Missing required field: {field}")
            
            # Validate header section
            if 'headerSection' in invoice_data:
                header = invoice_data['headerSection']
                if not header.get('vendorName'):
                    validation_errors.append("Missing vendor name in header")
                if not header.get('subtotal'):
                    validation_errors.append("Missing subtotal in header")
            
            # Validate billing details
            if 'billingDetails' in invoice_data:
                billing = invoice_data['billingDetails']
                if not billing.get('invoiceNumber'):
                    validation_errors.append("Missing invoice number")
                if not billing.get('invoiceDate'):
                    validation_errors.append("Missing invoice date")
            
            is_valid = len(validation_errors) == 0
            
            logger.info(f"Data validation completed: {'valid' if is_valid else 'invalid'}")
            
            return {
                "success": True,
                "data": {
                    "is_valid": is_valid,
                    "validation_errors": validation_errors,
                    "validated_data": invoice_data
                }
            }
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def postgres_insert(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into PostgreSQL"""
        try:
            invoice_data = input_data.get('invoice_data', {})
            table_name = input_data.get('table_name', 'invoices')
            
            # Extract key fields from invoice data
            header = invoice_data.get('headerSection', {})
            billing = invoice_data.get('billingDetails', {})
            charges = invoice_data.get('chargesSummary', {})
            
            # Prepare insert data
            insert_data = {
                'invoice_number': billing.get('invoiceNumber', ''),
                'vendor_name': header.get('vendorName', ''),
                'invoice_date': billing.get('invoiceDate', ''),
                'total_amount': charges.get('document_total', 0),
                'tax_amount': charges.get('secondary_tax', 0),
                'line_items': json.dumps(charges.get('lineItemsBreakdown', [])),
                'status': 'processed'
            }
            
            # Connect to database and insert
            conn = psycopg2.connect(self.postgres_url)
            cursor = conn.cursor()
            
            # Build insert query
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(insert_data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id"
            
            cursor.execute(query, list(insert_data.values()))
            record_id = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Successfully inserted record with ID: {record_id}")
            
            return {
                "success": True,
                "data": {
                    "success": True,
                    "record_id": record_id,
                    "database_table": table_name,
                    "inserted_data": insert_data
                }
            }
            
        except Exception as e:
            logger.error(f"Database insert failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sql_executor(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query against PostgreSQL"""
        try:
            sql_query = input_data.get('sql_query', '')
            
            if not sql_query:
                return {
                    "success": False,
                    "error": "No SQL query provided"
                }
            
            # Connect to database and execute query
            conn = psycopg2.connect(self.postgres_url)
            cursor = conn.cursor()
            
            # Execute the query
            cursor.execute(sql_query)
            
            # Fetch results if it's a SELECT query
            if sql_query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                
                # Convert to list of dictionaries
                formatted_results = []
                for row in results:
                    row_dict = dict(zip(column_names, row))
                    # Convert date/datetime objects to strings for JSON serialization
                    for key, value in row_dict.items():
                        if hasattr(value, 'isoformat'):  # datetime, date objects
                            row_dict[key] = value.isoformat()
                        elif isinstance(value, Decimal):  # Decimal objects
                            row_dict[key] = float(value)
                    formatted_results.append(row_dict)
                
                logger.info(f"SQL query executed successfully, returned {len(results)} rows")
                
                return {
                    "success": True,
                    "data": {
                        "query": sql_query,
                        "results": formatted_results,
                        "row_count": len(results),
                        "columns": column_names
                    }
                }
            else:
                # For non-SELECT queries (INSERT, UPDATE, DELETE)
                conn.commit()
                affected_rows = cursor.rowcount
                
                logger.info(f"SQL query executed successfully, affected {affected_rows} rows")
                
                return {
                    "success": True,
                    "data": {
                        "query": sql_query,
                        "affected_rows": affected_rows,
                        "message": "Query executed successfully"
                    }
                }
            
        except Exception as e:
            logger.error(f"SQL execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    async def text_to_sql_generator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL from natural language using LLM or fallback to pattern matching"""
        try:
            question = input_data.get('question', '')
            schema_info = input_data.get('schema_info', {})
            
            if not question:
                return {
                    "success": False,
                    "error": "No question provided"
                }
            
            # If no schema provided or incomplete, fetch it dynamically
            if not schema_info or not schema_info.get('schema', {}).get('invoices', {}).get('columns'):
                logger.info("No schema provided, fetching dynamically from database")
                schema_info = await self.get_table_schema("invoices")
            
            # Try LLM-based generation first
            if self.hf_client:
                try:
                    return await self._llm_text_to_sql(question, schema_info)
                except Exception as e:
                    logger.warning(f"LLM text-to-SQL failed, falling back to pattern matching: {e}")
            
            # Fallback to pattern matching
            return await self._pattern_text_to_sql(question, schema_info)
            
        except Exception as e:
            logger.error(f"Text-to-SQL generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _llm_text_to_sql(self, question: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL using Hugging Face LLM"""
        
        # Extract schema information
        tables = schema_info.get('schema', {})
        table_name = 'invoices'  # Default table
        columns = []
        
        # Get column information from schema
        if table_name in tables:
            table_info = tables[table_name]
            if 'columns' in table_info:
                columns = [f"{col['name']} ({col['type']})" for col in table_info['columns']]
        
        # If no schema info, use default columns
        if not columns:
            columns = [
                'id (integer)',
                'vendor_name (text)',
                'invoice_number (text)', 
                'invoice_date (date)',
                'total_amount (numeric)',
                'tax_amount (numeric)',
                'line_items (jsonb)',
                'status (text)'
            ]
        
        # Create the prompt for the LLM
        schema_text = f"Table: {table_name}\nColumns: {', '.join(columns)}"
        
        # Comprehensive prompt with detailed instructions and examples
        prompt = f"""You are a PostgreSQL SQL query generator. Convert natural language questions into valid PostgreSQL queries.

IMPORTANT RULES:
1. ALWAYS return a complete, valid SQL query
2. Use ONLY the table and columns provided in the schema
3. Use PostgreSQL syntax (ILIKE for case-insensitive matching)
4. For aggregations with GROUP BY, don't include non-aggregated columns in ORDER BY unless they're in GROUP BY
5. Use appropriate aliases for calculated columns (as count, as total, as average, etc.)
6. For date queries, use proper date functions and comparisons

TABLE SCHEMA:
Table: invoices
Columns: {', '.join(columns)}

QUERY PATTERNS AND EXAMPLES:

1. COUNT QUERIES:
Q: How many invoices are there?
A: SELECT COUNT(*) as count FROM invoices

Q: How many invoices from Air Liquide?
A: SELECT COUNT(*) as count FROM invoices WHERE vendor_name ILIKE '%air liquide%'

2. VENDOR FILTERING:
Q: Show me all invoices from Air Liquide
A: SELECT * FROM invoices WHERE vendor_name ILIKE '%air liquide%'

Q: Find invoices from Microsoft
A: SELECT * FROM invoices WHERE vendor_name ILIKE '%microsoft%'

3. AGGREGATION QUERIES:
Q: What is the total amount of all invoices?
A: SELECT SUM(total_amount) as total FROM invoices

Q: What is the average invoice amount?
A: SELECT AVG(total_amount) as average FROM invoices

Q: What is the highest invoice amount?
A: SELECT MAX(total_amount) as max_amount FROM invoices

4. GROUPING QUERIES:
Q: Show me invoices grouped by date
A: SELECT invoice_date, COUNT(*) as count FROM invoices GROUP BY invoice_date ORDER BY invoice_date

Q: Show me invoice counts by vendor
A: SELECT vendor_name, COUNT(*) as count FROM invoices GROUP BY vendor_name ORDER BY count DESC

Q: Who is the primary vendor?
A: SELECT vendor_name, COUNT(*) as count FROM invoices GROUP BY vendor_name ORDER BY count DESC LIMIT 1

5. SORTING AND LIMITING:
Q: Show me the 3 most recent invoices
A: SELECT * FROM invoices ORDER BY invoice_date DESC LIMIT 3

Q: Show me the oldest invoice
A: SELECT * FROM invoices ORDER BY invoice_date ASC LIMIT 1

6. AMOUNT FILTERING:
Q: Find invoices with amounts greater than 1000
A: SELECT * FROM invoices WHERE total_amount > 1000

Q: Show me invoices under 500
A: SELECT * FROM invoices WHERE total_amount < 500

7. DATE QUERIES:
Q: What is the most recent invoice date?
A: SELECT MAX(invoice_date) as latest_date FROM invoices

Q: Show me invoices from this year
A: SELECT * FROM invoices WHERE EXTRACT(YEAR FROM invoice_date) = EXTRACT(YEAR FROM CURRENT_DATE)

Q: What are the invoices created this month?
A: SELECT * FROM invoices WHERE EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE) AND EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE)

Q: Show me invoices from last month
A: SELECT * FROM invoices WHERE EXTRACT(YEAR FROM invoice_date) = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month') AND EXTRACT(MONTH FROM invoice_date) = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')

8. DISTINCT QUERIES:
Q: Show me all the vendors
A: SELECT DISTINCT vendor_name FROM invoices ORDER BY vendor_name

Q: What are all the different invoice dates?
A: SELECT DISTINCT invoice_date FROM invoices ORDER BY invoice_date

9. COMPLEX VENDOR ANALYSIS:
Q: Which vendor has the highest total invoice amount?
A: SELECT vendor_name, SUM(total_amount) as total FROM invoices GROUP BY vendor_name ORDER BY total DESC LIMIT 1

Q: Show me vendor totals
A: SELECT vendor_name, SUM(total_amount) as total, COUNT(*) as count FROM invoices GROUP BY vendor_name ORDER BY total DESC

10. LINE ITEMS (JSONB):
Q: Show me all the line item costs
A: SELECT vendor_name, invoice_number, line_items FROM invoices WHERE line_items IS NOT NULL

Q: What are the line item details?
A: SELECT id, vendor_name, line_items FROM invoices WHERE line_items IS NOT NULL AND line_items != '[]'

Q: Which invoice contains a line item for 'Electricity'?
A: SELECT * FROM invoices WHERE line_items::text ILIKE '%electricity%'

Q: Find invoices with line items containing 'PROPANE'
A: SELECT * FROM invoices WHERE line_items::text ILIKE '%propane%'

IMPORTANT: 
- Always return a complete SQL query starting with SELECT
- Never return partial queries or just "SELECT"
- Use proper PostgreSQL syntax
- Include appropriate WHERE, GROUP BY, ORDER BY, and LIMIT clauses as needed
- For vendor searches, use ILIKE with % wildcards for partial matching

Question: {question}
SQL Query:
"""

        try:
            # Call Hugging Face API with improved parameters
            response = self.hf_client.text_generation(
                prompt,
                max_new_tokens=150,  # Increased for complex queries
                temperature=0.05,    # Lower temperature for more deterministic output
                do_sample=True,
                stop_sequences=["\n\n", "Q:", "Question:", "Examples:"],  # Reduced to 4 sequences
                return_full_text=False  # Only return the generated part
            )
            
            # Extract SQL from response
            sql_query = response.strip()
            
            # Clean up the response - remove any extra text and extract SQL
            if "SELECT" in sql_query.upper():
                # Find the SQL query part
                lines = sql_query.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.upper().startswith('SELECT'):
                        sql_query = line.rstrip(';')
                        break
                else:
                    # If no line starts with SELECT, try to extract from the whole response
                    sql_match = re.search(r'(SELECT[^;]+)', sql_query, re.IGNORECASE | re.DOTALL)
                    if sql_match:
                        sql_query = sql_match.group(1).strip()
            
            # Final cleanup
            sql_query = sql_query.replace('\n', ' ').strip()
            
            # Validate the SQL contains basic components
            if not sql_query.upper().strip().startswith('SELECT'):
                raise ValueError(f"Generated response is not a valid SQL query: '{sql_query}'")
            
            # Check for incomplete queries
            if len(sql_query.strip()) < 15 or sql_query.upper().strip() == 'SELECT':
                raise ValueError(f"Generated incomplete SQL query: '{sql_query}'")
            
            logger.info(f"LLM generated SQL for question: '{question}' -> {sql_query}")
            
            return {
                "success": True,
                "data": {
                    "question": question,
                    "generated_sql": sql_query,
                    "explanation": f"Generated using {self.hf_model} LLM with schema context",
                    "confidence": "high",
                    "method": "llm",
                    "schema_used": {
                        "table": table_name,
                        "columns": [col.split(' (')[0] for col in columns]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"LLM text-to-SQL generation failed: {str(e)}")
            raise e
    
    async def _pattern_text_to_sql(self, question: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL using pattern matching (fallback method)"""
        
        # Extract schema information for better SQL generation
        tables = schema_info.get('schema', {})
        table_name = 'invoices'  # Default table
        columns = []
        
        # Get column information from schema
        if table_name in tables:
            table_info = tables[table_name]
            if 'columns' in table_info:
                columns = [col['name'] for col in table_info['columns']]
                column_types = {col['name']: col['type'] for col in table_info['columns']}
        
        # If no schema info, use default columns
        if not columns:
            columns = ['id', 'vendor_name', 'invoice_number', 'invoice_date', 'total_amount', 'line_items']
            column_types = {
                'id': 'integer',
                'vendor_name': 'text',
                'invoice_number': 'text', 
                'invoice_date': 'date',
                'total_amount': 'numeric',
                'line_items': 'jsonb'
            }
        
        # Generate SQL based on question and schema context
        question_lower = question.lower()
        
        # Determine what columns to select based on question
        select_clause = "*"  # default
        
        if 'total amount' in question_lower or 'sum' in question_lower:
            if 'total_amount' in columns:
                select_clause = "SUM(total_amount) as total"
            else:
                select_clause = "SUM(amount) as total"  # fallback
        elif 'count' in question_lower or 'how many' in question_lower:
            select_clause = "COUNT(*) as count"
        elif 'average' in question_lower or 'avg' in question_lower:
            if 'total_amount' in columns:
                select_clause = "AVG(total_amount) as average"
            else:
                select_clause = "AVG(amount) as average"  # fallback
        elif 'vendors' in question_lower or 'companies' in question_lower:
            if 'who are' in question_lower or 'all the' in question_lower or 'list' in question_lower:
                select_clause = "DISTINCT vendor_name"
        elif 'last' in question_lower or 'latest' in question_lower or 'most recent' in question_lower:
            if 'date' in question_lower:
                select_clause = "MAX(invoice_date) as latest_date"
            elif 'invoice' in question_lower:
                # For "last invoice" or "latest invoice", show the most recent one
                select_clause = "*"
                # Will be handled in ORDER BY section
        elif 'first' in question_lower or 'earliest' in question_lower:
            if 'date' in question_lower:
                select_clause = "MIN(invoice_date) as earliest_date"
            elif 'invoice' in question_lower:
                select_clause = "*"
                # Will be handled in ORDER BY section
        elif 'max' in question_lower or 'maximum' in question_lower or 'highest' in question_lower:
            if 'amount' in question_lower:
                select_clause = "MAX(total_amount) as max_amount"
            elif 'date' in question_lower:
                select_clause = "MAX(invoice_date) as max_date"
        elif 'min' in question_lower or 'minimum' in question_lower or 'lowest' in question_lower:
            if 'amount' in question_lower:
                select_clause = "MIN(total_amount) as min_amount"
            elif 'date' in question_lower:
                select_clause = "MIN(invoice_date) as min_date"
        
        # Build WHERE clause based on question
        where_clause = ""
        
        # Look for vendor filtering patterns
        vendor_patterns = [
            ('from', 'from'),  # "invoices from Air Liquide"
            ('by', 'by'),      # "invoices by Microsoft"
            ('for', 'for'),    # "invoices for Apple"
        ]
        
        vendor_name = None
        for pattern, keyword in vendor_patterns:
            if keyword in question_lower:
                parts = question_lower.split(keyword)
                if len(parts) > 1:
                    # Extract vendor name after the keyword
                    vendor_part = parts[1].strip()
                    # Remove common trailing words
                    vendor_part = vendor_part.replace(' invoices', '').replace(' invoice', '').strip()
                    # Take first few words as vendor name
                    vendor_words = vendor_part.split()[:3]  # Max 3 words for vendor name
                    if vendor_words:
                        vendor_name = ' '.join(vendor_words).strip('"\'.,?!')
                        break
        
        # Also check for direct company name patterns
        if not vendor_name:
            # Look for patterns like "Air Liquide invoices" or "Microsoft invoices"
            # Match capitalized words that might be company names
            company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+invoices?'
            match = re.search(company_pattern, question)
            if match:
                vendor_name = match.group(1)
        
        if vendor_name:
            if 'vendor_name' in columns:
                where_clause = f"WHERE vendor_name ILIKE '%{vendor_name}%'"
            elif 'vendor' in columns:
                where_clause = f"WHERE vendor ILIKE '%{vendor_name}%'"
        
        # Build ORDER BY clause
        order_clause = ""
        limit_clause = ""
        
        if 'recent' in question_lower or 'latest' in question_lower or 'last' in question_lower:
            if 'invoice_date' in columns:
                order_clause = "ORDER BY invoice_date DESC"
            elif 'date' in columns:
                order_clause = "ORDER BY date DESC"
            elif 'created_at' in columns:
                order_clause = "ORDER BY created_at DESC"
            
            # Add LIMIT for recent queries if it's asking for specific invoices
            if 'invoice' in question_lower and select_clause == "*":
                # Extract number if specified
                numbers = re.findall(r'\d+', question)
                limit = numbers[0] if numbers else "1"  # Default to 1 for "last invoice"
                limit_clause = f"LIMIT {limit}"
                
        elif 'first' in question_lower or 'earliest' in question_lower:
            if 'invoice_date' in columns:
                order_clause = "ORDER BY invoice_date ASC"
            elif 'date' in columns:
                order_clause = "ORDER BY date ASC"
            elif 'created_at' in columns:
                order_clause = "ORDER BY created_at ASC"
            
            # Add LIMIT for earliest queries if it's asking for specific invoices
            if 'invoice' in question_lower and select_clause == "*":
                numbers = re.findall(r'\d+', question)
                limit = numbers[0] if numbers else "1"
                limit_clause = f"LIMIT {limit}"
        
        elif re.search(r'\d+', question) and ('recent' in question_lower or 'latest' in question_lower or 'last' in question_lower):
            # Handle "Show me the 5 most recent invoices"
            if 'invoice_date' in columns:
                order_clause = "ORDER BY invoice_date DESC"
            numbers = re.findall(r'\d+', question)
            if numbers:
                limit_clause = f"LIMIT {numbers[0]}"
        
        # Construct the final SQL query
        sql_parts = [f"SELECT {select_clause}", f"FROM {table_name}"]
        
        if where_clause:
            sql_parts.append(where_clause)
        
        if order_clause:
            sql_parts.append(order_clause)
            
        if limit_clause:
            sql_parts.append(limit_clause)
        
        sql_query = " ".join(sql_parts)
        
        # Generate explanation based on schema context
        explanation_parts = [f"Generated SQL query for table '{table_name}' using pattern matching"]
        if columns:
            explanation_parts.append(f"Available columns: {', '.join(columns)}")
        if where_clause:
            explanation_parts.append("Applied filtering based on question context")
        if order_clause:
            explanation_parts.append("Added sorting and/or limiting based on question")
        
        explanation = ". ".join(explanation_parts)
        
        logger.info(f"Pattern matching generated SQL for question: '{question}' -> {sql_query}")
        logger.info(f"Used schema with columns: {columns}")
        
        return {
            "success": True,
            "data": {
                "question": question,
                "generated_sql": sql_query,
                "explanation": explanation,
                "confidence": "medium",  # Lower confidence for pattern matching
                "method": "pattern_matching",
                "schema_used": {
                    "table": table_name,
                    "columns": columns,
                    "column_types": column_types if 'column_types' in locals() else {}
                }
            }
        }
    
    async def health_check(self, request: web_request.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "mcp-bridge"})
    
    async def get_schema(self, request: web_request.Request) -> web.Response:
        """Get database schema endpoint"""
        try:
            table_name = request.query.get('table', 'invoices')
            schema = await self.get_table_schema(table_name)
            return web.json_response({
                "success": True,
                "data": schema
            })
        except Exception as e:
            logger.error(f"Schema fetch failed: {str(e)}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    def create_app(self) -> web.Application:
        """Create aiohttp application"""
        app = web.Application()
        
        # Add routes
        app.router.add_post('/execute_tool', self.execute_tool)
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/get_schema', self.get_schema)
        
        return app
    
    async def start(self, port: int = 8081):
        """Start the server"""
        app = self.create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        
        logger.info(f"MCP Bridge Server started on http://localhost:{port}")
        logger.info(f"Available endpoints:")
        logger.info(f"  POST /execute_tool - Execute MCP tools")
        logger.info(f"  GET  /health - Health check")
        logger.info(f"  GET  /get_schema - Get database schema")
        
        # Keep running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
        finally:
            await runner.cleanup()

    async def get_table_schema(self, table_name: str = "invoices") -> Dict[str, Any]:
        """Dynamically fetch table schema from database"""
        try:
            conn = psycopg2.connect(self.postgres_url)
            cursor = conn.cursor()
            
            # Get column information
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """
            cursor.execute(query, (table_name,))
            columns = cursor.fetchall()
            
            schema = {
                "schema": {
                    table_name: {
                        "columns": [
                            {
                                "name": col[0],
                                "type": col[1],
                                "nullable": col[2] == "YES",
                                "default": col[3]
                            }
                            for col in columns
                        ]
                    }
                }
            }
            
            cursor.close()
            conn.close()
            
            logger.info(f"Dynamically fetched schema for table '{table_name}' with {len(columns)} columns")
            return schema
            
        except Exception as e:
            logger.error(f"Failed to fetch schema for table '{table_name}': {str(e)}")
            # Fallback to basic schema
            return {
                "schema": {
                    table_name: {
                        "columns": [
                            {"name": "id", "type": "integer"},
                            {"name": "vendor_name", "type": "character varying"},
                            {"name": "invoice_date", "type": "date"},
                            {"name": "total_amount", "type": "numeric"}
                        ]
                    }
                }
            }

def main():
    # Get configuration from environment
    postgres_url = os.getenv('MCP_POSTGRES_URL', 'postgresql://memra:memra123@localhost:5432/memra_invoice_db')
    bridge_secret = os.getenv('MCP_BRIDGE_SECRET', 'test-secret-for-development')
    hf_api_key = os.getenv('HUGGINGFACE_API_KEY', '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')
    hf_model = os.getenv('HUGGINGFACE_MODEL', 'meta-llama/Llama-3.1-8B-Instruct')
    
    logger.info(f"Starting MCP Bridge Server...")
    logger.info(f"PostgreSQL URL: {postgres_url}")
    logger.info(f"Bridge Secret: {'*' * len(bridge_secret)}")
    logger.info(f"Hugging Face Model: {hf_model}")
    logger.info(f"Hugging Face API Key: {'*' * (len(hf_api_key) - 8) + hf_api_key[-8:] if hf_api_key else 'Not set'}")
    
    # Create and start server
    server = MCPBridgeServer(postgres_url, bridge_secret)
    asyncio.run(server.start())

if __name__ == '__main__':
    main() 