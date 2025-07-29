from typing import Union
import os
import webbrowser

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

html_path = os.path.join(os.path.dirname(__file__), 'html')
from threading import Timer

app.mount("/", StaticFiles(directory=html_path, html=True))


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

from pywander.web import get_random_available_port

PORT = get_random_available_port()

def open_browser():
    webbrowser.open_new(f"http://127.0.0.1:{PORT}")


def main():
    Timer(1, open_browser).start()
    uvicorn.run(app, host="localhost", port=PORT)

if __name__ == "__main__":
    main()