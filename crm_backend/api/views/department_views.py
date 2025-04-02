from ..serializers.department_serializers import(
  DepartmentSerializer,
  Departement,
  AssignDepartmentSerializer,
  DeleteDepartmentSerializer,
  ChangeDepartementLeader,
  RemoveMemberSerializer
  )
from ..serializers.task_serializers import CreateTaskSerializer
from tasks.models import Task
from utils.api_response import api_response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework import status,viewsets
from users.models import User,UserProfile
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from utils.permissions import IsDepartmentLeader,IsLeaderOrAdmin


class DepartmentView(viewsets.ViewSet):
  
  @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
  def create_department(self,request):
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
      created_by = request.user
      leader = serializer.validated_data['leader']
    
      UserProfile.objects.filter(user=leader).update(role=UserProfile.Role.DEPARTMENT_LEADER)
      serializer.save(created_by=created_by,leader=leader)
      return api_response(
        message='Department created successfully!!!',
        status_code=status.HTTP_201_CREATED,
        success=True,
        data={"department":serializer.data}
      )
    return api_response(
      message='unexpected error occured',
      status_code=status.HTTP_400_BAD_REQUEST,
      success=False,
      errors=serializer.errors
    )

  @action(detail=False, methods=['patch'], permission_classes=[IsAdminUser])
  def change_leader(self, request):
      serializer = ChangeDepartementLeader(data=request.data)
      if serializer.is_valid():
          email = serializer.validated_data['new_leader_email']
          department_id = serializer.validated_data['department_id']
          
          department = None
          user = None
          errors = {}

          try:
              department = Departement.objects.select_related("leader").get(id=department_id)
              user = User.objects.get(email=email)
          except ObjectDoesNotExist:
              errors["department_id"] = "Department with this name does not exist."
          except ObjectDoesNotExist:
              errors["new_leader_email"] = "User with this email does not exist."
        
              
         

          if errors:
              return api_response(
                  message="Validation failed",
                  errors=errors,
                  status_code=status.HTTP_400_BAD_REQUEST,
                  success=False,
              )

          if department.leader:
              department.leader.userprofile.role = UserProfile.Role.DEPARTMENT_MEMBER
              department.leader.userprofile.save() 

          user.userprofile.role = UserProfile.Role.DEPARTMENT_LEADER
          user.userprofile.save()  
          department.leader = user
          department.save()
          return api_response(
              message="Department leader updated successfully",
              status_code=status.HTTP_200_OK,
              success=True,
          )
      
      return api_response(
          message="Invalid input",
          errors=serializer.errors,
          status_code=status.HTTP_400_BAD_REQUEST,
          success=False,
      )


  @action(detail=False,methods=['get'],permission_classes=[IsAdminUser])
  def get_departments(self,request):
    departments = Departement.objects.all()
    serializer = DepartmentSerializer(departments,many=True)
    return api_response(
    message="departments retrieved successfully",
    status_code=status.HTTP_200_OK,
    success=True,
    data={"departments":serializer.data}
  )
    
    
  @action(detail=False,methods=['delete'],permission_classes=[IsAdminUser])
  def delete_department(self,request):
    serializer = DeleteDepartmentSerializer(data=request.data)
    
    if serializer.is_valid():
      department_id = serializer.validated_data['department_id']
      password = serializer.validated_data['admin_password']
     
      admin_account = request.user
      
      if not admin_account.check_password(password):
        return api_response(
            message="Please enter the correct password",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        )
        
      department_to_delete = get_object_or_404(Departement,id=department_id)

  
      department_to_delete.is_active = False
      department_to_delete.save()
      all_department = Departement.objects.filter(is_active=True)
      return api_response(
          data = [{'department_name': department.name,'department_leader': department.leader.email if department.leader else None} for department in all_department],
          message=f"Department '{department_id}' successfully deleted!",
          status_code=status.HTTP_200_OK,
          success=True
      )

  
    return api_response(
    message="Invalid data",
    status_code=status.HTTP_400_BAD_REQUEST,
    success=False,
    errors=serializer.errors
)


  @action(detail=False,methods=['post'],permission_classes=[IsAdminUser])
  def assign_department(self,request):
    serializer = AssignDepartmentSerializer(data=request.data)
    if serializer.is_valid():
      emails = serializer.validated_data['emails']
      department_id = serializer.validated_data['department_id']
      admin_password =  serializer.validated_data['admin_password']
      
      admin_account = request.user
      
      if not admin_account.check_password(admin_password):
        return api_response(
            message="Please enter the correct password",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        ) 
      
      users_to_add = User.objects.filter(email__in=emails)
      department = get_object_or_404(Departement, id=department_id)
      if  department.is_active:
        total_users_added = users_to_add.count()
        
        UserProfile.objects.filter(user__email__in=emails).exclude(department=department).update(department=department)

          
        return api_response(
            data=[{"email": user.email, "department": department_id} for user in users_to_add],
            message=f"{total_users_added} user(s) added to department {department_id} successfully!",
            status_code=status.HTTP_200_OK,
            success=True
        )
      else:
        return api_response(
            message=f"{department} is not active department",
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        )       
    return api_response(
      message="Invalid data",
      status_code=status.HTTP_400_BAD_REQUEST,
      success=False,
      errors=serializer.errors
  )
    
  @action(detail=False,methods=['patch'],permission_classes=[IsLeaderOrAdmin])
  def revoke_department_access(self,request):
    serializer = RemoveMemberSerializer(data=request.data)
    if serializer.is_valid():
      emails = serializer.validated_data['emails']
      
      users = User.objects.filter(email__in= emails)
      user_number = users.count()
      UserProfile.objects.filter(user__email__in=emails).update(department=None)
      return api_response(
          message=f"Removed {user_number} user(s) from department successfully.",
          status_code=status.HTTP_200_OK,
          success=True
      )
      
    return api_response(
      message="Invalid data",
      status_code=status.HTTP_400_BAD_REQUEST,
      success=False,
      errors=serializer.errors
  )
    
  @action(detail=False,methods=['get'],url_path="tasks/(?P<department_id>\d+)",permission_classes=[IsLeaderOrAdmin])
  def department_tasks(self, request, department_id=None):
    tasks = Task.objects.filter(department_id=department_id)
    serializer = CreateTaskSerializer(tasks, many=True)
    return api_response(
        message="department task history",
        status_code=status.HTTP_200_OK,
        success=True,
        data=serializer.data
    ) 

  
