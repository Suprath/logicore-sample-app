# FILE: main.py
from fastapi import FastAPI
import subprocess
import uvicorn

app = FastAPI(title="Vulnerable Sample App")

# A safe, root endpoint
 @app.get("/")
def read_root():
    return {"Status": "OK"}

# A deliberately vulnerable endpoint for CodeQL to find
 @app.get("/run")
def run_command(cmd: str):
    """
    Executes a shell command.
    VULNERABILITY: This is a command injection sink.
    """
    # In a real app, this might be used for diagnostics, but it's very unsafe.
    # CodeQL is designed to find this exact kind of vulnerability.
    subprocess.run(cmd, shell=True)
    return {"detail": f"Command '{cmd}' executed."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)