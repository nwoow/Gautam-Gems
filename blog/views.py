from django.shortcuts import render
from . models import Blogpost
# Create your views here.


def blog(request):
    blog = Blogpost.objects.all()
    context = {'blog':blog}
    return render(request,'blog-list-fullwidth.html',context)



def blog_view(request,slug):
    blog = Blogpost.objects.filter(slug=slug).first()
    context = {'blog':blog}
    return render(request,'blog-details-fullwidth.html',context)