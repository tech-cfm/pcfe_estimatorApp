from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import login_view, logout_view

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('calculate/', views.calculate_view, name='calculate'),
    path('visualise/', views.data_visualisation, name='visualise'),
    path('global-footprint/', views.get_global_footprint_data, name='global_footprint'),
    
]
