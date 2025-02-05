
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Створює і зберігає звичайного користувача з заданими username, email та password.
        """
        if not username:
            raise ValueError("Username повинен бути вказаний")
        if not email:
            raise ValueError("Email повинен бути вказаний")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Створює і зберігає суперкористувача з заданими username, email та password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперкористувач повинен мати is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперкористувач повинен мати is_superuser=True")
        
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("Username", max_length=150, unique=True)
    email = models.EmailField("Email Address", max_length=254, unique=True)

    # Додаткові поля
    middle_name = models.CharField("По-батькові", max_length=30, blank=True, null=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    date_of_birth = models.DateField("Дата народження", blank=True, null=True)
    SEX_CHOICES = (
        ('male', 'Чоловік'),
        ('female', 'Жінка'),
    )
    sex = models.CharField("Стать", max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    language = models.CharField("Мова", max_length=20, blank=True, null=True)

    # Додаткові поля для імені користувача (якщо потрібно)
    first_name = models.CharField("Ім'я", max_length=30, blank=True)
    last_name = models.CharField("Прізвище", max_length=150, blank=True)

    # Поля, необхідні для роботи адміністративного інтерфейсу
    is_staff = models.BooleanField("Персонал", default=False, help_text="Може увійти в адмін-панель")
    is_active = models.BooleanField("Активований", default=True)
    date_joined = models.DateTimeField("Дата реєстрації", default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # email є обов'язковим; при потребі можна додати інші

    def __str__(self):
        return self.username
