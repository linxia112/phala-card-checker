from typing import List
# Form 是这次修改的关键，我们需要导入它
from fastapi import FastAPI, Form
from pydantic import BaseModel, Field

# 导入我们两个核心逻辑模块
import card_processor
import data_parser

app = FastAPI(
    title="Card Checker API",
    description="Processes card info. Supports single, pre-formatted batch, and raw text endpoints.",
    version="4.0.0-final" # 最终版！
)

# --- 数据输出模型定义 (输入模型不再需要为表单定义) ---
class ProcessResponse(BaseModel):
    card: str
    status: str
    message: str

# --- API 端点（接收窗口）定义 ---

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "API is running"}

# --------------------------------------------------------------------
# 【【【 已升级为更方便的表单模式 】】】
@app.post("/extract-only", response_model=List[str], summary="【推荐】仅从原始文本提取标准格式 (表单输入)")
def extract_format_only(
    # 我们告诉 API，这个数据直接从一个叫做 "raw_text" 的表单字段里取
    raw_text: str = Form(..., example="在这里直接粘贴多行原始文本...")
):
    """
    接收大段原始文本作为表单数据，仅返回提取和格式化后的标准卡片字符串列表。
    """
    cleaned_cards = data_parser.parse_raw_text(raw_text)
    return cleaned_cards
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# 【【【 已升级为更方便的表单模式 】】】
@app.post("/extract-and-process", response_model=List[ProcessResponse], summary="【推荐】处理原始文本 (表单输入, 一步到位)")
def extract_and_process_batch(
    # 同样，数据从表单字段 "raw_text" 里取
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
# --------------------------------------------------------------------
