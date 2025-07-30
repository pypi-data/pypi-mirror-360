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
from aiohttp import web, web_request
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPBridgeServer:
    def __init__(self, postgres_url: str, bridge_secret: str):
        self.postgres_url = postgres_url
        self.bridge_secret = bridge_secret
        
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
    
    async def health_check(self, request: web_request.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "mcp-bridge"})
    
    def create_app(self) -> web.Application:
        """Create aiohttp application"""
        app = web.Application()
        
        # Add routes
        app.router.add_post('/execute_tool', self.execute_tool)
        app.router.add_get('/health', self.health_check)
        
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
        
        # Keep running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
        finally:
            await runner.cleanup()

def main():
    # Get configuration from environment
    postgres_url = os.getenv('MCP_POSTGRES_URL', 'postgresql://tarpus@localhost:5432/memra_invoice_db')
    bridge_secret = os.getenv('MCP_BRIDGE_SECRET', 'test-secret-for-development')
    
    logger.info(f"Starting MCP Bridge Server...")
    logger.info(f"PostgreSQL URL: {postgres_url}")
    logger.info(f"Bridge Secret: {'*' * len(bridge_secret)}")
    
    # Create and start server
    server = MCPBridgeServer(postgres_url, bridge_secret)
    asyncio.run(server.start())

if __name__ == '__main__':
    main() 