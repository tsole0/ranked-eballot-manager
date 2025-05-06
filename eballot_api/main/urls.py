from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This maps the root URL to the home view
    path('work/', views.work, name='work'),  # This maps '/about/' to the about view
    path('blog/', views.blog, name='blog')
]