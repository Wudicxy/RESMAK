# resumes/services/providers.py
import time
from dataclasses import dataclass
from .provider_hunyuan import HunyuanProvider
@dataclass
class ProviderOutput:
    text: str
    tokens: int | None = None
    latency_ms: int | None = None

class RewriteProvider:
    def rewrite(self, raw_text: str, target_role: str, job_desc: str, tone: str) -> dict:
        raise NotImplementedError

class DummyRewriteProvider(RewriteProvider):
    def rewrite(self, raw_text: str, target_role: str, job_desc: str, tone: str) -> dict:
        start = time.time()
        # 这里简单拼接模拟一下
        new_text = f"""# Rewritten Resume ({tone})
Target Role: {target_role}

Matched Requirements:
{job_desc or '(No JD provided)'}

==== Polished Resume ====
{raw_text}
"""
        return {
            "text": new_text,
            "tokens": len(raw_text.split()),
            "latency_ms": int((time.time() - start) * 1000)
        }

def get_provider():
    return HunyuanProvider()


def basic_clean(text: str | None) -> str:
    if not text:
        return ''
    # 去 BOM、替换奇怪空格等
    text = text.replace('\ufeff', '').strip()
    return text