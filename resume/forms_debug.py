from django import forms

class TextOnlyForm(forms.Form):
    target_role = forms.CharField(
        max_length=120, label='应聘岗位',
        widget=forms.TextInput(attrs={"class": "input"})
    )
    job_description = forms.CharField(
        required=False, label='岗位要求',
        widget=forms.Textarea(attrs={"rows": 6, "class": "input input--textarea"})
    )
    raw_text = forms.CharField(
        required=True, label='简历文本（必填，仅调试）',
        widget=forms.Textarea(attrs={"rows": 16, "class": "input input--textarea input--tall"})
    )
    tone = forms.ChoiceField(
        choices=[('professional','Professional'), ('concise','Concise'), ('impactful','Impactful')],
        initial='professional', label='风格',
        widget=forms.Select(attrs={"class": "select"})
    )
