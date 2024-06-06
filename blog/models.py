from django.db import models
from base.models import BaseModel
from ckeditor.fields import RichTextField
from django.utils.text import slugify 

# Create your models here.



class Blogpost(BaseModel):
    title = models.CharField(max_length= 100)
    overview = RichTextField()
    time_upload = models.DateField(blank=True)
    author = models.CharField(max_length=25)
    slug = models.CharField(max_length=130,default="",unique=True,blank=True)
    thumbnail = models.ImageField(upload_to = 'thumbnails')
    publish = models.BooleanField()
    

    class Meta:
        ordering = ['-time_upload',]
        
    def __str__(self):
        return self.title + '  '+ self.author

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Blogpost, self).save(*args, **kwargs) 