from django import forms
from .models import Confession


class ConfessionForm(forms.ModelForm):
    # Champ honeypot - invisible pour les humains, mais les bots le remplissent
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none !important;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = Confession
        fields = ['body', 'website']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'J\'ai réutilisé un filtre à café en le séchant...',
                'rows': 3,
                'maxlength': 280
            }),
        }
    
    def clean_website(self):
        """Si le champ honeypot est rempli, c'est un bot"""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError("Spam détecté")
        return website