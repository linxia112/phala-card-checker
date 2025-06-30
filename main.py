from typing import List
# UploadFile 和 File 是实现文件上传的关键
from fastapi import FastAPI, Form, File, UploadFile
from pydantic import BaseModel, Field

# 导入我们两个核心逻辑模块
import card_processor
import data_parser

app = FastAPI(
    title="Card Checker API",
    description="Processes card info. Now supports direct file upload!",
    version="5.0.0-fileupload" # 终极版！
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

# --------------------------------------------------------------------
# 【【【 这 是 您 要 的 最 终 功 能 】】】
@app.post("/upload-and-process-file", response_model=List[ProcessResponse], summary="【推荐】直接上传 .txt 文件并处理")
async def upload_and_process_file(
    # 我们告诉 API，这里要接收一个文件
    file: UploadFile = File(...)
):
    """
    直接上传一个 .txt 文件，服务器会自动读取内容，提取格式，并批量处理。
    """
    # 第一步：从上传的文件中读取内容。
    # file.read() 读取的是字节(bytes)，需要用 .decode() 转换成我们能看懂的文本(string)。
    try:
        raw_text = (await file.read()).decode("utf-8")
    except Exception:
        # 如果文件不是UTF-8编码，可能会解码失败，我们返回一个错误提示
        return [{"card": "File Error", "status": "Error", "message": "Could not decode file. Please ensure it is a UTF-8 encoded text file."}]

    # 第二步：调用“打包服务”，从文本中提取出标准格式的卡片列表
    cleaned_cards = data_parser.parse_raw_text(raw_text)

    if not cleaned_cards:
        return []

    # 第三步：循环处理所有被成功提取的卡片
    results = []
    for card in cleaned_cards:
        results.append(card_processor.process_card(card))

    # 第四步：返回包含所有结果的清单
    return results
# --------------------------------------------------------------------

# --- 以下是旧的接口，我们依然保留，为您提供多种选择 ---

@app.post("/extract-and-process", response_model=List[ProcessResponse], summary="处理原始文本 (表单输入)")
def extract_and_process_batch(raw_text: str = Form(...)):
    cleaned_cards = data_parser.parse_raw_text(raw_text)
    if not cleaned_cards:
        return []
    results = []
    for card in cleaned_cards:
        results.append(card_processor.process_card(card))
    return results

@app.post("/extract-only", response_model=List[str], summary="仅从原始文本提取标准格式 (表单输入)")
def extract_format_only(raw_text: str = Form(...)):
    cleaned_cards = data_parser.parse_raw_text(raw_text)
    return cleaned_cards
