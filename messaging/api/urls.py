from django.urls import path

from messaging.api.views import RapidProWebhook

app_name = 'api'

urlpatterns = [
    path('rapidpro-webhook/', RapidProWebhook.as_view(), name='rapidpro_webhook')
]
