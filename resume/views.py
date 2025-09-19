# resume/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile

from logger.conf import settings
from .forms import UploadResumeForm
from .models import Resume, RewriteResult
from .services.provider_cn import CNProvider
from .services.sanitizer import basic_clean
from .services.provider_ali import AliyunQwenProvider
from .utils import extract_text_from_upload

def get_provider():
    return AliyunQwenProvider()
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    def _debug_ctx():
        try:
            view_name = request.resolver_match.view_name
        except Exception:
            view_name = ""
        return {
            "show": settings.DEBUG and request.method == "POST",
            "path": request.path,
            "method": request.method,
            "view_name": view_name,
            "post_keys": list(request.POST.keys()),
            "file_keys": list(request.FILES.keys()),
        }

    if request.method == 'POST':
        logger.info("POST to dashboard: path=%s view=%s post_keys=%s file_keys=%s",
                    request.path,
                    getattr(request.resolver_match, "view_name", ""),
                    list(request.POST.keys()),
                    list(request.FILES.keys()))

        form = UploadResumeForm(request.POST, request.FILES)

        if form.is_valid():
            target_role = form.cleaned_data['target_role']
            job_desc = form.cleaned_data.get('job_description', '')
            tone = form.cleaned_data['tone']
            # ⭐ 防空兜底
            raw_text = basic_clean(form.cleaned_data.get('raw_text') or '')

            upload_file = form.cleaned_data.get('resume_file')
            if upload_file and not raw_text:
                # 读取文本
                raw_text = extract_text_from_upload(upload_file) or ''
                # 关键：复位文件指针
                if hasattr(upload_file, "seek"):
                    try:
                        upload_file.seek(0)
                    except Exception:
                        pass

            if not raw_text.strip():
                messages.error(request, "读取简历内容失败，请粘贴文本或上传 PDF/DOCX/TXT。")
                return render(request, 'resumes/dashboard.html',
                              {'form': form, 'debug': _debug_ctx()})

            # 可选：成功后再落库，避免孤儿记录
            resume = Resume.objects.create(
                owner=request.user,
                title=f"Resume-{request.user.username}",
                raw_text=raw_text,
                upload=upload_file
            )

            provider = get_provider()
            try:
                out = provider.rewrite(raw_text, target_role, job_desc, tone)
            except Exception as e:
                logger.exception("Provider rewrite failed: %s", e)
                messages.error(request, f"改写服务暂不可用：{e}")
                return render(request, 'resumes/dashboard.html',
                              {'form': form, 'debug': _debug_ctx()})

            output_text = (out or {}).get('text') or ''
            if not output_text.strip():
                messages.error(request, "改写结果为空，请稍后重试或更换模型/供应商。")
                return render(request, 'resumes/dashboard.html',
                              {'form': form, 'debug': _debug_ctx()})

            rr = RewriteResult.objects.create(
                resume=resume,
                target_role=target_role,
                job_description=job_desc,
                tone=tone,
                provider=type(provider).__name__,
                output_text=output_text,
                tokens_used=(out or {}).get('tokens'),
                latency_ms=(out or {}).get('latency_ms'),
            )
            return redirect('resumes:result', pk=rr.pk)

        else:
            logger.warning("Form invalid: %s", form.errors)
            messages.error(request, "表单校验失败，请检查必填项与格式。")
            return render(request, 'resumes/dashboard.html',
                          {'form': form, 'debug': _debug_ctx()})

    else:
        form = UploadResumeForm()

    return render(request, 'resumes/dashboard.html',
                  {'form': form, 'debug': {"show": False}})

@login_required
def result(request, pk: int):
    rr = get_object_or_404(
        RewriteResult.objects.select_related('resume'),
        pk=pk,
        resume__owner=request.user
    )
    return render(request, 'resumes/result.html', {'rr': rr})


@login_required
def resume_history(request):
    # 查询当前用户的所有改写记录，按时间倒序
    results = RewriteResult.objects.filter(resume__owner=request.user).order_by('-created_at')

    # 面包屑数据（在视图里准备）
    breadcrumb_items = [
        {'url': '', 'label': '历史记录'}
    ]

    return render(request, 'resumes/history.html', {
        'results': results,
        'breadcrumb_items': breadcrumb_items
    })

@login_required
def resume_detail(request, resume_id):
    """
    展示单条简历的改写历史
    """
    resume = get_object_or_404(Resume, pk=resume_id, owner=request.user)
    results = resume.results.all().order_by('-created_at')
    return render(request, 'resumes/detail.html', {
        'resume': resume,
        'results': results
    })

@login_required
def rewrite_result_detail(request, result_id):
    """
    展示某条改写记录的详细内容
    """
    result = get_object_or_404(RewriteResult, pk=result_id, resume__owner=request.user)
    return render(request, 'resumes/result_detail.html', {'result': result})