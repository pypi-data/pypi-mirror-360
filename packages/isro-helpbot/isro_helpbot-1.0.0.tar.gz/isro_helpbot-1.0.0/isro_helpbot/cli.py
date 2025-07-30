# isro_helpbot/cli.py

import uvicorn

def main():
    uvicorn.run("api.main_api:app", host="127.0.0.1", port=8080, reload=True)
