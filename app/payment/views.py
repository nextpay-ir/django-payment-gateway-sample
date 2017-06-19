from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import random

# import conf
from .conf import *

# Soap Client
from zeep import Client


class PaymentView(View):
    template_name = 'payment.html'
    messages = {
        "invalid_amount": {
            "level": messages.ERROR,
            "text": "Invalid Amount"
        },
        "get_token_fail": {
            "level": messages.ERROR,
            "text": "Get Token Failed : %s"
        },
    }

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):

        amount = request.POST.get('amount')
        order_id = random.random()

        # store in session
        # request.session['amount'] = amount
        # request.session['order_id'] = order_id

        if amount:
            client = Client('https://api.nextpay.org/gateway/token.wsdl')
            result = client.service.TokenGenerator(
                API_KEY,
                order_id,
                amount,
                request.build_absolute_uri(reverse('payment_callback')),
            )

            if result.code != -1:
                messages.add_message(
                    self.request,
                    self.messages["get_token_fail"]["level"],
                    self.messages["get_token_fail"]["text"] % result.code
                )
            else:
                return redirect('https://api.nextpay.org/gateway/payment/%s' % result.trans_id)

        else:
            messages.add_message(
                self.request,
                self.messages["invalid_amount"]["level"],
                self.messages["invalid_amount"]["text"]
            )

        return redirect(self.get_fail_url())

    def get_fail_url(self):
        return str(reverse_lazy('payment'))

    def get_success_url(self):
        return str(reverse_lazy('payment'))


class PaymentCallbackView(View):
    template_name = 'callback.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PaymentCallbackView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):

        trans_id = request.POST.get('trans_id')
        order_id = request.POST.get('order_id')

        # amount = request.session.get('amount')
        amount = 2000

        # if order_id != request.session.get('order_id'):
        #     return HttpResponseForbidden()

        if trans_id and order_id and amount:
            client = Client('https://api.nextpay.org/gateway/verify.wsdl')
            result = client.service.PaymentVerification(
                API_KEY,
                order_id,
                amount,
                trans_id,
            )

            # if result == 0 then success payment
            return render(request, self.template_name, {
                'result_code':result,
                'trans_id': trans_id
            })

        else:
            return HttpResponseBadRequest()


