from tasks.models import Task,SubTask
from rest_framework import serializers
from datetime import datetime, timezone
from users.models import User
class CreateTaskSerializer(serializers.ModelSerializer):
  class Meta:
    model = Task
    fields = ['title','description','deadline','department','status','assigned_by','created_at']
    read_only_fields = ['status','assigned_by','created_at']
    
  def validate(self, data):
    allowed_fields = set(self.fields.keys()) 
    received_fields = set(self.initial_data.keys()) 
    extra_fields = received_fields - allowed_fields 
    
    if extra_fields:
        raise serializers.ValidationError(
            {field: "This field is not allowed." for field in extra_fields}
        )
        
    deadline = data.get("deadline")
    if deadline:
        now = datetime.now(timezone.utc) 
        if deadline < now:
         raise serializers.ValidationError({"deadline": "Deadline cannot be in the past."})

    return data
class UpdateTaskSerializer(serializers.Serializer):
  title = serializers.CharField()
  department_name = serializers.CharField()
  status = serializers.CharField()
  
  def validate(self, data):
    allowed_fields = set(self.fields.keys()) 
    received_fields = set(self.initial_data.keys()) 
    extra_fields = received_fields - allowed_fields 
    
    if extra_fields:
        raise serializers.ValidationError(
            {field: "This field is not allowed." for field in extra_fields}
        )

    return data


class CreateSubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['task', 'assigned_to', 'title', 'description', 'deadline', 'status', 'subtask_type','created_at']
        read_only_fields = ('created_at',)

    def validate(self, data):
        allowed_fields = set(self.fields.keys()) 
        received_fields = set(self.initial_data.keys()) 
        extra_fields = received_fields - allowed_fields 

        if extra_fields:
            raise serializers.ValidationError({field: "This field is not allowed." for field in extra_fields})


        deadline = data.get("deadline")
        if deadline:
            now = datetime.now(timezone.utc)
            if deadline < now:
                raise serializers.ValidationError({"deadline": "Deadline cannot be in the past."})

        assigned_to = data.get('assigned_to')
        task = data.get('task')

        user_department = assigned_to.userprofile.department

        if not user_department:
            raise serializers.ValidationError("The user doesn't have a department. Please assign a department first.")

        if user_department != task.department:
            raise serializers.ValidationError("The user isn't in this department, you can't assign this task.")

        return data

    
class UpdateSubTaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    task_title = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=SubTask.STATUS.choices)
    def validate(self, data):
        allowed_fields = set(self.fields.keys()) 
        received_fields = set(self.initial_data.keys()) 
        extra_fields = received_fields - allowed_fields 
        
        if extra_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in extra_fields}
            )

        return data
class DeleteSubTaskSerializer(serializers.ModelField):
    class Meta:
        model = SubTask
        fields = ['id']
    def validate(self, data):
        allowed_fields = set(self.fields.keys()) 
        received_fields = set(self.initial_data.keys()) 
        extra_fields = received_fields - allowed_fields 
        
        if extra_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in extra_fields}
            )
        if SubTask.objects.get(id=data.get('id')) is None:
           raise serializers.ValidationError('there is no subtask with this id')
        return data
   
   
class ReassignSubTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    assigned_to = serializers.IntegerField(allow_null=True, required=False)  
    def validate(self, attrs):
        subtask_id = attrs.get('id')
        if not SubTask.objects.filter(id=subtask_id).exists():
            raise serializers.ValidationError({"id": "There is no subtask with this ID."})

        assigned_to = attrs.get('assigned_to')
        if assigned_to is not None and not User.objects.filter(id=assigned_to).exists():
            raise serializers.ValidationError({"assigned_to": "Assigned user does not exist."})

        return attrs

    def update(self, instance, validated_data):
        instance.assigned_to = validated_data.get("assigned_to") 
        instance.save()
        return instance
