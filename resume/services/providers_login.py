# resumes/services/providers_login.py
import requests, time
from django.conf import settings
from .sanitizer import basic_clean

class SessionProvider:
    """
    调用外部改写 API 的 Provider
    登录一次拿 token，之后请求带上 Authorization
    """

    _token = None

    def _login(self):
        if self._token:
            return self._token
        r = requests.post(
            settings.PROVIDER_LOGIN_URL,
            json={
                "username": settings.PROVIDER_USERNAME,
                "password": settings.PROVIDER_PASSWORD,
            },
            timeout=30
        )
        r.raise_for_status()
        self._token = r.json().get("access_token")
        return self._token

    def rewrite(self, raw_text, target_role, job_description, tone):
        start = time.time()
        token = self._login()

        payload = {
            "raw_text": basic_clean(raw_text),
            "target_role": target_role,
            "job_description": job_description,
            "tone": tone,
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = settings.PROVIDER_API_BASE.rstrip("/") + "/v1/rewrite"
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()

        return {
            "text": data.get("text", ""),
            "tokens": data.get("tokens"),
            "latency_ms": int((time.time() - start) * 1000),
        }
