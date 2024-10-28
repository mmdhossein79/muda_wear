import time

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.urls import reverse
from datetime import datetime

from product_module.models import Product
from .models import Order, OrderDetail
from django.shortcuts import redirect, render
import requests
import json
from muda import settings

# Create your views here.


# MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
# ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
# ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
# ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
# amount = 11000  # Rial / Required
# description = "نهایی کردن خرید شما از سایت ما"  # Required
# email = ''  # Optional
# mobile = ''  # Optional
# # Important: need to edit for realy server.
# CallbackURL = 'http://127.0.0.1:8000/order/verify-payment/'
MERCHANT = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

# ZP_API_REQUEST = f"https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
# ZP_API_STARTPAY = f"https://sandbox.zarinpal.com/pg/StartPay/"
ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"
description = "خرید شما نهایی شد"  # Required
# Important: need to edit for realy server.
CallbackURL = 'http://127.0.0.1:8000/order/verify-payment/'


def add_product_to_order(request: HttpRequest):
    product_id = int(request.GET.get('product_id'))
    count = int(request.GET.get('count'))
    print("rreeee",request)
    if count < 1:
        # count = 1
        return JsonResponse({
            'status': 'invalid_count',
            'text': 'مقدار وارد شده معتبر نمی باشد',
            'confirm_button_text': 'مرسی از شما',
            'icon': 'warning'
        })

    if request.user.is_authenticated:
        product = Product.objects.filter(id=product_id, is_active=True, is_delete=False).first()
        print("product",product.price)
        if product is not None:
            current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
            current_order_detail = current_order.orderdetail_set.filter(product_id=product_id).first()
            if current_order_detail is not None:
                current_order_detail.count += count
                current_order_detail.final_price = product.price
                current_order_detail.save()
            else:
                new_detail = OrderDetail(order_id=current_order.id, product_id=product_id, count=count,final_price=product.price)
                new_detail.save()

            return JsonResponse({
                'status': 'success',
                'text': 'محصول مورد نظر با موفقیت به سبد خرید شما اضافه شد',
                'confirm_button_text': 'باشه ممنونم',
                'icon': 'success'
            })
        else:
            return JsonResponse({
                'status': 'not_found',
                'text': 'محصول مورد نظر یافت نشد',
                'confirm_button_text': 'مرسییییی',
                'icon': 'error'
            })
    else:
        return JsonResponse({
            'status': 'not_auth',
            'text': 'برای افزودن محصول به سبد خرید ابتدا می بایست وارد سایت شوید',
            'confirm_button_text': 'ورود به سایت',
            'icon': 'error'
        })


@login_required
def request_payment(request: HttpRequest):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    if total_price == 0:
        return redirect(reverse('user_basket_page'))

    MERCHANT = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # شناسه مرچنت sandbox
    # CallbackURL = "YOUR_CALLBACK_URL"  # آدرس بازگشت شما
    description = "YOUR_PAYMENT_DESCRIPTION"  # توضیح پرداخت

    data = {
        "MerchantID": MERCHANT,  # دقت کنید که کلیدها به صورت camelCase هستند
        "Amount": total_price * 10,  # تبدیل تومان به ریال (1 تومان = 10 ریال)
        "CallbackURL": CallbackURL,
        "Description": description,
        # "Metadata": {"mobile": mobile, "email": email}  # در صورت نیاز
    }
    data = json.dumps(data)
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    response = requests.post("https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json", data=data, headers=headers, timeout=10)
    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            return redirect("https://sandbox.zarinpal.com/pg/StartPay/" + str(response['Authority']))
        else:
            return HttpResponse(response)
    return HttpResponse(response)
# def request_payment(request: HttpRequest):
#     current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
#     total_price = current_order.calculate_total_price()
#     if total_price == 0:
#         return redirect(reverse('user_basket_page'))
#
#     data = {
#         "merchant_id": MERCHANT,
#         "amount": total_price * 10,
#         "callback_url": CallbackURL,
#         "description": description,
#         # "metadata": {"mobile": mobile, "email": email}
#     }
#     data = json.dumps(data)
#     # set content length by data
#     headers = {'content-type': 'application/json', 'content-length': str(len(data))}
#     # req_header = {"accept": "application/json", "content-type": "application/json'"}
#     response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
#     print(response.json())
#     if response.status_code == 200:
#         response = response.json()
#         if response['Status'] == 100:
#             return redirect(ZP_API_STARTPAY + str(response['Authority']))
#         else:
#             return HttpResponse(response)
#     return HttpResponse(response)

    # if len(req.json()['errors']) == 0:
    #     return redirect(ZP_API_STARTPAY.format(authority=authority))
    # else:
    #     e_code = req.json()['errors']['code']
    #     e_message = req.json()['errors']['message']
    #     return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


@login_required
def verify_payment(request: HttpRequest):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        MERCHANT = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # شناسه مرچنت sandbox
        # CallbackURL = "YOUR_CALLBACK_URL"  # آدرس بازگشت شما
        req_data = {
            "MerchantID": MERCHANT,
            "Amount": total_price * 10,
            "Authority": t_authority
        }
        data = json.dumps(req_data)
        headers = { "content-type": "application/json'",'content-length': str(len(data))}
        req = requests.post("https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json", data=data, headers=headers)
        print(req.json())
        if req.status_code == 200:
            t_status = req.json()
            if t_status["Status"] == 100:
                current_order.is_paid = True
                current_order.payment_date = str(datetime.now().date())
                current_order.save()
                ref_str = t_status["RefID"]
                return render(request, 'order_module/payment_result.html', {
                    'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد'
                })
            elif t_status['Status'] == 101:
                return render(request, 'order_module/payment_result.html', {
                    'info': 'این تراکنش قبلا ثبت شده است'
                })
            else:
                # return HttpResponse('Transaction failed.\nStatus: ' + str(
                #     req.json()['data']['message']
                # ))
                return render(request, 'order_module/payment_result.html', {
                    'error': str(req.json()['data']['message'])
                })
        else:
            # e_code = req.json()['errors']['code']
            # e_message = req.json()['errors']['message']
            e_message = req.json()
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
            return render(request, 'order_module/payment_result.html', {
                'error': e_message
            })
    else:
        return render(request, 'order_module/payment_result.html', {
            'error': 'پرداخت با خطا مواجه شد / کاربر از پرداخت ممانعت کرد'
        })
