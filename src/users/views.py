from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from orders.models import Cart
from .forms import CustomUserCreationForm
from .models import CustomUser
from .schemas import *


def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user.set_password(password1)
                user.save()
                Cart.objects.create(user=user)
                return redirect('login')
    context = {
        "form": CustomUserCreationForm
    }
    return render(request, "signup.html", context=context)


def index_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return redirect("login")


class UserCreationAPIView(APIView):
    @extend_schema(**user_create)
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not all([username, password, email]):
            return Response({"status": "invalid request body"})

        if CustomUser.objects.filter(username=username) or CustomUser.objects.filter(email=email):
            return Response({"status": "user already exists"})

        new_user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        Cart.objects.create(user=new_user)

        return Response({"status": "user created"})


class CreateTokenView(APIView):
    @extend_schema(**token_create)
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class CreateTgTokenView(APIView):
    @extend_schema(**tg_token_create)
    def post(self, request):
        tgid = request.data.get("tgid")
        if not CustomUser.objects.filter(username=tgid):
            CustomUser.objects.create_user(
                username=tgid,
                password=tgid,
                email=tgid + "@tg.id"
            )

        user = authenticate(username=tgid, password=tgid)
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
