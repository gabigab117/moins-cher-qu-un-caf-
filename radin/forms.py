from django import forms
from .models import Confession
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
import sys


class ConfessionForm(forms.ModelForm):
    class Meta:
        model = Confession
        fields = ['body', 'captcha']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'J\'ai réutilisé un filtre à café en le séchant...',
                'rows': 3,
                'maxlength': 280
            }),
        }
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'test' in sys.argv:
            del self.fields['captcha']