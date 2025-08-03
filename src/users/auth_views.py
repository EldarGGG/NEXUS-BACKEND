import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import CustomUser
from stores.models import Store

# Настройка логгера
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AuthLoginView(APIView):
    """
    Full login endpoint with JWT tokens and store information
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            logger.info(f"Начало обработки входа. Данные запроса: {request.data}")
            
            # Get credentials
            phone = request.data.get('phone')
            password = request.data.get('password')
            
            logger.info(f"Получены учетные данные. Телефон: {phone}")
            
            # Basic validation
            if not phone or not password:
                return Response(
                    {"detail": "Phone and password are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find user
            try:
                logger.info(f"Поиск пользователя с username: {phone}")
                user = CustomUser.objects.get(username=phone)
                logger.info(f"Пользователь найден: ID={user.id}, username={user.username}")
            except CustomUser.DoesNotExist:
                logger.warning(f"Пользователь с username={phone} не найден")
                return Response(
                    {"detail": "Invalid credentials"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check password
            logger.info("Проверка пароля пользователя")
            if not user.check_password(password):
                logger.warning("Неверный пароль")
                return Response(
                    {"detail": "Invalid credentials"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Get user's store information if it exists
            store_data = None
            try:
                store = Store.objects.get(owner=user)
                store_data = {
                    'id': store.id,
                    'name': store.name,
                    'description': store.description,
                    'email': store.email,
                    'phone': store.phone,
                }
            except Store.DoesNotExist:
                # User doesn't have a store yet, which is fine for login
                pass
            
            # Return full response with tokens and user data
            return Response({
                "access_token": str(access_token),
                "refresh_token": str(refresh),
                "user_id": user.id,
                "username": user.username,
                "phone": user.username,
                "email": user.email or "",
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "store": store_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Ошибка при входе: {str(e)}\n{error_trace}")
            return Response({
                "detail": f"Server error: {str(e)}",
                "traceback": error_trace.split('\n') if 'DEBUG' in os.environ else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class AuthSignupView(APIView):
    """
    Signup endpoint that matches frontend expectations
    POST /auth/signup
    Expected data: { email, phone, password, name, surname, user_type }
    """
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = request.data
            
            # Required fields validation
            required_fields = ['password', 'name', 'surname', 'user_type']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response(
                    {"detail": f"Missing fields: {', '.join(missing_fields)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            phone = data.get('phone', '')
            email = data.get('email', '')
            password = data.get('password')
            name = data.get('name')
            surname = data.get('surname')
            user_type = data.get('user_type')
            
            # Must have either phone or email
            if not phone and not email:
                return Response(
                    {"detail": "Either phone or email is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already exists
            if phone and CustomUser.objects.filter(username=phone).exists():
                return Response(
                    {"detail": "User with this phone already exists"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if email and CustomUser.objects.filter(email=email).exists():
                return Response(
                    {"detail": "User with this email already exists"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new user
            # Use phone as username if available, otherwise use email
            username = phone if phone else email
            user = CustomUser.objects.create_user(
                username=username,
                email=email if email else f"{username}@example.com",  # Provide default email if none
                password=password,
                first_name=name,
                last_name=surname
            )
            
            # Create store for user (IMPORTANT: Each user gets their own store)
            store = Store.objects.create(
                name=f"Магазин {name} {surname}",
                description=f"Личный магазин пользователя {name} {surname}",
                email=email if email else f"{username}@example.com",
                phone=phone if phone else "+77000000000",
                owner=user
            )
            
            return Response({
                "message": "Successful registration!",
                "user_id": user.pk,
                "store_id": store.id,
                "store_name": store.name
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
