# 敏感词列表
SENSITIVE_WORDS = ['傻福', 'nm', 'tm','你妈','cn','sb','傻逼','纱布','操你','狗日']

def contains_sensitive_words(text):
    """检查文本是否包含敏感词"""
    for word in SENSITIVE_WORDS:
        if word in text:
            return True
    return False
