from django.db import models
from base.models import BaseModel
# Create your models here.


class Contact(BaseModel):
    name= models.CharField(max_length=180)
    email = models.CharField(max_length=180)
    desc = models.TextField()
    mobile = models.CharField(max_length=12)
    

class Subscribe(BaseModel):
    email = models.EmailField()