from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views.user_views import UserCreationApiView
from .views.department_views import DepartmentView
from .views.task_views import TaskView
from .views.perfromance_views import Performance_analysis
router = DefaultRouter()
router.register(r'user',UserCreationApiView,basename='user')
router.register(r'department', DepartmentView, basename='department')
router.register(r'task',TaskView,basename='task')
router.register(r'performance',Performance_analysis,basename='performance')
urlpatterns = [
  path('api/',include(router.urls)),
  path('user/<slug:slug>/', UserCreationApiView.as_view({'get': 'retrieve_user'}), name='user-detail')
  
]


