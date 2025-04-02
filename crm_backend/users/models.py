from django.db import models
from django.urls import reverse
from django.contrib.auth.models import BaseUserManager,AbstractUser
import uuid
from django.utils.text import slugify
class UserManger(BaseUserManager):
  def create_user(self,email,password,username):
    if email is None:
      raise ValueError('Email required')
    
    email = self.normalize_email(email)
    user = self.model(email=email,username=username)
    user.set_password(password)
    user.save(using=self._db)
    return user
  def create_superuser(self,email,password,username):
    user = self.create_user(email=email,password=password,username=username)
    user.is_staff = True
    user.is_superuser = True
    user.save(using= self._db)
    return user
  
class User(AbstractUser):
  email = models.EmailField(unique=True,max_length=200)
  username = models.CharField(max_length=100,unique=False)
  slug = models.SlugField(unique=True,max_length=100)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ['username']
  objects= UserManger()
  
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(f"{self.username}-{uuid.uuid4().hex[:8]}")
    super().save(*args,**kwargs)
  
  def get_absolute_url(self):
      return reverse("user-detail", kwargs={"slug":self.slug})
  
  
  def __str__(self):
    return self.username
  
  
class UserProfile(models.Model):
  class Role(models.TextChoices):
    ADMIN = 'AD','Admin'
    DEPARTMENT_LEADER = 'DL','Department_Leader'
    DEPARTMENT_MEMBER = 'DM','Department_Member'
  user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='userprofile')
  address = models.CharField(max_length=200,default='Not provided')
  profile_picture = models.ImageField(upload_to='profile_pictures/',null=True,blank=True)
  phone_number = models.CharField(max_length=13,default="Not provided")
  role = models.CharField(max_length=2,choices=Role.choices,default=Role.DEPARTMENT_MEMBER)
  document = models.FileField(upload_to='user_documents/', blank=True, null=True)
  objects = models.Manager()
  department = models.ForeignKey('departments.Departement', on_delete=models.SET_NULL, null=True, blank=True)

  def __str__(self):
    return self.user.username
  