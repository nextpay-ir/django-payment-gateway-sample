from django.conf.urls import url

from app.payment.views import PaymentView, PaymentCallbackView


urlpatterns = [
    url(r'^$', PaymentView.as_view(), name='payment'),
    url(r'^callback/$', PaymentCallbackView.as_view(), name='payment_callback'),
]
