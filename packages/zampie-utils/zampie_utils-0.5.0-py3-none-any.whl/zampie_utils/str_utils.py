import re

def find_emojis(response):
    """
    匹配 emoji
    """

    emoji_pattern = re.compile(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F"
        r"\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F"
        r"\U0001FA70-\U0001FAFF\U00002640\U00002642]",  # 添加 U+2640 和 U+2642 范围
        flags=re.UNICODE,
    )

    emojis = emoji_pattern.findall(response)
    return emojis


def find_expressings(response):
    """
    匹配 emoji
    """

    expression_pattern = re.compile(r"<.*?>")

    # 查找匹配项
    expressions = expression_pattern.findall(response)
    return expressions


def remove_blank_lines(dialog):
    """
    Args:
        dialog: str, dialog content
    """
    dialog = dialog.strip()
    dialog_list = []
    for line in dialog.split("\n"):
        if not line:
            continue
        dialog_list.append(line)

    dialog = "\n".join(dialog_list)

    return dialog


def find_chinese(text):
    """
    提取文本中的中文字符
    
    Args:
        text: str, 输入文本
        
    Returns:
        list: 包含所有中文字符的列表
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+', flags=re.UNICODE)
    chinese_chars = chinese_pattern.findall(text)
    return "".join(chinese_chars)
