from django.contrib import admin
from .models import *
# Register your models here.

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title']


admin.site.register(Blogpost,BlogPostAdmin)