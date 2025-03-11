'''
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django_email_verification import send_email

from .forms import UserCreateForm, UserLoginForm, UserUpdateForm

# type hinting
from django.http import HttpRequest


User = get_user_model()


from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate, logout


# FIXME: fix and refactor account app, implement additional functionality

# NOTE: accounts templates stored in (that you can use if you name your app accounts): django\contrib\admin\templates\registration
 # but I am make custom template for password resetting

# Register new user
def register_user(request: HttpRequest):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_email = form.cleaned_data.get('email')
            user_username = form.cleaned_data.get('username')
            user_password = form.cleaned_data.get('password1')
            
            # Create new user
            user = User.objects.create_user(
                username=user_username, email=user_email, password=user_password
            )
            
            user.is_active = False
            
            send_email(user)
            
            return redirect('/account/email-verification-sent/')
    else:
        form = UserCreateForm()
    return render(request, 'account/registration/register.html', {'form': form}) 


def login_user(request: HttpRequest):
    form = UserLoginForm()
    
    if request.user.is_authenticated:
        return redirect('shop:products')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request=request, user=user)
            return redirect('account:dashboard')
        else:
            messages.info(request, "Username or Password is incorrect")
            return redirect('account:login')

    context = {'form': form}
    return render(request, 'account/login/login.html', context)


def logout_user(request: HttpRequest):
    logout(request)
    return redirect('shop:products')


# Dashboard
@login_required(login_url='account:login')
def dashboard_user(request: HttpRequest):
    return render(request, 'account/dashboard/dashboard.html')


@login_required(login_url='account:login')
def profile_user_management(request: HttpRequest):

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('account:dashboard')
    else:
        form = UserUpdateForm(instance=request.user)
        
    context = {'form': form}
    return render(request, 'account/dashboard/profile_management.html', context)
    


@login_required(login_url='account:login')
def delete_user(request: HttpRequest):
    user = User.objects.filter(id=request.user.id)
    if request.method == 'POST':
        user.delete()
        return redirect('shop:products')
    
    return render(request, 'account/dashboard/account_delete.html')




'''
'''
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
'''
'''
from rest_framework.permissions import AllowAny

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    user.refresh_token = str(refresh)  # Зберігаємо refresh-токен
    user.save()
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class LoginView(APIView):
    permission_classes = [AllowAny]  # ✅ Дозволяємо всім доступ

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # ✅ Логін користувача в систему
            tokens = get_tokens_for_user(user)
            
            response = JsonResponse({"message": "Login successful"})
            response.set_cookie("access_token", tokens["access"], httponly=True, secure=False, samesite="Strict")
            response.set_cookie("refresh_token", tokens["refresh"], httponly=True, secure=False, samesite="Strict")
            return response

        return JsonResponse({"error": "Invalid credentials"}, status=401)

class LogoutView(APIView):
    def post(self, request):
        user = request.user
        user.refresh_token = None  # Видаляємо refresh-токен
        user.save()

        response = JsonResponse({"message": "Logged out"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
class UserView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]  # ✅ Додаємо аутентифікацію
    permission_classes = [IsAuthenticated]  # ✅ Доступ тільки для авторизованих

    def get(self, request):
        user = request.user
        return Response({"username": user.username, "role": "admin" if user.is_staff else "user"})
    
class UserView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return JsonResponse({"username": user.username, "role": getattr(user, "role", "user")})'
'''
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django_email_verification import send_email
from django.http import HttpRequest, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

# ------------------------------
# 🔹 Класичні Django Views
# ------------------------------

def register_user(request: HttpRequest):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_email = form.cleaned_data.get('email')
            user_username = form.cleaned_data.get('username')
            user_password = form.cleaned_data.get('password1')
            
            # Create new user
            user = User.objects.create_user(
                username=user_username, email=user_email, password=user_password
            )
            user.is_active = False
            send_email(user)
            
            return redirect('/account/email-verification-sent/')
    else:
        form = UserCreateForm()
    return render(request, 'account/registration/register.html', {'form': form})


def login_user(request: HttpRequest):
    form = UserLoginForm()
    
    if request.user.is_authenticated:
        return redirect('shop:products')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request=request, user=user)
            return redirect('account:dashboard')
        else:
            messages.info(request, "Username or Password is incorrect")
            return redirect('account:login')

    context = {'form': form}
    return render(request, 'account/login/login.html', context)


def logout_user(request: HttpRequest):
    logout(request)
    return redirect('shop:products')


@login_required(login_url='account:login')
def dashboard_user(request: HttpRequest):
    return render(request, 'account/dashboard/dashboard.html')


@login_required(login_url='account:login')
def profile_user_management(request: HttpRequest):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('account:dashboard')
    else:
        form = UserUpdateForm(instance=request.user)
        
    context = {'form': form}
    return render(request, 'account/dashboard/profile_management.html', context)


@login_required(login_url='account:login')
def delete_user(request: HttpRequest):
    user = User.objects.filter(id=request.user.id)
    if request.method == 'POST':
        user.delete()
        return redirect('shop:products')
    
    return render(request, 'account/dashboard/account_delete.html')

# ------------------------------
# 🔹 REST API Views
# ------------------------------

# ✅ Функція генерації токенів та збереження refresh у БД
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    user.refresh_token = str(refresh)  # Зберігаємо refresh-токен
    user.save()
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginView(APIView):
    """
    Логін користувача через API, встановлює HttpOnly cookies.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Ім'я користувача"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль"),
            },
        ),
        responses={201: "Login successful"},
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # Логін користувача в систему
            tokens = get_tokens_for_user(user)

            response = JsonResponse({"message": "Login successful"})
            response.set_cookie("access_token", tokens["access"], httponly=True, secure=False, samesite="Strict")
            response.set_cookie("refresh_token", tokens["refresh"], httponly=True, secure=False, samesite="Strict")
            return response

        return JsonResponse({"error": "Invalid credentials"}, status=401)

# ✅ Логаут: Видалення токенів
class LogoutView(APIView):
    """
    Вихід користувача, видаляє HttpOnly cookies.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={201: "Logged out"}
    )
    def post(self, request):
        user = request.user
        user.refresh_token = None  # Видаляємо refresh-токен
        user.save()

        response = JsonResponse({"message": "Logged out"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class UserView(APIView):
    """
    Отримання інформації про автентифікованого користувача.
    """
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Ім'я користувача"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Електронна пошта"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, description="Роль користувача"),
            },
        )}
    )
    # ✅ Отримання інформації про користувача
    class UserView(APIView):
        authentication_classes = [SessionAuthentication, JWTAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            user = request.user
            return Response({"username": user.username, "role": "admin" if user.is_staff else "user"})
'''
class UserView(APIView):
    """
    Отримання інформації про автентифікованого користувача.
    """
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Ім'я користувача"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Електронна пошта"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, description="Роль користувача"),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="Ім'я"),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="Прізвище"),
                "middle_name": openapi.Schema(type=openapi.TYPE_STRING, description="По-батькові"),
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="Телефон"),
                "date_of_birth": openapi.Schema(type=openapi.TYPE_STRING, format="date", description="Дата народження"),
                "sex": openapi.Schema(type=openapi.TYPE_STRING, description="Стать"),
                "language": openapi.Schema(type=openapi.TYPE_STRING, description="Мова"),
                "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Чи є користувач адміністратором"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Чи активний обліковий запис"),
                "date_joined": openapi.Schema(type=openapi.TYPE_STRING, format="date-time", description="Дата реєстрації"),
            },
        )}
    )
    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "middle_name": user.middle_name,
            "phone": user.phone,
            "date_of_birth": user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else None,
            "sex": user.sex,
            "language": user.language,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
        })
'''



# ✅ Оновлення JWT-токена через HttpOnly cookies
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh-токен"),
            },
        ),
        responses={200: "Token refreshed", 401: "Invalid refresh token"},
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return JsonResponse({"error": "Refresh token required"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            response = JsonResponse({"message": "Token refreshed"})
            response.set_cookie("access_token", new_access_token, httponly=True, secure=False, samesite="Strict")
            return response
        except Exception:
            return JsonResponse({"error": "Invalid refresh token"}, status=401)

from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GetCSRFToken(APIView):
    """
    Отримати CSRF-токен.
    """
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Отримати CSRF-токен для захищених POST-запитів.",
        responses={
            200: openapi.Response(
                description="CSRF-токен успішно отримано",
                examples={"application/json": {"csrfToken": "your-csrf-token"}},
            )
        },
    )
    def get(self, request):
        """
        Генерує та повертає CSRF-токен у JSON-форматі.
        """
        return JsonResponse({"csrfToken": get_token(request)})