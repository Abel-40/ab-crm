from rest_framework import viewsets,status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from ..serializers.task_serializers import CreateSubTaskSerializer,SubTask
from ..serializers.user_serializers import (
  UserSerializer,
  User,
  UserProfile,
  UserDetailSerializer,
  RoleAssignSerializer,
  UpdateUserInfoSerializer,
  UpadateUserProfileSerializer,
  CreateUserProfileSerializer,
  UserDeletionSerializer
  
  )
import logging
from django.shortcuts import get_object_or_404
from users.views import send_welcome_email
from utils.api_response import api_response 
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
class UserCreationApiView(viewsets.ViewSet):
    logger = logging.getLogger(__name__)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                message="Account created successfully",
                status_code=status.HTTP_201_CREATED,
                success=True,
                data={"user": serializer.data}
            )
        
        # Improved error handling
        email_errors = serializer.errors.get("email", [])
        if email_errors and any("already registered" in str(e) for e in email_errors):
            return api_response(
                message="Account exists, please sign in",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                errors={"email": email_errors}
            )
        
        return api_response(
            message='Validation error',
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )


    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def signin(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return api_response(
                message="Email and password are required",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
                return api_response(
                    message="Invalid email.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    success=False
                )
        if not user.is_active:
            return api_response(
                message="Account is inactive. Please wait for admin approval.",
                status_code=status.HTTP_403_FORBIDDEN,
                success=False
            )
        active_user = authenticate(request, username=email, password=password)
        if active_user is None:
            return api_response(
                message="Invalid password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False                
            )
        seriaizer = UserSerializer(active_user)
        
        refresh = RefreshToken.for_user(active_user)
        response = api_response(
            message="Login successful",
            status_code=status.HTTP_200_OK,
            success=True,
            data={
                "user":seriaizer.data,
                "is_authenticated":user.is_authenticated,
                "access": str(refresh.access_token),
            }
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Strict',
        )
        return response
    

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def refresh_token(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return api_response(
                message="No refresh token provided",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = api_response(
                message="Token refreshed successfully",
                status_code=status.HTTP_200_OK,
                success=True,
                data={"access": access_token}
            )

            # Optional: rotate refresh token cookie (recommended for added security)
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),  # Still valid refresh token
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=7*24*60*60
            )

            return response

        except TokenError as e:
            return api_response(
                message="Invalid refresh token",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False,
                errors={"token": str(e)}
            )


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_users(self, request):
        if request.user.is_superuser or request.user.userprofile.role == UserProfile.Role.DEPARTMENT_LEADER:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        else:
            user = User.objects.get(email=request.user.email)
            serializer = UserSerializer(user)
        return api_response(
            message="Users retrieved successfully",
            status_code=status.HTTP_200_OK,
            success=True,
            data={"users":serializer.data}
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def retrieve_user(self, request, slug=None):
        try:
            user = User.objects.get(slug=slug)
            serializer = UserDetailSerializer(user)
            return api_response(
                message="User retrieved successfully",
                status_code=status.HTTP_200_OK,
                success=True,
                data={"user":serializer.data}
            )
        except User.DoesNotExist:
            return api_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
                success=False
            )
            
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_user_activation(self, request):
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)

        user.is_active = not user.is_active
        user.save()

        return api_response(
            message=f"User {'activated' if user.is_active else 'deactivated'} successfully",
            status_code=status.HTTP_200_OK,
            success=True,
            data={"is_active": user.is_active}
        )

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_user_info(self, request):
        user = get_object_or_404(User, email=request.user.email)
        serializer = UpdateUserInfoSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            password = serializer.validated_data.pop('password', None)
            if password:
                user.set_password(password)
            serializer.save()
            return api_response(
                message="User updated successfully!",
                status_code=status.HTTP_200_OK,
                success=True,
                data=serializer.data
            )
        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_userprofile_info(self, request):
        user = get_object_or_404(User, email=request.user.email)
        userprofile = get_object_or_404(UserProfile, user=user)
        serializer = UpadateUserProfileSerializer(userprofile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                message="UserProfile updated successfully!",
                status_code=status.HTTP_200_OK,
                success=True,
                data=serializer.data
            )
        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )
        
         
    @action(detail=False, methods=['patch'], permission_classes=[AllowAny], authentication_classes=[])
    def create_userprofile_info(self, request):
        email = request.data.get('email')
        userprofile = get_object_or_404(UserProfile,user__email = email)
        if not email:
            return api_response(
                message="Email is required for user lookup.",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                errors={"email": "This field is required for user lookup."}
            )
            
        serializer = CreateUserProfileSerializer(userprofile,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                message="UserProfile created successfully!",
                status_code=status.HTTP_200_OK,
                success=True,
                data={"userprofile": CreateUserProfileSerializer(userprofile).data}
            )

        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )

    @action(detail=False, methods=['delete'], permission_classes=[IsAdminUser])
    def delete_account(self, request):
        serializer = UserDeletionSerializer(data=request.data)
        if not request.user.is_authenticated:
            return api_response(
                message="User not authenticated",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False
            )

        if serializer.is_valid():
            password = serializer.validated_data['password']
            user = serializer.validated_data['user']
            admin_account = request.user
            if not admin_account.check_password(password):
                return api_response(
                    message="Please enter the correct password",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )
            
            user.delete()  
            return api_response(
                message="User account deleted successfully!",
                status_code=status.HTTP_200_OK,
                success=True
            )
        
        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )  

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_subtasks(self, request):
        subtasks = SubTask.objects.filter(assigned_to=request.user)
        serializer = CreateSubTaskSerializer(subtasks, many=True)

        return api_response(
            message="Subtasks retrieved successfully",
            status_code=status.HTTP_200_OK,
            success=True,
            data=serializer.data
        )
