from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from django.contrib.auth.decorators import login_required  # Add this import
from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import Order,Item
from .forms import ItemForm
import os
from django.core.mail import EmailMessage
from django.http import JsonResponse
from .models import Order
from .utils import generate_pdf
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
import stripe


# views.py



stripe.api_key = "sk_test_51Q15fzFzd9nZWjbWXz9fFPkYZKUFTgWKMefmhOpkS1IdA09d6avbherdu77eg9QlksWHbKLFc5s0nJACYAw26wMY00VikHSV34"
# views.py






class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = User.objects.create_user(username=username, password=password)
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f'/api/password-reset/confirm/?uid={uid}&token={token}')

            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

            return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

            if not default_token_generator.check_token(user, serializer.validated_data['token']):
                return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create the order but don't commit to save items yet
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = sum(item.price for item in form.cleaned_data['items'])  # Calculate total price
            order.save()
            form.save_m2m()  # Save the many-to-many relationship (items)

            # Create a payment intent
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(order.total_price * 100),  # Amount in cents
                    currency='usd',  # Adjust currency as needed
                )
                client_secret = payment_intent['client_secret']
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Render the payment form with the client secret
            return render(request, 'payment_form.html', {
                'stripe_public_key': settings.STRIPE_TEST_PUBLIC_KEY,
                'client_secret': client_secret,
                'order_id': order.id,  # Pass the order ID
            })
    else:
        form = OrderForm()

    return render(request, 'create_order.html', {'form': form})

def send_invoice_email(order):
    pdf_file = generate_pdf(order)
    subject = f"Your Invoice for Order #{order.id}"
    body = "Please find attached your invoice."
    from_email = os.environ.get('EMAIL_HOST_USER')
    to_email = [order.user.email]
    
    email = EmailMessage(
        subject,
        body,
        from_email,
        to_email
    )
    
    email.attach(f'invoice_{order.id}.pdf', pdf_file.read(), 'application/pdf')
    email.send()


@login_required
def order_success(request, order_id):
    # Attempt to retrieve the order; if it doesn't exist, a 404 will be raised.
    order = get_object_or_404(Order, id=order_id)

    # Check if the order belongs to the authenticated user
    if order.user != request.user:
        raise PermissionDenied("You do not have permission to access this order.")
    
    # If the order is found and belongs to the user, send the invoice
    send_invoice_email(order)
    return JsonResponse({'status': 'success', 'message': 'Invoice sent!'})



# @login_required
# def create_order(request):
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             # Create the order but don't commit to save items yet
#             order = form.save(commit=False)
#             order.user = request.user
#             order.total_price = sum(item.price for item in form.cleaned_data['items'])  # Calculate total price
#             order.save()
#             form.save_m2m()  # Save the many-to-many relationship (items)
            
#             # Redirect to the success page
#             return redirect('order_success', order_id=order.id)
#     else:
#         form = OrderForm()

#     return render(request, 'create_order.html', {'form': form})



@login_required
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new item to the database
            return redirect('item_list')  # Redirect to a list view or success page
    else:
        form = ItemForm()

    return render(request, 'create_item.html', {'form': form})

def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})