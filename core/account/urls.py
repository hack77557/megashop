'''
from django.urls import path, reverse_lazy
from django.shortcuts import render
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'



from django.urls import path
#from .views import MyTokenObtainPairView




urlpatterns = [
    # Registration and Verification
    path('register/', views.register_user, name='register'),
    path(
        route='email-verification-sent/',
        view=lambda request: render(request, 'account/email/email_verification_sent.html'),
        name='email-verification-sent'
    ),
    # Login and Logout
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_user, name='dashboard'),
    path('profile-management/', views.profile_user_management, name='profile-management'),
    path('delete-user/', views.delete_user, name='delete-user'),
    
    # Password reset
    path(
        'password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='account/password/password_reset.html',
            email_template_name='account/password/password_reset_email.html',
            success_url=reverse_lazy('account:password-reset-done'),
        ), 
        name='password-reset'
    ),
    path(
        'password-reset-done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='account/password/password_reset_done.html',
        ), 
        name='password-reset-done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='account/password/password_reset_confirm.html',
            success_url=reverse_lazy('account:password-reset-complete'),
        ), 
        name='password-reset-confirm'
    ),
    path(
        'password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='account/password/password_reset_complete.html',
        ), 
        name='password-reset-complete'
    ),
    #path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]

'''


from django.urls import path, reverse_lazy, include
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from . import views
from account.views import LoginView, LogoutView, UserView, RefreshTokenView, GetCSRFToken



app_name = 'account'

urlpatterns = [
    # 🔹 Стандартні маршрути для аутентифікації
    path('register/', views.register_user, name='register'),
    path(
        'email-verification-sent/',
        lambda request: render(request, 'account/email/email_verification_sent.html'),
        name='email-verification-sent'
    ),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # 🔹 JWT API Маршрути (для аутентифікації через API)
    #path('api/login/', LoginView.as_view(), name='api-login'),   # ✅ API логін
    #path('api/logout/', LogoutView.as_view(), name='api-logout'), # ✅ API логаут
    #path('api/user/', UserView.as_view(), name='api-user-info'),  # ✅ API Отримання даних про користувача
    # ✅ Аутентифікація через HttpOnly cookies
    path("api/login/", LoginView.as_view(), name="account_api_login_create"),# ✅ API логін
    path("api/logout/", LogoutView.as_view(), name="account_api_logout_create"),# ✅ API логаут
    path("api/user/", UserView.as_view(), name="account_api_user_list"),# ✅ API Отримання даних про користувача
    path("api/token/refresh/", RefreshTokenView.as_view(), name="account_api_token_refresh"),
    path("api/csrf/", GetCSRFToken.as_view(), name="csrf-token"),
    # ✅ Підключення Djoser (реєстрація, зміна пароля, управління профілем)
    path("api/", include("djoser.urls")),


    # 🔹 Dashboard та управління акаунтом
    path('dashboard/', views.dashboard_user, name='dashboard'),
    path('profile-management/', views.profile_user_management, name='profile-management'),
    path('delete-user/', views.delete_user, name='delete-user'),

    # 🔹 Скидання пароля
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='account/password/password_reset.html',
            email_template_name='account/password/password_reset_email.html',
            success_url=reverse_lazy('account:password-reset-done'),
        ),
        name='password-reset'
    ),
    path(
        'password-reset-done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='account/password/password_reset_done.html',
        ),
        name='password-reset-done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='account/password/password_reset_confirm.html',
            success_url=reverse_lazy('account:password-reset-complete'),
        ),
        name='password-reset-confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='account/password/password_reset_complete.html',
        ),
        name='password-reset-complete'
    ),
]
