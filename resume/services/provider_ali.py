import os
import time
from django.conf import settings
from dashscope import Generation
from http import HTTPStatus

class AliyunQwenProvider:
    """
    使用阿里 DashScope 官方 SDK 调用 Qwen 模型进行简历改写
    """
    def __init__(self):
        self.api_key = getattr(settings, "ALI_API_KEY", os.getenv("ALI_API_KEY"))
        self.model   = getattr(settings, "ALI_MODEL", os.getenv("ALI_MODEL", "qwen-plus"))

    def rewrite(self, raw_text, target_role, job_description, tone):
        """
        改写简历文本
        """
        start = time.time()

        prompt_text = f"""你是一个专业的简历优化助手。
请根据以下信息改写简历，使其更符合岗位要求，并保持原意：
岗位信息: {target_role}
岗位职责: {job_description}
风格: {tone}

【个人经历】:
{raw_text}

请遵循以下要求：
1. 强调与岗位匹配的技能和成就。
2. 每条经历至少包含一个量化成果。
3. 避免重复表达，每条经历简洁明了。
4. 语言正式、专业，中文/英文根据用户选择。
5. 输出格式为条目列表，方便直接放入简历模板。
"""

        # 使用 messages 风格调用官方 SDK
        messages = [
            {"role": "system", "content": "你是一个简历优化助手。"},
            {"role": "user", "content": prompt_text}
        ]

        try:
            # 调用官方 Generation API
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message",  # 返回 message 对象，带 role + content
                api_key=self.api_key
            )

            # 检查返回状态
            if response.status_code != HTTPStatus.OK:
                return {
                    "error": f"{response.code}: {response.message}",
                    "latency_ms": int((time.time()-start)*1000)
                }

            # 提取文本
            reply = response.output.choices[0].message
            text = reply.content.strip()

            # fallback: 如果 messages 返回空，用 prompt 风格
            if not text:
                fallback = Generation.call(
                    model=self.model,
                    prompt=prompt_text,
                    result_format="text",  # 纯文本输出
                    api_key=self.api_key
                )
                if fallback.status_code == HTTPStatus.OK:
                    text = fallback.output.strip()
                    print("Fallback prompt response:", text)
                else:
                    return {
                        "error": f"Fallback failed: {fallback.code}: {fallback.message}",
                        "latency_ms": int((time.time()-start)*1000)
                    }

        except Exception as e:
            return {
                "error": str(e),
                "latency_ms": int((time.time()-start)*1000)
            }

        return {
            "text": text,
            "tokens": getattr(response, "usage", {}).get("total_tokens"),
            "latency_ms": int((time.time()-start)*1000)
        }
