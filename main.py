# FILE: main.py

from fastapi import FastAPI
import subprocess
import uvicorn
import time # Import the 'time' module for the slow endpoint

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Vulnerable Sample App for LogiCore Correlator",
    description="This application contains several deliberate flaws to test different analysis types."
)

# --- Endpoints ---

@app.get("/")
def read_root():
    """A safe, root endpoint to confirm the server is running."""
    return {"Status": "OK", "Description": "Sample App is running."}

# --- 1. Security Vulnerability Endpoint ---
@app.get("/run")
def run_command(cmd: str):
    """
    Executes a shell command.
    VULNERABILITY: This is a classic Command Injection sink.
    An alert with 'suspicious' or 'vulnerability' should trigger a security scan that finds this.
    """
    # This is an unsafe operation that CodeQL is designed to detect.
    subprocess.run(cmd, shell=True)
    return {"detail": f"Command '{cmd}' executed."}

# --- 2. Performance Issue Endpoint ---
@app.get("/slow")
def slow_endpoint():
    """
    This endpoint simulates a slow database query or a long-running process.
    It will cause a 'latency' or 'timeout' alert in a real monitoring system.
    """
    print("INFO: Received request for /slow endpoint. Simulating a 5-second delay...")
    time.sleep(5) # Pauses execution for 5 seconds
    print("INFO: Slow operation complete.")
    return {"detail": "This response was intentionally delayed by 5 seconds."}

# --- 3. Reliability Issue Endpoint ---
@app.get("/error")
def error_endpoint():
    """
    This endpoint will reliably crash with a server error (HTTP 500).
    It simulates a common bug, like a Null Pointer or Type Error.
    An alert with 'error' or '5xx' should trigger a reliability scan.
    """
    try:
        # This will raise a TypeError because you can't add a string to an integer.
        result = "hello" + 5
        # This line will never be reached.
        return {"detail": f"This should not be returned: {result}"}
    except TypeError as e:
        # In a real FastAPI app, this would be handled by an exception handler
        # and would return a 500 Internal Server Error response.
        print(f"ERROR: A TypeError occurred: {e}")
        # Re-raise to let FastAPI's default error handling take over.
        raise e

# --- Main Execution Block ---
# This allows you to run the server locally for testing if needed,
# though it's primarily designed to be run in a container.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)