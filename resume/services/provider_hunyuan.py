import time
from django.conf import settings
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

class HunyuanProvider:
    def __init__(self):
        self.cred = credential.Credential(
            settings.TENCENTCLOUD_SECRET_ID,
            settings.TENCENTCLOUD_SECRET_KEY
        )
        self.client = hunyuan_client.HunyuanClient(self.cred, settings.TENCENTCLOUD_REGION)

    def rewrite(self, raw_text, target_role, job_description, tone):
        try:
            start = time.time()
            req = models.ChatCompletionsRequest()
            # prompt 拼接
            prompt = f"请帮我改写以下简历。\n岗位：{target_role}\n岗位要求：{job_description}\n风格：{tone}\n\n【简历原文】\n{raw_text}"

            params = {
                "Model": settings.TENCENTCLOUD_MODEL,
                "Messages": [
                    {"Role": "user", "Content": prompt}
                ]
            }
            req.from_json_string(str(params).replace("'", '"'))

            resp = self.client.ChatCompletions(req)
            latency = int((time.time() - start) * 1000)

            # 从响应里取出文本
            text = resp.Choices[0].Message.Content if resp.Choices else ""

            return {
                "text": text,
                "tokens": resp.Usage.TotalTokens if resp.Usage else None,
                "latency_ms": latency
            }

        except TencentCloudSDKException as e:
            return {"text": f"调用混元失败: {e}", "tokens": None, "latency_ms": None}
