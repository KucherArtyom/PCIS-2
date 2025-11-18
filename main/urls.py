from django.http import JsonResponse
from django.urls import path, include
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

router = DefaultRouter()
router.register(r'clubs', views.ClubViewSet)
router.register(r'transfers', views.TransferViewSet, basename='transfers')
router.register(r'games', views.GameViewSet, basename='games')
router.register(r'players', views.PlayerViewSet, basename='players')
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'admin/auth', views.AdminAuthViewSet, basename='admin-auth')
router.register(r'admin/games', views.GamesAdminViewSet, basename='admin-games')
router.register(r'admin/players', views.PlayersAdminViewSet, basename='admin-players')
router.register(r'admin/clubs', views.ClubsAdminViewSet, basename='admin-clubs')
router.register(r'admin/transfers', views.TransfersAdminViewSet, basename='admin-transfers')

@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', get_csrf),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]