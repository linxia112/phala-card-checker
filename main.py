# 导入 List 类型，这是支持列表（批量）的关键
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import card_processor

app = FastAPI(
    title="Card Checker API",
    description="An API to process card information. Now supports batch processing.",
    version="2.0.0-batch" # 更新一下版本号
)

# 1. 修改输入模型：现在接收一个字符串列表 (List[str])
# 也就是说，它期望的数据是 ["卡片1", "卡片2", ...]
class CardBatchInput(BaseModel):
    card_data: List[str] = Field(...,
                               description="A list of card strings in 'number|mm|yy|cvc' format.",
                               example=["553680286483249|06|25|504", "4111222233334444|01|27|123"])

# 输出模型保持不变，因为它描述的是单条记录的结果
class ProcessResponse(BaseModel):
    card: str
    status: str
    message: str

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "API is running"}

# 2. 修改 API 端点：
# - 输入类型改为 CardBatchInput
# - 返回类型改为一个包含多个结果的列表：List[ProcessResponse]
@app.post("/process-card", response_model=List[ProcessResponse], summary="Process a batch of cards")
def process_card_batch(card_input: CardBatchInput):
    """
    Receives a batch (list) of card data, processes each one,
    and returns a list of results.
    """
    # 创建一个空列表，用来存放所有结果
    results = []

    # 3. 核心修改：使用 for 循环来处理列表中的每一张卡片
    for card in card_input.card_data:
        # 对每一张卡片，都调用一次我们原来的处理函数
        single_result = card_processor.process_card(card)
        # 将单条结果加入到总的结果列表中
        results.append(single_result)

    # 循环结束后，返回包含所有处理结果的列表
    return results
