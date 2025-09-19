# resume/views_debug.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms_debug import TextOnlyForm
from .models import Resume, RewriteResult
from .services.sanitizer import basic_clean
from .views import get_provider  # 复用你现有的 get_provider()

@login_required
def debug_text_dashboard(request):
    """
    纯文本调试入口：只取 raw_text，验证调用链是否通。
    URL: /debug-text/
    """
    if request.method == 'POST':
        form = TextOnlyForm(request.POST)
        if form.is_valid():
            target_role = form.cleaned_data['target_role']
            job_desc = form.cleaned_data.get('job_description', '')
            tone = form.cleaned_data['tone']
            raw_text = basic_clean(form.cleaned_data['raw_text'])

            if not raw_text.strip():
                messages.error(request, "简历文本不能为空（调试模式）")
                return render(request, 'resumes/debug_text.html', {'form': form})

            # 直接保存简历（无文件）
            resume = Resume.objects.create(
                owner=request.user,
                title=f"Resume-{request.user.username}",
                raw_text=raw_text,
                upload=None
            )

            provider = get_provider()
            try:
                out = provider.rewrite(raw_text, target_role, job_desc, tone)
            except Exception as e:
                messages.error(request, f"改写服务调用失败：{e}")
                return render(request, 'resumes/debug_text.html', {'form': form})

            output_text = (out.get('text') or '').strip()
            import json
            print("DEBUG: provider output:", json.dumps(out, ensure_ascii=False, indent=2))

            if not output_text:
                messages.error(request, "改写结果为空，请稍后重试或更换供应商/模型。")
                return render(request, 'resumes/debug_text.html', {'form': form})

            rr = RewriteResult.objects.create(
                resume=resume,
                target_role=target_role,
                job_description=job_desc,
                tone=tone,
                provider=type(provider).__name__,
                output_text=output_text,
                tokens_used=out.get('tokens'),
                latency_ms=out.get('latency_ms'),
            )
            # 注意命名空间，用你的实际 app_name（大多是 'resumes'）
            return redirect('resumes:result', pk=rr.pk)
    else:
        form = TextOnlyForm()

    return render(request, 'resumes/debug_text.html', {'form': form})
