from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field

# 导入我们两个核心逻辑模块
import card_processor
import data_parser

app = FastAPI(
    title="Card Checker API",
    description="Processes card info. Supports single, pre-formatted batch, and raw text endpoints.",
    version="3.1.0-full-suite" # 再次升级版本号
)

# --- 数据输入/输出模型定义 ---

class SingleCardInput(BaseModel):
    card_data: str

class BatchCardInput(BaseModel):
    card_data: List[str]

class RawTextInput(BaseModel):
    raw_text: str = Field(..., example="5536...|...| Name | Address...\n4111...|...| Name | Address...")

class ProcessResponse(BaseModel):
    card: str
    status: str
    message: str

# --- API 端点（接收窗口）定义 ---

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "API is running"}

# --------------------------------------------------------------------
# 【【【 这 是 您 要 的 新 功 能 】】】
@app.post("/extract-only", response_model=List[str], summary="【新增功能】只提取格式，不处理支付")
def extract_format_only(input_data: RawTextInput):
    """
    接收一大段原始文本，仅返回提取和格式化后的标准卡片字符串列表。
    """
    # 直接调用“打包服务”，并立刻返回打包好的结果
    cleaned_cards = data_parser.parse_raw_text(input_data.raw_text)
    return cleaned_cards
# --------------------------------------------------------------------

@app.post("/extract-and-process", response_model=List[ProcessResponse], summary="【推荐】处理原始文本 (一步完成提取+处理)")
def extract_and_process_batch(input_data: RawTextInput):
    """
    接收一大段原始文本，先提取格式，然后批量处理。
    """
    cleaned_cards = data_parser.parse_raw_text(input_data.raw_text)

    if not cleaned_cards:
        return []

    results = []
    for card in cleaned_cards:
        results.append(card_processor.process_card(card))

    return results

@app.post("/process-batch", response_model=List[ProcessResponse], summary="【旧】处理已格式化的卡片列表")
def process_batch(card_input: BatchCardInput):
    results = []
    for card in card_input.card_data:
        results.append(card_processor.process_card(card))
    return results

@app.post("/process-single-card", response_model=List[ProcessResponse], summary="【旧】处理单张已格式化的卡片")
def process_single(card_input: SingleCardInput):
    # 为了保持返回格式统一，我们让它也返回一个列表，即使只有一个元素
    result = card_processor.process_card(card_input.card_data)
    return [result]
