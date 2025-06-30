from typing import List
# 我们暂时移除了 UploadFile 和 File
from fastapi import FastAPI, Form
from pydantic import BaseModel, Field

# 导入我们两个核心逻辑模块
import card_processor
import data_parser

app = FastAPI(
    title="Card Checker API (Stable Test Version)",
    description="A temporary stable version for debugging.",
    version="4.0.0-stable-test" # 这是一个测试版本
)

# --- 数据输出模型定义 ---
class ProcessResponse(BaseModel):
    card: str
    status: str
    message: str

# --- API 端点（接收窗口）定义 ---

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "API is running"}

@app.post("/extract-and-process", response_model=List[ProcessResponse], summary="【测试用】处理原始文本 (表单输入)")
def extract_and_process_batch(
    raw_text: str = Form(..., example="在这里直接粘贴多行原始文本...")
):
    """
    接收大段原始文本作为表单数据，先提取格式，然后批量处理。
    """
    cleaned_cards = data_parser.parse_raw_text(raw_text)

    if not cleaned_cards:
        return []

    results = []
    for card in cleaned_cards:
        results.append(card_processor.process_card(card))

    return results

@app.post("/extract-only", response_model=List[str], summary="【测试用】仅从原始文本提取标准格式 (表单输入)")
def extract_format_only(
    raw_text: str = Form(..., example="在这里直接粘贴多行原始文本...")
):
    cleaned_cards = data_parser.parse_raw_text(raw_text)
    return cleaned_cards
