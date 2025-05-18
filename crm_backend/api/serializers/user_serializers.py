from users.models import User,UserProfile
from django.urls import reverse
from rest_framework import serializers
class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserProfile
    fields = ['id','user', 'address', 'profile_picture', 'phone_number', 'role', 'resume','position']
    read_only_fields = ('user','id')

class UserSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'detail_url',  
        ]
        read_only_fields = ( 'detail_url','id')
        extra_kwargs = {'password':{'write_only':True}}
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user
    def validate(self, attrs):
        if not attrs.get('password'):
            raise serializers.ValidationError("Please enter a password")
        return attrs
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def get_detail_url(self, obj):
        return obj.get_absolute_url()
    


class UserDetailSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'userprofile',
        )
        read_only_fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'userprofile'
        ]


# users/serializers.py
class RoleAssignSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)
    role = serializers.CharField(max_length=2)

    def validate(self, attrs):
        role = ['AD', 'DL', 'EM'] 
        if not attrs.get('role') in role:
            raise serializers.ValidationError({
                "role": f"Invalid role. Available roles are: \n AD = Admin \n DL = Department Leader \n EM = Employee"
            })
        return attrs
    
class UpdateUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'first_name', 'last_name']

    def validate(self, attrs):
        if 'email' in attrs:
            raise serializers.ValidationError({"error": "Email field can't be updated. Please try updating other fields."})
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('email', None)
        return super().update(instance, validated_data)

# users/serializers.py
class UpadateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['address', 'profile_picture', 'phone_number', 'role', 'resume']

    def validate(self, attrs):
        if 'role' in attrs:
            raise serializers.ValidationError({"error": "Role cannot be updated here. Use the assign_role endpoint."})
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        return super().update(instance, validated_data)
class CreateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['address', 'profile_picture', 'phone_number','department', 'resume']
    def validate(self, data):
      missing_fields = [field for field in self.fields if field not in self.initial_data or self.initial_data.get(field) in [None, '']]
        
      if missing_fields:
            raise serializers.ValidationError(
                {field: "This field is required." for field in missing_fields}
            )

      return data

class UserDeletionSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100)
    