from django.shortcuts import render
from django.template.loader import get_template

# Create your views here.
def home(request):
    print(get_template('main/about.html').origin)
    return render(request, 'main/about.html')  # Renders the about.html template

def work(request):
    return render(request, 'main/work.html')  # Renders the work.html template

def blog(request):
    return render(request, 'main/blog.html')