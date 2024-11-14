from django.shortcuts import render



from news.models import News
from courses.models import Course


def home(request):
    news = News.objects.all()
    courses = Course.objects.all()
    return render(request, 'home.html', {
        'news':news,
        'courses':courses,
        'pagename':'home'
    })