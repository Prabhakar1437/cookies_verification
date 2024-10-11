from django import forms
from .models import UserData
from django.core.exceptions import ValidationError

class UserDataForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(render_value=True), required=False)

    class Meta:
        model = UserData
        fields = ['username', 'password', 'cookies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing an existing instance
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['password'].required = False
            self.initial['password'] = self.instance.get_decoded_password()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not self.instance.pk and UserData.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.pk and not password:
            raise ValidationError('Password is required for new users')
        return password

    def clean_cookies(self):
        cookies = self.cleaned_data.get('cookies')
        if not cookies:
            raise ValidationError('Cookies field cannot be empty')
        return cookies

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk:
            # If editing, only update the cookies field
            instance.cookies = self.cleaned_data['cookies']
            if commit:
                instance.save(update_fields=['cookies'])
        else:
            if commit:
                instance.save()
        return instance