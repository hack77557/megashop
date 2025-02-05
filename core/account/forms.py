from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput

User = get_user_model()

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        # Додаємо додаткові поля: зверніть увагу, що ви можете змінити набір полів за потребою
        fields = (
            'username',
            'email',
            'middle_name',
            'phone',
            'date_of_birth',
            'sex',
            'language',
            'password1',
            'password2'
        )

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Your Email Address'
        self.fields['email'].required = True
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists() or len(email) > 254:
            raise forms.ValidationError("Email already exists or is too long")
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        # Додаємо як базові, так і додаткові поля для редагування профілю.
        fields = ['username', 'email', 'middle_name', 'phone', 'date_of_birth', 'sex', 'language']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Your Email Address'
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists() or len(email) > 254:
            raise forms.ValidationError("Email already in use or is too long")
        return email
