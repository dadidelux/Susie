from django import forms

class QuestionForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea(attrs={'class': 'materialize-textarea', 'data-length': '120', 'placeholder': 'Ask any question:'}))
