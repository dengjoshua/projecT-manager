import modal
from fastapi import FastAPI



app = modal.App("project-manager")

app.image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

@app.function()
def run_server():
    from main import app
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.local_entrypoint()
def start_app():
    return run_server()