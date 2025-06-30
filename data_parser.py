import re
from typing import List

# 这个函数接收一大段包含多行信息的原始文本作为输入
def parse_raw_text(raw_text: str) -> List[str]:
    """
    Parses a block of raw text to find and format credit card information.
    """
    # 这个正则表达式是为了从复杂的行中精确匹配 卡号|月|年|CVC 格式
    # 它会寻找15或16位数字，然后跳过一些非数字字符去寻找月、年、CVC
    pattern = r'(\d{15,16})[^\d\n]*?(\d{1,2})[^\d\n]*?(\d{2,4})[^\d\n]*?(\d{3,4})'

    # 使用集合(set)来自动处理重复的卡片
    cards = set()

    # 将输入的长文本按行分割，然后逐行处理
    for line in raw_text.strip().splitlines():
        # 在每一行里查找所有匹配项
        matches = re.findall(pattern, line)
        for match in matches:
            # match 会是 (卡号, 月份, 年份, CVC)
            card_number, month, year, cvv = match

            # 确保月份是两位数，例如 7 -> 07
            month = month.zfill(2)

            # 确保年份是两位数，例如 2025 -> 25
            if len(year) == 4:
                year = year[-2:]
            elif len(year) != 2:
                continue  # 如果年份格式不正确，就跳过这条记录

            # 组合成我们 API 需要的标准格式
            card_info = f"{card_number}|{month}|{year}|{cvv}"
            cards.add(card_info)

    # 将处理好的、不重复的卡片列表返回
    return list(cards)

