from django.shortcuts import render, get_object_or_404

from django.core.paginator import Paginator

from django.db.models import Count

from .models import Course, CoursePart, Comment, CourseRelation
from .forms import CommentForm


def courses(request):
    courses = Course.objects.all()
    recomended = Course.objects.annotate(num_relations=Count('related_users')).order_by('num_relations')
    page_num = request.GET.get('page', 1)
    courses_paginator = Paginator(courses, 5)
    page_items = courses_paginator.get_page(page_num)
    return render(request, 'courses.html',{
        'courses':courses.order_by('time'),
        'recomended':recomended,
        'page':page_items,
        'page_range':courses_paginator.page_range,
        'pagenum':int(page_num),
        'pagename':'courses'
    })

def course_part_detail(request, course_part_id):
    course_part = get_object_or_404(CoursePart, id=course_part_id)
    if request.user.is_authenticated:
        if not CourseRelation.objects.filter(course=course_part.course, user=request.user).exists():
            CourseRelation.objects.create(course=course_part.course, user=request.user)
    if request.method == "POST":
        text = request.POST.get('text')
        print('text', text)
        if text:
            Comment.objects.create(author=request.user,course_part=course_part, text=text)
    return render(request, 'course_detail.html', {
        'course_part':course_part
    })
