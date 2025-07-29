#!/usr/bin/env python3
"""
Memra System Stop Script
Gracefully stops all Memra system dependencies
"""

import os
import sys
import subprocess
import requests
import signal
from pathlib import Path

class MemraStop:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def print_banner(self):
        """Print stop banner"""
        print("=" * 60)
        print("🛑 MEMRA SYSTEM SHUTDOWN")
        print("=" * 60)
        print("Stopping all Memra system dependencies...")
        print()
        
    def stop_mcp_bridge(self):
        """Stop the MCP bridge server"""
        print("🌉 Stopping MCP Bridge Server...")
        
        try:
            # Try to send a graceful shutdown signal
            response = requests.get('http://localhost:8081/health', timeout=5)
            if response.status_code == 200:
                print("   MCP Bridge Server is running, stopping...")
                
                # Find and kill the MCP bridge process
                result = subprocess.run(['pkill', '-f', 'mcp_bridge_server.py'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ MCP Bridge Server stopped")
                else:
                    print("⚠️  MCP Bridge Server process not found (may already be stopped)")
            else:
                print("✅ MCP Bridge Server is not running")
                
        except requests.RequestException:
            print("✅ MCP Bridge Server is not running")
            
    def stop_postgresql(self):
        """Stop PostgreSQL using Docker Compose"""
        print("🐘 Stopping PostgreSQL...")
        
        try:
            # Check if PostgreSQL container is running
            result = subprocess.run(['docker', 'ps', '--filter', 'name=memra-postgres'], 
                                  capture_output=True, text=True)
            
            if 'memra-postgres' in result.stdout:
                print("   PostgreSQL container is running, stopping...")
                
                # Stop PostgreSQL container
                result = subprocess.run(['docker-compose', 'stop', 'postgres'], 
                                      cwd=self.project_root, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ PostgreSQL stopped")
                else:
                    print(f"⚠️  Warning: Failed to stop PostgreSQL: {result.stderr}")
            else:
                print("✅ PostgreSQL is not running")
                
        except Exception as e:
            print(f"⚠️  Warning: Error stopping PostgreSQL: {e}")
            
    def cleanup_docker(self):
        """Clean up any orphaned Docker containers"""
        print("🧹 Cleaning up Docker containers...")
        
        try:
            # Remove any stopped containers
            result = subprocess.run(['docker', 'container', 'prune', '-f'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Docker containers cleaned up")
            else:
                print("⚠️  Warning: Failed to clean up Docker containers")
                
        except Exception as e:
            print(f"⚠️  Warning: Error cleaning up Docker: {e}")
            
    def stop(self):
        """Main stop sequence"""
        try:
            self.print_banner()
            
            # Stop MCP bridge server
            self.stop_mcp_bridge()
            
            # Stop PostgreSQL
            self.stop_postgresql()
            
            # Clean up Docker
            self.cleanup_docker()
            
            print("\n" + "=" * 60)
            print("✅ MEMRA SYSTEM STOPPED SUCCESSFULLY!")
            print("=" * 60)
            print("All services have been stopped:")
            print("   • MCP Bridge Server")
            print("   • PostgreSQL Database")
            print("   • Docker containers cleaned up")
            print()
            print("💡 To start the system again, run:")
            print("   ./scripts/start_memra.sh")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Stop failed: {e}")
            return False
            
        return True

def main():
    """Main entry point"""
    stop = MemraStop()
    success = stop.stop()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 