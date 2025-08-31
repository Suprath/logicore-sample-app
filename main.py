# FILE: logicore-sample-app/main.py
import os
import time
import traceback
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import subprocess
import uvicorn

app = FastAPI(
    title="Vulnerable Sample App for LogiCore Correlator",
    description="This application contains several deliberate flaws to test different analysis types."
)

# --- NEW: Custom Exception Handler ---
# This function will run automatically whenever an unhandled error occurs in any endpoint.
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    # 1. Get the commit hash and service name. In a real app, these are often
    #    baked in at build time. We use environment variables for flexibility.
    commit_hash = os.environ.get("GIT_COMMIT_HASH", "unknown_commit")
    service_name = os.environ.get("SERVICE_NAME", "Suprath/logicore-sample-app")

    # 2. Format the error details, including the full stack trace.
    error_message = str(exc)
    stack_trace = traceback.format_exc()
    
    print("--- LIVE ERROR DETECTED ---")
    print(stack_trace)
    
    # 3. Prepare the JSON payload for the Correlator service.
    correlator_payload = {
        "service_name": service_name,
        "commit_hash": commit_hash,
        "log_message": error_message,
        "stack_trace": stack_trace
    }
    
    # 4. Get the Correlator's URL from an environment variable.
    correlator_url = os.environ.get("CORRELATOR_LOG_ANALYSIS_URL")
    
    if correlator_url:
        try:
            print(f"INFO: Sending error log to Correlator at {correlator_url}")
            # Send the error log to our new '/analyze-log' endpoint.
            # We set a short timeout so this doesn't slow down the error response.
            requests.post(correlator_url, json=correlator_payload, timeout=3)
        except requests.RequestException as e:
            # If the correlator can't be reached, just print an error and continue.
            print(f"ERROR: Could not send log to Correlator: {e}")

    # 5. Return a standard 500 error response to the original user who triggered the error.
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. The incident has been reported for analysis."},
    )


# --- Endpoints ---

@app.get("/")
def read_root():
    """A safe, root endpoint to confirm the server is running."""
    return {"Status": "OK", "Description": "Sample App is running."}


# --- 1. Security Vulnerability Endpoint ---
@app.get("/run")
def run_command(cmd: str):
    """Executes a shell command. VULNERABILITY: This is a command injection sink."""
    subprocess.run(cmd, shell=True, check=True)
    return {"detail": f"Command '{cmd}' executed."}


# --- 2. Performance Issue Endpoint ---
@app.get("/slow")
def slow_endpoint():
    """This endpoint simulates a slow database query or a long-running process."""
    print("INFO: Received request for /slow endpoint. Simulating a 5-second delay...")
    time.sleep(5)
    print("INFO: Slow operation complete.")
    return {"detail": "This response was intentionally delayed by 5 seconds."}


# --- 3. Reliability Issue Endpoint ---
@app.get("/error")
def error_endpoint():
    """This endpoint will reliably crash and be caught by the exception handler."""
    # This will raise a TypeError because you can't add a string to an integer.
    result = "hello" + 5 
    return {"detail": f"This line will never be reached: {result}"}


# --- Main Execution Block ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)