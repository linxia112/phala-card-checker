from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field

# 导入我们两个核心逻辑模块
import card_processor
import data_parser # <-- 导入我们刚刚创建的新模块

app = FastAPI(
    title="Card Checker API",
    description="Processes card info. Supports single, pre-formatted batch, and raw text batch processing.",
    version="3.0.0-full" # 升级版本号
)

# --- 数据输入/输出模型定义 ---

# 用于接收单条标准格式输入的模型
class SingleCardInput(BaseModel):
    card_data: str

# 用于接收多条标准格式输入的模型
class BatchCardInput(BaseModel):
    card_data: List[str]

# 【新】用于接收原始文本输入的模型
class RawTextInput(BaseModel):
    raw_text: str = Field(..., example="5536...|...| Name | Address...\n4111...|...| Name | Address...")

# 用于定义单条输出结果的模型
class ProcessResponse(BaseModel):
    card: str
    status: str
    message: str

# --- API 端点（接收窗口）定义 ---

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "API is running"}

# 【新功能】我们全新的、最智能的端点！
@app.post("/extract-and-process", response_model=List[ProcessResponse], summary="【推荐】直接处理原始文本，自动提取并批量处理")
def extract_and_process_batch(input_data: RawTextInput):
    """
    接收一大段原始文本，先提取格式，然后批量处理。
    """
    # 第一步：调用“打包服务”，从原始文本中提取出标准格式的卡片列表
    cleaned_cards = data_parser.parse_raw_text(input_data.raw_text)

    # 如果没有提取到任何有效卡片，就返回一个空列表
    if not cleaned_cards:
        return []

    # 第二步：像以前一样，循环处理所有被成功提取的卡片
    results = []
    for card in cleaned_cards:
        results.append(card_processor.process_card(card))

    # 第三步：返回包含所有结果的清单
    return results

# --- 以下是旧的端点，我们保留它们以备不时之需 ---

@app.post("/process-batch", response_model=List[ProcessResponse], summary="【旧】处理已格式化的卡片列表")
def process_batch(card_input: BatchCardInput):
    results = []
    for card in card_input.card_data:
        results.append(card_processor.process_card(card))
    return results

@app.post("/process-single-card", response_model=ProcessResponse, summary="【旧】处理单张已格式化的卡片")
def process_single(card_input: SingleCardInput):
    return card_processor.process_card(card_input.card_data)

