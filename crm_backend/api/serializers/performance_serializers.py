from performance.models import (
  TaskSubmission,
  ManualReview,
  DepartmentRank,
  EmployeeRank,
  SubTaskSubmission,
  Task,
  SubTask
  )
from rest_framework import serializers
from performance.models import ManualReview
from performance.models import DepartmentRank
from performance.models import EmployeeRank

class TaskSubmissionSerializer(serializers.ModelSerializer):
  class Meta:
    model = TaskSubmission
    fields = ('task','submitted_by','submission_time','progress','status','system_score')
    read_only_fields = ('system_score','submission_time','status','submitted_by')
    
  def validate(self, data):
    user = self.context['request'].user
    task = data['task']
    
    if task:
        incomplete_mandatory_subtasks = SubTask.objects.filter(task=task, subtask_type=SubTask.TYPE.MANDATORY, status__in=['PN', 'IN_P']).exists()
        if incomplete_mandatory_subtasks:
            raise serializers.ValidationError("All mandatory subtasks must be completed before submitting the task.")
    submission_count = TaskSubmission.objects.filter(task=task, submitted_by=user).count()
    if submission_count >= 3:
        raise serializers.ValidationError("You have already submitted this task 3 times please contact your head.")

    return data 
  
class SubTaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTaskSubmission
        fields = ('id', 'subtask', 'submission_time', 'progress', 'status', 'system_score')
        read_only_fields = ('submission_time', 'status', 'system_score', 'submitted_by')

    def validate(self, data):
        user = self.context['request'].user
        subtask = data['subtask']
        subtask = data['subtask']
        submission_count = SubTaskSubmission.objects.filter(subtask=subtask, submitted_by=user).count()
        if submission_count >= 3:
            raise serializers.ValidationError("You have already submitted this subtask 3 times please contact  your department leader.")

        return data

class ManualReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualReview
        fields = ('id', 'review_employee', 'review_department', 'review_type', 'score', 'comments', 'weight')
        read_only_fields = ('weight', 'reviewer')
        
    def validate_review_type(self, value):
      valid_choices = [choice[0] for choice in ManualReview.REVIEW_TYPE.choices]
      if value not in valid_choices:
          raise serializers.ValidationError(f"Invalid review type. Choose from {valid_choices}.")
      return value      
    
    def validate_score(self, value):
        if not (1 <= value <= 100):
            raise serializers.ValidationError("Score must be between 1 and 100.")
        return value
      
    def validate(self, data):
        request = self.context.get('request')
        reviewer = request.user
        reviewed_employee = data.get('review_employee')
        reviewed_department = data.get('review_department')

        if reviewed_employee is not None and reviewed_department is not None:
            raise serializers.ValidationError("You can only review either an employee or a department at a time. Please select only one.")

        if reviewed_employee == reviewer:
            raise serializers.ValidationError("You cannot submit a review for yourself.")

        if reviewed_department is not None and reviewed_department.leader == reviewer:
            raise serializers.ValidationError("As the department leader, you are not allowed to review your own department.")

        if reviewed_employee is None and reviewed_department is None:
            raise serializers.ValidationError("Please select either an employee or a department to review.")

        reviewer_department = reviewer.userprofile.department

        if reviewed_employee is not None:
            reviewed_employee_department = reviewed_employee.userprofile.department
            if reviewer_department != reviewed_employee_department:
                raise serializers.ValidationError("You can only review an employee who belongs to your department.")

        if reviewed_department is not None:
            if reviewer_department != reviewed_department:
                raise serializers.ValidationError("You can only review a department you are a member of.")

        return data


class DepartmentRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentRank
        fields = ('id', 'department', 'system_score', 'manual_score', 'overall_score')
        read_only_fields = ('system_score', 'manual_score', 'overall_score')


class EmployeeRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRank
        fields = ('id', 'employee', 'system_score', 'manual_score', 'overall_score')
        read_only_fields = ('system_score', 'manual_score', 'overall_score')


