from django import forms

class ReportForm(forms.Form):
    title = forms.CharField(label="주제", max_length=30, required=True)
    content = forms.CharField(label="내용", max_length=400, required=True, widget=forms.Textarea)

    def clean(self):
        clean_data=super().clean()
        # This method will set the cleaned_data attribute
        title = clean_data.get('title')
        content = clean_data.get('content')
        return self.cleaned_data