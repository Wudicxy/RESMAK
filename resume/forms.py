# resumes/forms.py
from django import forms

class UploadResumeForm(forms.Form):
    target_role = forms.CharField(max_length=120, label='应聘岗位')
    job_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}), required=False, label='岗位要求')
    resume_file = forms.FileField(required=False, label='上传简历文件（PDF/DOCX/TXT）')
    raw_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 12}), required=False, label='或直接粘贴文本')
    tone = forms.ChoiceField(
        choices=[('professional','Professional'), ('concise','Concise'), ('impactful','Impactful')],
        label='风格'
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('resume_file') and not cleaned.get('raw_text'):
            raise forms.ValidationError("请上传简历文件或粘贴文本")
        return cleaned
