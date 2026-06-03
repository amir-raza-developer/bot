from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts import views as acc_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("listings/", include("listings.urls")),

    # Auth
    path("accounts/login/", acc_views.login_page, name="login"),
    path("accounts/signup/", acc_views.signup_page, name="signup"),
    path("accounts/logout/", acc_views.logout_view, name="logout"),

    # Pages
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("dashboard/", acc_views.dashboard_page, name="dashboard"),
    path("form/", TemplateView.as_view(template_name="form_filler.html"), name="form_filler"),
    path("automation/", TemplateView.as_view(template_name="automation.html"), name="automation"),
    path("bulk/", TemplateView.as_view(template_name="bulk_upload.html"), name="bulk_upload"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
