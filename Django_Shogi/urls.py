"""
URL configuration for Django_Shogi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from Shogi import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Shogi API",
      default_version='v1',
      description="Rules, Register, Login, Logout and CRUD, join, move of Shogi game API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@shogi.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('reset/', views.reset_session, name='reset_session'),
    path('game/', views.game_board, name='game_board'),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('game/<uuid:uid>/', views.game_socket, name='game_socket'),
    path('api/rules/', views.RuleAPIView.as_view(), name='api-rules'),
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
    path('api/check-login/', views.CheckLoginStatusView.as_view(), name='check-login'),
    path('api/player/<str:username>/', views.PlayerView.as_view(), name='player-detail-by-username'),
    path('api/game/', views.GameCreateView.as_view(), name='game-create'),
    path('api/games/', views.GameListView.as_view(), name='game-list'),
    path('api/games/<uuid:uid>/', views.GameDetailDeleteView.as_view(), name='game-detail-delete'),
    path('api/games/join/', views.GameJoinView.as_view(), name='game-join'),
    path('api/games/move/', views.GameMoveView.as_view(), name='game-move'),
    path('api/games/moves/<uuid:uid>/', views.GameMovesView.as_view(), name='game-moves'),
]

urlpatterns += [
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]