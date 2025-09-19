# resumes/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import RewriteJob
from .services.providers_login import SessionProvider
from .services.sanitizer import basic_clean

@require_GET
@login_required
def job_status(request, job_id):
    try:
        job = RewriteJob.objects.get(pk=job_id)
    except RewriteJob.DoesNotExist:
        raise Http404

    if job.owner_id != request.user.id:
        return HttpResponseForbidden("Forbidden")

    data = {
        "status": job.status,
        "progress": job.progress,
        "error": job.error,
        "result_id": job.result_id,
        "done": job.status == RewriteJob.Status.DONE,
        "failed": job.status == RewriteJob.Status.FAILED,
        "result_url": (f"/resumes/result/{job.result_id}/" if job.result_id else None),
    }
    return JsonResponse(data)
class RewriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        target_role = payload.get("target_role", "")
        job_desc = payload.get("job_description", "")
        raw_text = basic_clean(payload.get("raw_text", ""))
        tone = payload.get("tone", "professional")

        if not raw_text:
            return Response(
                {"detail": "raw_text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider = SessionProvider()
        out = provider.rewrite(raw_text, target_role, job_desc, tone)
        return Response(out, status=status.HTTP_200_OK)
