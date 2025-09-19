# resumes/tasks.py
from celery import shared_task
from django.db import transaction
from django.urls import reverse
from .models import RewriteJob, Resume, RewriteResult
from .services.provider_ali import AliyunQwenProvider
from .services.sanitizer import basic_clean

def get_provider():
    return AliyunQwenProvider()

@shared_task(bind=True)
def run_rewrite_job(self, job_id, payload):
    """
    payload = {
      "owner_id": ...,
      "raw_text": ...,
      "upload_file_path": optional,
      "target_role": ...,
      "job_desc": ...,
      "tone": ...
    }
    """
    job = RewriteJob.objects.select_for_update().get(pk=job_id)
    try:
        job.status = RewriteJob.Status.RUNNING
        job.progress = 5
        job.save(update_fields=["status", "progress", "updated_at"])

        raw_text = basic_clean(payload.get("raw_text") or "")
        if not raw_text.strip():
            raise ValueError("Empty raw_text after clean.")

        # 10%：准备 provider
        provider = get_provider()
        job.bump(10)

        # 20%~90%：调用改写（你也可以在 provider 内加回调实时上报进度）
        out = provider.rewrite(
            raw_text,
            payload["target_role"],
            payload.get("job_desc", ""),
            payload.get("tone")
        )
        job.bump(85)

        output_text = (out or {}).get("text") or ""
        if not output_text.strip():
            raise ValueError("Provider returned empty text.")

        # 90%：落库结果
        with transaction.atomic():
            resume = Resume.objects.get(pk=payload["resume_id"])
            rr = RewriteResult.objects.create(
                resume=resume,
                target_role=payload["target_role"],
                job_description=payload.get("job_desc", ""),
                tone=payload.get("tone"),
                provider=type(provider).__name__,
                output_text=output_text,
                tokens_used=(out or {}).get("tokens"),
                latency_ms=(out or {}).get("latency_ms"),
            )
            job.result = rr
            job.progress = 100
            job.status = RewriteJob.Status.DONE
            job.save(update_fields=["result", "progress", "status", "updated_at"])

        return {"ok": True, "result_id": rr.pk}
    except Exception as e:
        job.status = RewriteJob.Status.FAILED
        job.error = str(e)
        job.save(update_fields=["status", "error", "updated_at"])
        raise
