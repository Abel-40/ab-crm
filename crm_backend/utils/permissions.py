from rest_framework.permissions import BasePermission
from users.models import UserProfile
class IsDepartmentLeader(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.userprofile.role == UserProfile.Role.DEPARTMENT_LEADER
class IsLeaderOrAdmin(BasePermission):
  
  def has_permission(self, request, view):
      if not request.user.is_authenticated:
        return False
      
      return request.user.userprofile.role in [UserProfile.Role.ADMIN, UserProfile.Role.DEPARTMENT_LEADER]