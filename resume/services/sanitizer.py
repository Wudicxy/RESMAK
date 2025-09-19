def basic_clean(text: str | None) -> str:
    if not text:
        return ''
    # 去 BOM、替换奇怪空格等
    text = text.replace('\ufeff', '').strip()
    return text