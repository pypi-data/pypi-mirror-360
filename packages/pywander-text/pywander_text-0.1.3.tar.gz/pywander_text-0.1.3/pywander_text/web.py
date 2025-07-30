from typing import Union
import os
import webbrowser
from threading import Timer

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pywander.web import get_random_available_port
from pywander_text.tc_sc import tc2sc,sc2tc
api_app = FastAPI()


# 定义请求模型
class TextConvertRequest(BaseModel):
    text: str
    direction: str  # 't2s' 或 's2t'

@api_app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# 转换API端点
@api_app.post("/convert")
async def convert_text(request: TextConvertRequest):
    try:
        if request.direction == 't2s':
            converted_text = tc2sc(request.text)
        elif request.direction == 's2t':
            converted_text = sc2tc(request.text)
        else:
            raise HTTPException(status_code=400, detail="不支持的转换方向")

        return {"converted_text": converted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 创建主应用
app = FastAPI()

# 挂载API应用到/api路径
app.mount("/api", api_app)

# 挂载静态文件服务
html_path = os.path.join(os.path.dirname(__file__), 'html')
app.mount("/", StaticFiles(directory=html_path, html=True), name="static")

PORT = get_random_available_port()

def open_browser():
    webbrowser.open_new(f"http://127.0.0.1:{PORT}")


def main():
    Timer(1, open_browser).start()
    uvicorn.run(app, host="localhost", port=PORT)

if __name__ == "__main__":
    main()