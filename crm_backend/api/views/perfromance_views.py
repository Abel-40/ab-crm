from ..serializers.performance_serializers import (
  TaskSubmissionSerializer,
  SubTaskSubmissionSerializer,
  ManualReviewSerializer,
  DepartmentRankSerializer,
  EmployeeRankSerializer,
  DepartmentRank,
  EmployeeRank,
  Task,
  SubTask
)
from utils.api_response import api_response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status, viewsets
from utils.permissions import IsDepartmentLeader


class Performance_analysis(viewsets.ViewSet):
  permission_classes = [IsAuthenticated]
  @action(detail=False, methods=['post'], permission_classes=[IsDepartmentLeader])
  def submit_task(self, request):
      serializer = TaskSubmissionSerializer(data=request.data, context={'request': request})
      
      if serializer.is_valid():
          task = serializer.validated_data['task']
          submitted_by = request.user
          department_leader = task.department.leader
          progress = serializer.validated_data['progress']
          incomplete_mandatory_subtasks = SubTask.objects.filter(
            task=task,
            subtask_type="Mandatory",
            status__in=['PN', 'IN_P']
          ).exists()

          if incomplete_mandatory_subtasks:
            return api_response(
                message="All mandatory subtasks must be completed before submitting the task.",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
            
          if submitted_by != department_leader:
              return api_response(
                  message="You aren't a department leader for this department",
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  success=False
              )
          task.status = Task.STATUS.COMPLETED
          task.save()   
          serializer.save(task=task, submitted_by=submitted_by,progress=progress)

          return api_response(
              message="Task submitted successfully",
              status_code=status.HTTP_201_CREATED,
              success=True,
              data=serializer.data
          )

    
      return api_response(
          message="Unexpected error occurred",
          status_code=status.HTTP_400_BAD_REQUEST,
          success=False,
          errors=serializer.errors
      )

  @action(detail=False, methods=['post'])
  def submit_subtask(self, request):
      serializer = SubTaskSubmissionSerializer(data=request.data,context={'request':request})

      if serializer.is_valid():
          subtask = serializer.validated_data['subtask']
          submitted_by = request.user
          task = subtask.task
          progress = serializer.validated_data['progress']

          if subtask.assigned_to != submitted_by:
              return api_response(
                  message="You can only submit a subtask that is assigned to you.",
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  success=False
              )
          subtask.status = SubTask.STATUS.COMPLETED
          subtask.save()
          serializer.save(subtask=subtask, submitted_by=submitted_by, progress=progress)

          return api_response(
              message="Subtask submitted successfully.",
              status_code=status.HTTP_201_CREATED,
              success=True,
              data=serializer.data
          )

      return api_response(
          message="Subtask submission failed. Please check the provided data.",
          status_code=status.HTTP_400_BAD_REQUEST,
          success=False,
          errors=serializer.errors
      )


  @action(detail=False, methods=['post'])
  def submit_review(self, request):
      serializer = ManualReviewSerializer(data=request.data,context={'request':request})

      if serializer.is_valid():
          reviewer = request.user
          review_employee = serializer.validated_data.get('review_employee')
          review_department = serializer.validated_data.get('review_department')
          review_type = serializer.validated_data['review_type']
          score = serializer.validated_data.get('score')
          comments = serializer.validated_data.get('comments')

          
          manual_review = serializer.save(reviewer=reviewer, review_employee=review_employee,review_department=review_department,score=score, comments=comments,review_type=review_type)

          return api_response(
              message="Manual review submitted successfully.",
              status_code=status.HTTP_201_CREATED,
              success=True,
              data=serializer.data
          )

      return api_response(
          message="Review submission failed. Please check the provided data.",
          status_code=status.HTTP_400_BAD_REQUEST,
          success=False,
          errors=serializer.errors
      )
 
  @action(detail=False, methods=['get'],permission_classes=[IsAdminUser])
  def department_ranks(self, request):
      ranks = DepartmentRank.objects.all()
      serializer = DepartmentRankSerializer(ranks, many=True)

      return api_response(
          message="Department rankings retrieved successfully.",
          status_code=status.HTTP_200_OK,
          success=True,
          data=serializer.data
      )

  @action(detail=False, methods=['get'],permission_classes=[IsAdminUser])
  def employee_ranks(self, request):
      ranks = EmployeeRank.objects.all()
      serializer = EmployeeRankSerializer(ranks, many=True)

      return api_response(
          message="Employee rankings retrieved successfully.",
          status_code=status.HTTP_200_OK,
          success=True,
          data=serializer.data
      )