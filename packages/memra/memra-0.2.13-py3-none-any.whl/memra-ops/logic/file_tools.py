"""
File handling tools for the Memra API server
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FileReader:
    """Read files from the filesystem"""
    
    def __init__(self):
        pass
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file and return its contents"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "data": {
                    "file_path": file_path,
                    "content": content,
                    "size": len(content)
                }
            }
            
        except Exception as e:
            logger.error(f"File reading failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 