# resumes/services/provider_cn.py
import os, time, requests

class CNProvider:
    def __init__(self, vendor="hunyuan"):
        self.vendor = vendor
        self.api_key = os.getenv("LLM_API_KEY")  # 在 .env 或系统环境里配置
        self.model = os.getenv("LLM_MODEL", "")
        if vendor == "hunyuan":
            self.base = "hunyuan.tencentcloudapi.com"
            self.path = "/v1/chat/completions"   # 具体以官方 SDK/文档为准
        elif vendor == "zhipu":
            self.base = "https://open.bigmodel.cn/api/paas/v4"
            self.path = "/chat/completions"
        elif vendor == "doubao":
            self.base = "https://ark.cn-beijing.volces.com/api/v3"
            self.path = "/chat/completions"
        else:
            raise ValueError("Unsupported vendor")

    def rewrite(self, raw_text, target_role, job_desc, tone):
        start = time.time()
        prompt = f"请基于以下信息改写简历：岗位={target_role}；JD={job_desc}；风格={tone}\n\n【简历原文】\n{raw_text}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        body = {
            "model": self.model,
            "messages":[{"role":"user","content":prompt}]
        }
        r = requests.post(self.base + self.path, json=body, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        # 各家返回结构略有差异，取常见字段
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or data.get("output_text","")
        return {"text": text, "tokens": data.get("usage", {}).get("total_tokens"), "latency_ms": int((time.time()-start)*1000)}
