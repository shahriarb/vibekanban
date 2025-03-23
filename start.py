import subprocess
import sys
import os
import time

def start_servers():
    """Start both the Flask application and the MCP server."""
    try:
        # Start Flask app in a subprocess
        flask_cmd = ["python", "-m", "flask", "run", "--port", "5050"]
        flask_proc = subprocess.Popen(
            flask_cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Started Flask app on port 5050")
        
        # Give Flask time to start up
        time.sleep(2)
        
        # Start MCP server
        mcp_cmd = ["python", "kanban_mcp_server.py"]
        mcp_proc = subprocess.Popen(
            mcp_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Started MCP server")
        
        # Keep the script running and monitor subprocesses
        while True:
            # Check Flask stdout/stderr and print
            flask_out = flask_proc.stdout.readline()
            if flask_out:
                print(f"[Flask] {flask_out.strip()}")
                
            flask_err = flask_proc.stderr.readline()
            if flask_err:
                print(f"[Flask Error] {flask_err.strip()}")
            
            # Check MCP stdout/stderr and print
            mcp_out = mcp_proc.stdout.readline()
            if mcp_out:
                print(f"[MCP] {mcp_out.strip()}")
                
            mcp_err = mcp_proc.stderr.readline()
            if mcp_err:
                print(f"[MCP Error] {mcp_err.strip()}")
            
            # Check if either process has exited
            if flask_proc.poll() is not None:
                print("Flask app stopped. Exiting...")
                mcp_proc.terminate()
                sys.exit(1)
                
            if mcp_proc.poll() is not None:
                print("MCP server stopped. Exiting...")
                flask_proc.terminate()
                sys.exit(1)
                
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        if 'flask_proc' in locals():
            flask_proc.terminate()
        if 'mcp_proc' in locals():
            mcp_proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    # Set environment variable for Flask
    os.environ["FLASK_APP"] = "run.py"
    
    # Run both servers
    start_servers() 