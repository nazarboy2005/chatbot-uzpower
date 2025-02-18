from django.urls import path
from home.views import HomeView, ContactView

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contact', ContactView.as_view(), name='contact')

]
