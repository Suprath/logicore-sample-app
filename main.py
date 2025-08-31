

# --- NEW: A deliberately slow endpoint to simulate performance issues ---
@app.get("/slow")
def slow_endpoint():
    """
    This endpoint simulates a slow database query or a long-running process.
    It will cause a 'latency' or 'timeout' alert.
    """
    time.sleep(5) # Pauses execution for 5 seconds
    return {"detail": "This was intentionally slow."}


# --- NEW: An endpoint that will reliably crash to simulate reliability issues ---
@app.get("/error")
def error_endpoint():
    """
    This endpoint simulates a classic bug, like a Null Pointer Exception.
    It will cause a '5xx' or 'exception' alert.
    """
    # This is a simple way to cause a TypeError, which is a common runtime error.
    result = "hello" + 5
    return {"detail": f"This should not be returned: {result}"}
