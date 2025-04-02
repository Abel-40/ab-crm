from rest_framework import serializers
from departments.models import Departement
from django.contrib.auth.models import User

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = ['id', 'name', 'created_by', 'leader']
        read_only_fields = ('id',)

    def validate(self, attrs):
        if len(attrs.get('name', '')) <= 5:
            raise serializers.ValidationError('Department name must be greater than 5 characters!')
        return attrs

    def create(self, validated_data):
        leader = validated_data.get("leader") 
        department = Departement.objects.create(**validated_data)
        if hasattr(leader, "userprofile"):
            leader.userprofile.department = department 
            leader.userprofile.save() 

        return department

  
class ChangeDepartementLeader(serializers.Serializer):
  department_id = serializers.IntegerField()
  new_leader_email = serializers.EmailField(max_length=150)
  

class DeleteDepartmentSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    admin_password = serializers.CharField(write_only=True)

    def validate(self, data):
        allowed_fields = set(self.fields.keys()) 
        received_fields = set(self.initial_data.keys()) 
        extra_fields = received_fields - allowed_fields 
        
        if extra_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in extra_fields}
            )
        return data

      
class AssignDepartmentSerializer(serializers.Serializer):
  emails = serializers.ListField(
    child = serializers.EmailField(),
    required = True
  )
  
  department_id = serializers.IntegerField()
  admin_password = serializers.CharField()
  def validate_emails(self, value):
      if isinstance(value, str):
          return [value] 
      return value
    
  def validate(self, data):
      allowed_fields = set(self.fields.keys()) 
      received_fields = set(self.initial_data.keys()) 
      extra_fields = received_fields - allowed_fields 
      
      if extra_fields:
          raise serializers.ValidationError(
              {field: "This field is not allowed." for field in extra_fields}
          )
      return data

class RemoveMemberSerializer(serializers.Serializer):
  emails = serializers.ListField(
    child = serializers.EmailField()
  )
  
  def validate_emails(self, value):
      if isinstance(value, str):
          return [value] 
      return value
    
  def validate(self, data):
    allowed_fields = set(self.fields.keys()) 
    received_fields = set(self.initial_data.keys()) 
    extra_fields = received_fields - allowed_fields 
    
    if extra_fields:
        raise serializers.ValidationError(
            {field: "This field is not allowed." for field in extra_fields}
        )
    return data