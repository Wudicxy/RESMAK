from django import forms

class PromtForm(forms.Form):
    target_role = forms.CharField(max_length=100, label="应聘岗位")
    job_description = forms.CharField(widget=forms.Textarea, label="岗位要求（JD）")
    tone = forms.ChoiceField(
        choices=[('formal', '正式'), ('casual', '轻松')],
        label="风格"
    )
    custom_dropdown = forms.CharField(
        max_length=100, required=False, label="自定义下拉框"
    )
    resume_file = forms.FileField(required=False, label="上传简历（PDF / DOCX / TXT）")
    raw_text = forms.CharField(widget=forms.Textarea, required=False, label="粘贴简历文本")
