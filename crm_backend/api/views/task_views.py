from ..serializers.task_serializers import (
    CreateTaskSerializer,
    Task, UpdateTaskSerializer,
    CreateSubTaskSerializer, 
    UpdateSubTaskSerializer,
    ReassignSubTaskSerializer,
    DeleteSubTaskSerializer,
    SubTask
)
from utils.api_response import api_response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from utils.permissions import IsDepartmentLeader
from django.shortcuts import get_object_or_404
class TaskView(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def create_task(self, request):
        serializer = CreateTaskSerializer(data=request.data)
        if serializer.is_valid():
            assigned_by = request.user
            serializer.save(assigned_by=assigned_by)
            return api_response(
                message="task created successfully!",
                status_code=status.HTTP_201_CREATED,
                success=True,
                data=serializer.data
            )
        return api_response(
            message="invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=True,
            errors=serializer.errors
        )

    @action(detail=False, methods=['patch'], permission_classes=[IsDepartmentLeader])
    def update_task_status(self, request):
        serializer = UpdateTaskSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            department_name = serializer.validated_data['department_name']
            task_status = serializer.validated_data['status']

            status_types = {
                'PN': Task.STATUS.PENDING,
                'IN_P': Task.STATUS.IN_PROGRESS,
                'CM': Task.STATUS.COMPLETED
            }

            new_status = status_types.get(task_status)
            if new_status is None:
                return api_response(
                    message="Choose only PN (Pending), IN_P (In Progress), CM (Completed)",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )

            task = Task.objects.select_related('department').filter(
                department__name=department_name, title=title
            ).first()

            if not task:
                return api_response(
                    message="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=False
                )

            if task.department.leader != request.user:
                return api_response(
                    message="You are not authorized to update this task",
                    status_code=status.HTTP_403_FORBIDDEN,
                    success=False
                )

            task.status = new_status
            task.save()

            return api_response(
                message=f"Status successfully changed to {new_status}",
                status_code=status.HTTP_200_OK,
                success=True
            )

        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )


    @action(detail=False, methods=['post'], permission_classes=[IsDepartmentLeader])
    def create_subtask(self, request):
        serializer = CreateSubTaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.validated_data['task']
            department_leader = task.department.leader
            if not request.user == department_leader:
                return api_response(
                    message="your not  department leader for this department!!!",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    success=False
                )              
            serializer.save()
            return api_response(
                message="Subtask created successfully!",
                status_code=status.HTTP_201_CREATED,
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
    def update_subtask_status(self, request):
        serializer = UpdateSubTaskSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            task_title = serializer.validated_data['task_title']
            subtask_status = serializer.validated_data['status']
            subtask = SubTask.objects.filter(
                task__title = task_title,title=title,
            ).first()
            task = Task.objects.filter(title=task_title).first()
            if not task:
                return api_response(
                    message="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=False
                )

            if not subtask:
                return api_response(
                    message="Subtask not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=False
                )

            if subtask.assigned_to != request.user:
                return api_response(
                    message="You are not authorized to update this subtask",
                    status_code=status.HTTP_403_FORBIDDEN,
                    success=False
                )

            subtask.status = subtask_status
            subtask.save()

            return api_response(
                message=f"Subtask status updated to {subtask_status}",
                status_code=status.HTTP_200_OK,
                success=True
            )

        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )
    @action(detail=False, methods=['delete'], url_path="delete/(?P<task_id>\d+)", permission_classes=[IsAdminUser])
    def delete_task(self, request, task_id=None):
        
        task = get_object_or_404(Task, id=task_id)

        task.delete()

        return api_response(
            message=f"Task {task_id} deleted successfully!",
            status_code=status.HTTP_200_OK,
            success=True
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_subtasks(self, request):
        task_title = request.query_params.get('task_title')
        if not task_title:
            return api_response(
                message="Task title is required",
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False
            )

        subtasks = SubTask.objects.filter(task__title=task_title)
        serializer = CreateSubTaskSerializer(subtasks, many=True)

        return api_response(
            message="Subtasks retrieved successfully",
            status_code=status.HTTP_200_OK,
            success=True,
            data=serializer.data
        )
        
    @action(detail=False, methods=['patch'], permission_classes=[IsDepartmentLeader])
    def reassign_subtask(self, request):
        serializer = ReassignSubTaskSerializer(data=request.data)
        if serializer.is_valid():
            subtask_id = serializer.validated_data['id']
            assigned_to = serializer.validated_data.get('assigned_to')  

            try:
                subtask = SubTask.objects.get(id=subtask_id)
            except SubTask.DoesNotExist:
                return api_response(
                    message="SubTask not found.",
                    status_code=status.HTTP_404_NOT_FOUND,
                    success=False
                )

            subtask.assigned_to_id = assigned_to  
            subtask.save()

            return api_response(
                message="SubTask reassigned successfully." if assigned_to else "SubTask unassigned successfully.",
                status_code=status.HTTP_200_OK,
                success=True,
                data=CreateSubTaskSerializer(subtask).data
            )

        return api_response(
            message="Invalid data",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=serializer.errors
        )
        
    @action(detail=False,methods=['delete'],url_path="delete/(?P<subtask_id>\d+)",permission_classes=[IsDepartmentLeader])
    def delete_subtask(self,request,subtask_id):
        subtask = get_object_or_404(SubTask, id=subtask_id)

        subtask.delete()

        return api_response(
            message=f"Task {subtask_id} deleted successfully!",
            status_code=status.HTTP_200_OK,
            success=True
        )
    
    


