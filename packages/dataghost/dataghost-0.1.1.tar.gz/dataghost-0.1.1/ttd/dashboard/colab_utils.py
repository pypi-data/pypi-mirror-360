"""
Utilities for running DataGhost dashboard in Google Colab and similar environments
"""
import os
import subprocess
import sys
import time
from typing import Optional, Tuple


def detect_colab_environment() -> bool:
    """Detect if running in Google Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def detect_jupyter_environment() -> bool:
    """Detect if running in Jupyter notebook/lab"""
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    return False


def install_and_setup_ngrok() -> bool:
    """Install and setup ngrok for tunneling"""
    try:
        # Check if ngrok is already installed
        result = subprocess.run(["which", "ngrok"], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        # Install ngrok
        print("Installing ngrok...")
        subprocess.run(["pip", "install", "pyngrok"], check=True)
        
        # Install ngrok binary
        from pyngrok import ngrok
        ngrok.install_ngrok()
        return True
    except Exception as e:
        print(f"Failed to install ngrok: {e}")
        return False


def create_ngrok_tunnel(port: int = 8501) -> Optional[str]:
    """Create an ngrok tunnel for the dashboard"""
    try:
        from pyngrok import ngrok
        
        # Create tunnel
        tunnel = ngrok.connect(port, "http")
        public_url = tunnel.public_url
        
        print(f"🌐 DataGhost Dashboard is now accessible at: {public_url}")
        print(f"📱 This URL works from anywhere in the world!")
        
        return public_url
    except Exception as e:
        print(f"Failed to create ngrok tunnel: {e}")
        return None


def create_localtunnel_tunnel(port: int = 8501) -> Optional[str]:
    """Create a localtunnel tunnel for the dashboard"""
    try:
        import subprocess
        import json
        
        # Install localtunnel if not available
        try:
            subprocess.run(["npm", "install", "-g", "localtunnel"], check=True, capture_output=True)
        except:
            print("Failed to install localtunnel. Make sure Node.js is installed.")
            return None
        
        # Create tunnel
        process = subprocess.Popen(
            ["lt", "--port", str(port), "--print-requests"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get the URL from output
        import time
        time.sleep(2)
        
        if process.poll() is None:
            # Process is running, try to get URL
            try:
                output = process.stdout.readline()
                if "https://" in output:
                    public_url = output.strip()
                    print(f"🌐 DataGhost Dashboard is now accessible at: {public_url}")
                    print(f"📱 This URL works from anywhere in the world!")
                    return public_url
            except:
                pass
        
        print("Failed to create localtunnel tunnel")
        return None
    except Exception as e:
        print(f"Failed to create localtunnel tunnel: {e}")
        return None


def create_tunnel(port: int = 8501, service: str = "ngrok") -> Optional[str]:
    """Create a tunnel using the specified service"""
    if service == "ngrok":
        return create_ngrok_tunnel(port)
    elif service == "localtunnel":
        return create_localtunnel_tunnel(port)
    else:
        print(f"Unknown tunnel service: {service}")
        return None


def setup_colab_dashboard(port: int = 8501) -> Tuple[Optional[str], bool]:
    """Setup dashboard for Google Colab environment"""
    print("🔧 Setting up DataGhost dashboard for Google Colab...")
    
    # Install ngrok if needed
    if not install_and_setup_ngrok():
        return None, False
    
    # Create tunnel
    public_url = create_ngrok_tunnel(port)
    
    if public_url:
        # Display instructions for Colab
        print("\n" + "="*60)
        print("📊 DATAGHOST DASHBOARD READY FOR COLAB!")
        print("="*60)
        print(f"🌐 Public URL: {public_url}")
        print("\n📋 Instructions:")
        print("1. Click the URL above to open the dashboard")
        print("2. The dashboard will work from any device/browser")
        print("3. Share the URL with team members if needed")
        print("4. The tunnel will stay active while this cell is running")
        print("\n⚠️  Note: Keep this cell running to maintain the tunnel")
        print("="*60)
        
        return public_url, True
    
    return None, False


def display_colab_instructions():
    """Display instructions for using DataGhost in Colab"""
    print("""
🚀 DataGhost in Google Colab
============================

To use the DataGhost dashboard in Google Colab:

1. Install DataGhost:
   !pip install dataghost

2. Import and setup:
   from ttd.dashboard.colab_utils import setup_colab_dashboard
   public_url, success = setup_colab_dashboard()

3. Run your dashboard:
   import dataghost
   # Your DataGhost code here...
   
4. The dashboard will be accessible via the public URL

Need help? Check the documentation at: https://github.com/dataghost/dataghost
""")


def create_colab_cell_code() -> str:
    """Generate code for a Colab cell to run the dashboard"""
    return '''
# DataGhost Dashboard for Google Colab
from ttd.dashboard.colab_utils import setup_colab_dashboard
from ttd.dashboard.server import DashboardServer
import asyncio
import threading

# Setup tunnel
public_url, success = setup_colab_dashboard()

if success:
    # Start dashboard server
    server = DashboardServer(port=8501)
    
    # Run in background thread
    def run_server():
        import uvicorn
        uvicorn.run(server.app, host="0.0.0.0", port=8501)
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    
    print(f"✅ Dashboard running at: {public_url}")
    print("📊 Keep this cell running to maintain the dashboard")
else:
    print("❌ Failed to setup dashboard tunnel")
'''