from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("magazin/", include("magazin.urls")),
    # http://127.0.0.1:8000/ duce direct la pagina principală a magazinului
    path("", RedirectView.as_view(pattern_name="index")),
]

# Imaginile și documentele încărcate din admin (MEDIA_ROOT). Doar cât rulează cu DEBUG = True.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
