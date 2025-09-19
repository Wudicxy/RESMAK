from django.shortcuts import render
from django.http import JsonResponse
from .forms import PromtForm

def dashboard(request):
    if request.method == 'POST':
        form = PromtForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO: 在这里处理文件上传或文本改写逻辑
            return render(request, 'promt/result.html', {'form': form})
    else:
        form = PromtForm()
    return render(request, 'promt/dashboard.html', {'form': form})

def get_dropdown_data(request):
    data = [
        {"id": 1, "name": "选项1"},
        {"id": 2, "name": "选项2"},
        {"id": 3, "name": "选项3"},
    ]
    return JsonResponse(data, safe=False)
