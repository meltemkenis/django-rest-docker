
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('post/api/', include('post.api.urls', namespace='post')),
    path('comment/api/', include('comment.api.urls', namespace='comment')),
    path('favourite/api/', include('favourite.api.urls', namespace='favourite')),
    path('user/api/', include('account.api.urls', namespace='account')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
