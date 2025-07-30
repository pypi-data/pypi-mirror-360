#!/usr/bin/env python3
"""
Memra System Startup Script
Starts all dependencies required for the Memra system to run
"""

import os
import sys
import time
import subprocess
import requests
import signal
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class MemraStartup:
    def __init__(self):
        self.project_root = project_root
        self.docker_compose_file = project_root / "docker-compose.yml"
        self.mcp_bridge_script = project_root / "mcp_bridge_server.py"
        self.processes = []
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 60)
        print("🚀 MEMRA SYSTEM STARTUP")
        print("=" * 60)
        print("Starting all dependencies for Memra AI workflow system...")
        print()
        
    def check_conda_environment(self):
        """Check if we're in the correct conda environment"""
        print("🔍 Checking conda environment...")
        
        # Check if we're in the memra environment
        conda_env = os.getenv('CONDA_DEFAULT_ENV')
        if conda_env != 'memra':
            print(f"❌ Warning: Not in 'memra' conda environment (current: {conda_env})")
            print("   Please run: conda activate memra")
            print("   Then run this script again.")
            return False
        
        print(f"✅ Conda environment: {conda_env}")
        return True
        
    def check_docker(self):
        """Check if Docker is running"""
        print("🐳 Checking Docker...")
        try:
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Docker is running")
                return True
            else:
                print("❌ Docker is not running")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Docker is not running or not installed")
            return False
            
    def start_postgresql(self):
        """Start PostgreSQL using Docker Compose"""
        print("🐘 Starting PostgreSQL...")
        
        try:
            # Check if containers are already running
            result = subprocess.run(['docker', 'ps', '--filter', 'name=memra-postgres'], 
                                  capture_output=True, text=True)
            
            if 'memra-postgres' in result.stdout:
                print("✅ PostgreSQL is already running")
                return True
                
            # Start PostgreSQL
            print("   Starting PostgreSQL container...")
            result = subprocess.run(['docker-compose', 'up', '-d', 'postgres'], 
                                  cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL started successfully")
                return True
            else:
                print(f"❌ Failed to start PostgreSQL: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting PostgreSQL: {e}")
            return False
            
    def wait_for_postgresql(self, max_attempts=30):
        """Wait for PostgreSQL to be ready"""
        print("⏳ Waiting for PostgreSQL to be ready...")
        
        for attempt in range(max_attempts):
            try:
                # Try to connect to PostgreSQL
                result = subprocess.run([
                    'docker', 'exec', 'memra-postgres', 
                    'pg_isready', '-U', 'memra', '-d', 'memra_invoice_db'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    print("✅ PostgreSQL is ready")
                    return True
                    
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
                
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(2)
            
        print("❌ PostgreSQL failed to start within timeout")
        return False
        
    def check_memra_api_key(self):
        """Check if MEMRA_API_KEY is set"""
        print("🔑 Checking Memra API key...")
        
        api_key = os.getenv('MEMRA_API_KEY')
        if not api_key:
            print("❌ MEMRA_API_KEY environment variable is not set")
            print("   Please set: export MEMRA_API_KEY='your-key-here'")
            return False
            
        print(f"✅ Memra API key is set: {api_key[:8]}...")
        return True
        
    def start_mcp_bridge(self):
        """Start the MCP bridge server"""
        print("🌉 Starting MCP Bridge Server...")
        
        try:
            # Check if MCP bridge is already running
            try:
                response = requests.get('http://localhost:8081/health', timeout=5)
                if response.status_code == 200:
                    print("✅ MCP Bridge Server is already running")
                    return True
            except requests.RequestException:
                pass
                
            # Start MCP bridge server in background
            print("   Starting MCP bridge server...")
            process = subprocess.Popen([
                sys.executable, str(self.mcp_bridge_script)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(process)
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server started successfully
            try:
                response = requests.get('http://localhost:8081/health', timeout=5)
                if response.status_code == 200:
                    print("✅ MCP Bridge Server started successfully")
                    return True
                else:
                    print(f"❌ MCP Bridge Server returned status {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ MCP Bridge Server failed to start: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting MCP Bridge Server: {e}")
            return False
            
    def test_memra_api(self):
        """Test the Memra API connection"""
        print("🌐 Testing Memra API connection...")
        
        try:
            from memra import get_api_status
            api_status = get_api_status()
            
            if api_status['api_healthy']:
                print(f"✅ Memra API is healthy")
                print(f"   URL: {api_status['api_url']}")
                print(f"   Tools Available: {api_status['tools_available']}")
                return True
            else:
                print("❌ Memra API is not healthy")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Memra API: {e}")
            return False
            
    def run_test_workflow(self):
        """Run a quick test to verify everything works"""
        print("🧪 Running system test...")
        
        try:
            # Import and run a simple test
            from memra import Agent, Department, LLM
            from memra.execution import ExecutionEngine
            
            # Create a simple test agent
            test_agent = Agent(
                role="Test Agent",
                job="Verify system is working",
                llm=LLM(model="llama-3.2-11b-vision-preview", temperature=0.1),
                sops=["Return a simple success message"],
                output_key="test_result"
            )
            
            # Create test department
            test_dept = Department(
                name="Test Department",
                mission="Verify Memra system is working",
                agents=[test_agent],
                workflow_order=["Test Agent"]
            )
            
            # Run test
            engine = ExecutionEngine()
            result = engine.execute_department(test_dept, {})
            
            if result.success:
                print("✅ System test passed - Memra is ready!")
                return True
            else:
                print(f"❌ System test failed: {result.error}")
                return False
                
        except Exception as e:
            print(f"❌ Error running system test: {e}")
            return False
            
    def cleanup(self):
        """Cleanup processes on exit"""
        print("\n🧹 Cleaning up processes...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
                    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n🛑 Received interrupt signal, shutting down...")
        self.cleanup()
        sys.exit(0)
        
    def start(self):
        """Main startup sequence"""
        try:
            self.print_banner()
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Check environment
            if not self.check_conda_environment():
                return False
                
            # Check Docker
            if not self.check_docker():
                print("❌ Please start Docker Desktop and try again")
                return False
                
            # Start PostgreSQL
            if not self.start_postgresql():
                return False
                
            if not self.wait_for_postgresql():
                return False
                
            # Check API key
            if not self.check_memra_api_key():
                return False
                
            # Start MCP bridge
            if not self.start_mcp_bridge():
                return False
                
            # Test API
            if not self.test_memra_api():
                return False
                
            # Run system test
            if not self.run_test_workflow():
                return False
                
            print("\n" + "=" * 60)
            print("🎉 MEMRA SYSTEM STARTED SUCCESSFULLY!")
            print("=" * 60)
            print("✅ All dependencies are running:")
            print("   • PostgreSQL Database (Docker)")
            print("   • MCP Bridge Server (localhost:8081)")
            print("   • Memra API (https://api.memra.co)")
            print()
            print("🚀 Ready to run workflows!")
            print("   Example: python3 examples/accounts_payable_client.py")
            print()
            print("💡 Keep this terminal open to maintain the MCP bridge server")
            print("   Press Ctrl+C to stop all services")
            print("=" * 60)
            
            # Keep the script running to maintain the MCP bridge server
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down Memra system...")
                self.cleanup()
                print("✅ Memra system stopped")
                
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            self.cleanup()
            return False
            
        return True

def main():
    """Main entry point"""
    startup = MemraStartup()
    success = startup.start()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 