from rest_framework import viewsets,status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from ..serializers.task_serializers import CreateSubTaskSerializer,SubTask
from ..serializers.user_serializers import (
  UserSerializer,
  User,
  UserProfile,
  UserDetailSerializer,
  RoleAssignSerializer,
  UpdateUserInfoSerializer,
  UpadateUserProfileSerializer,
  UserDeletionSerializer
  
  )
import logging
from django.shortcuts import get_object_or_404
from users.views import send_welcome_email
from utils.api_response import api_response 

class UserCreationApiView(viewsets.ViewSet):
    lookup_field = 'slug'

    logger = logging.getLogger(__name__)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            if User.objects.filter(email=email).exists():
                return api_response(
                    message = "Account exists, please sign in",
                    status_code=status.HTTP_403_FORBIDDEN,
                    success=False
                )

            # if send_welcome_email(email, username):
            serializer.save()
            return api_response(
                message =  "Account created successfully",
                status_code=status.HTTP_201_CREATED,
                success=True,
                data={"user":serializer.data}
            )
            # else:
            #     return api_response(
            #         {"message": "Please check your internet connection"},
            #         status_code=status.HTTP_408_REQUEST_TIMEOUT,
            #         success=False
                # )
        return api_response(message ='unexpected error occured', status_code=status.HTTP_400_BAD_REQUEST,success=False, errors=serializer.errors)


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

        
        user = authenticate(request, username=email, password=password)
        if user is None:
            return api_response(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False
            )

        
        refresh = RefreshToken.for_user(user)
        return api_response(
            message="Login successful",
            status_code=status.HTTP_200_OK,
            success=True,
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
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
