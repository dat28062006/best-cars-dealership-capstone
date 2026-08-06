from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from djangoapp import views as app_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoapp/", include("djangoapp.urls")),
    path("fetchDealers", app_views.get_dealerships),
    path("fetchDealers/<str:state>", app_views.get_dealerships),
    path("fetchDealer/<int:dealer_id>", app_views.get_dealer_details),
    path("fetchReviews/dealer/<int:dealer_id>", app_views.get_dealer_reviews),
    path("fetchCars", app_views.get_cars),
    path("", TemplateView.as_view(template_name="Home.html")),
    path("about/", TemplateView.as_view(template_name="About.html")),
    path("contact/", TemplateView.as_view(template_name="Contact.html")),
    path("login/", TemplateView.as_view(template_name="login_page.html")),
    path("register/", TemplateView.as_view(template_name="register_page.html")),
    path("dealers/", app_views.dealers_page),
    path("dealers/<str:state>/", app_views.dealers_page),
    path("dealer/<int:dealer_id>/", app_views.dealer_page),
    path("postreview/<int:dealer_id>/", app_views.postreview_page),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
