from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("user.urls")),
    path("airport/", include("airport.urls")),
    path("payments/", include("payments.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("doc/redoc/", SpectacularRedocView.as_view(url_name="schema"),
         name="redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
