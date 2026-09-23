from django import forms
from datetime import datetime, date
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import datetime



CURRENT_YEAR = datetime.datetime.now().year
YEAR_CHOICES = [(year, year) for year in range(1900, CURRENT_YEAR + 1)]



class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username","first_name","last_name","email","password",]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")

        return cleaned_data



class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "autocomplete": "email"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "autocomplete": "current-password"
            }
        )
    )
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "Invalid email or password."
                )

            user = authenticate(
                username=user.username,
                password=password
            )

            if user is None:
                raise forms.ValidationError(
                    "Invalid email or password."
                )

            if not user.is_active:
                raise forms.ValidationError(
                    "This account is inactive."
                )
            cleaned_data["user"] = user
        return cleaned_data