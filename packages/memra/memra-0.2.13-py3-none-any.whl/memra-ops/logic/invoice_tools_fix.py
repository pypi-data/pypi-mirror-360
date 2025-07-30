def _build_schema_prompt(self, schema: Dict[str, Any]) -> str:
    """Build a prompt that includes the database schema"""
    
    # Always return the schema-aware prompt
    base_prompt = '''Extract invoice data from this image and return ONLY a JSON object with these specific fields:
- vendor_name: The company name at the top of the invoice
- invoice_number: The invoice number or ID
- invoice_date: The date the invoice was issued (YYYY-MM-DD format)
- total_amount: The total invoice amount
- line_items: Array of items with descriptions and amounts

Look specifically for the company/vendor name prominently displayed on the invoice.

Return ONLY valid JSON with no additional text or explanation.'''
    
    # If no schema provided, return the base prompt
    if not schema:
        return base_prompt
    
    # Handle the schema format sent by the client
    if isinstance(schema, list):
        # Client sends array of column objects
        columns = schema
    elif isinstance(schema, dict) and "columns" in schema:
        # Standard format with columns array
        columns = schema["columns"]
    else:
        # Fallback to base prompt
        return base_prompt
    
    # Build field descriptions from schema
    field_descriptions = []
    for col in columns:
        # Handle both formats: {"column_name": "x"} and {"name": "x"}
        name = col.get("column_name") or col.get("name", "")
        col_type = col.get("data_type") or col.get("type", "")
        
        # Skip system fields
        if name and name not in ["id", "created_at", "updated_at", "status", "raw_json"]:
            if name == "vendor_name":
                field_descriptions.append(f"- {name}: The company name at the top of the invoice")
            elif name == "invoice_number":
                field_descriptions.append(f"- {name}: The invoice number or ID")
            elif name == "invoice_date":
                field_descriptions.append(f"- {name}: The date the invoice was issued (YYYY-MM-DD format)")
            elif name == "total_amount":
                field_descriptions.append(f"- {name}: The total invoice amount")
            elif name == "due_date":
                field_descriptions.append(f"- {name}: The invoice due date (YYYY-MM-DD format)")
            elif name == "tax_amount":
                field_descriptions.append(f"- {name}: The tax amount on the invoice")
            elif name == "line_items":
                field_descriptions.append(f"- {name}: Array of items with descriptions and amounts")
            else:
                field_descriptions.append(f"- {name}: {col_type}")
    
    if field_descriptions:
        schema_text = "\n".join(field_descriptions)
        return f'''Extract invoice data from this image and return ONLY a JSON object with these specific fields:
{schema_text}

Look specifically for the company/vendor name prominently displayed on the invoice.

Return ONLY valid JSON with no additional text or explanation.'''
    else:
        return base_prompt