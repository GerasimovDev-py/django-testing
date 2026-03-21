from django import forms
from .models import Comment

BAD_WORDS = ['редиска', 'негодяй', 'подлец']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']
        for word in BAD_WORDS:
            if word in text.lower():
                raise forms.ValidationError(
                    f'Обнаружено запрещённое слово: {word}'
                )
        return text
