"""gazette_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from gazette_backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view()),
    path('token/', obtain_auth_token, name='token'),
    path('user/check/', views.check_user),
    path('user/handle/', views.handle_user),
    path('user/delete/<int:pk>', views.delete_user),
    path('lost_password/<str:cred>', views.lost_password),
    path('editions/list/', views.editions_list),
    path('editions/add/', views.editions_add),
    path('editions/publish/<int:pk>', views.editions_publish),
    path('articles/list/<int:pk>', views.articles_list),
    path('tasks/list/<int:pk>', views.tasks_list),
    path('articles/add/', views.articles_add),
    path('articles/edit/<int:pk>', views.articles_edit),
    path('articles/permission/<int:pk>', views.articles_perm)
]
