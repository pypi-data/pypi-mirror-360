from typing import Union
import os
import webbrowser
from threading import Timer

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from pywander.web import get_random_available_port
from pywander_text.tc_sc import tc2sc,sc2tc
from pywander_text.pinyin import create_pinyin_string
from pywander_text.country_zh_abbr import get_country_zh_abbr, get_full_country_name
from pywander_text.encoding import print_encoding_convert_tab

api_app = FastAPI()


@api_app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# 转换API端点
@api_app.post("/convert")
async def convert_text(request: dict):
    ptype = request.get("ptype")
    text = request.get("text")

    try:
        if ptype == "tc_sc":
            direction = request.get("direction")

            if direction == 't2s':
                converted_text = tc2sc(text)
            elif direction == 's2t':
                converted_text = sc2tc(text)
            else:
                raise HTTPException(status_code=400, detail="不支持的转换方向")

            return {"converted_text": converted_text}
        elif ptype == "pinyin":
            hyphen = request.get("pinyinHyphen")

            converted_text = create_pinyin_string(text, hyphen=hyphen)
            return {"converted_text": converted_text}
        elif ptype == "country_zh_abbr":
            is_country_abbr = request.get("isCountryAbbr")

            if is_country_abbr:
                converted_text = get_full_country_name(text)
            else:
                converted_text = get_country_zh_abbr(text)

            return {"converted_text": converted_text}
        elif ptype == "encoding":
            converted_text = print_encoding_convert_tab(text)
            return {"converted_text": converted_text}
        else:
            raise HTTPException(status_code=400, detail="未知的处理类型")
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