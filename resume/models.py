from django.db import models
from django.conf import settings
# resumes/models.py
import uuid
from django.conf import settings
from django.db import models

class RewriteJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        DONE   = "done",   "Done"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rewrite_jobs")
    resume = models.ForeignKey("Resume", on_delete=models.CASCADE, related_name="jobs", null=True, blank=True)
    result = models.OneToOneField("RewriteResult", on_delete=models.SET_NULL, null=True, blank=True, related_name="job")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    progress = models.PositiveIntegerField(default=0)  # 0~100
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def bump(self, pct):
        self.progress = max(self.progress, min(int(pct), 99))
        self.save(update_fields=["progress", "updated_at"])

class Resume(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default='My Resume')
    raw_text = models.TextField(blank=True, default='')
    upload = models.FileField(upload_to='uploads/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.owner})"

class RewriteResult(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='results')
    target_role = models.CharField(max_length=120)
    job_description = models.TextField(blank=True, default='')
    tone = models.CharField(max_length=32, default='professional')
    provider = models.CharField(max_length=128, default='DummyProvider')
    output_text = models.TextField()
    tokens_used = models.IntegerField(blank=True, null=True)
    latency_ms = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)