from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.views.decorators.csrf import csrf_exempt

from .models import Kontest, Masala, UserKontestRelation, UserMasalaRelation
from users.models import User
from .forms import UserMasalaRelationForm
from .decorators import check_contest_time


def kontest(request):
    kontests = Kontest.objects.filter(top=True)
    return render(request, 'kontest.html', {
        'kontests':kontests,
        'pagename':'kontest'
    })

def musobaqalar(request):
    kontests = Kontest.objects.all()
    paginator = Paginator(kontests, 5)
    page_num = request.GET.get('page',1)
    page = paginator.get_page(page_num)
    return render(request, 'musobaqalar.html', {
        'kontests':kontests,
        'pagename':'kontest',
        'page':page,
        'pages':[i for i in range(10-page_num, paginator.num_pages) if abs(page_num-i)<3] if paginator.num_pages>10 else [i for i in range(paginator.num_pages)],
        'total_pages':paginator.num_pages,
    })

def masalalar(request):
    q = request.GET.get("q")
    masalalar = Masala.objects.filter(hidden=False)
    if q:
        masalalar = masalalar.filter(title__contains=q, hidden=False)
    else:
        q = ""
    paginator = Paginator(masalalar, 10)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    return render(request, "masalalar.html", {
        'masalalar':masalalar,
        'pagename':'kontest',
        'page':page,
        'total_pages':paginator.num_pages,
        'pages':paginator.page_range,
        'q':q
    })

def kontest_detail(request, kontest_id):
    kontest = get_object_or_404(Kontest, id=kontest_id)
    if request.user.is_authenticated:
        if not UserKontestRelation.objects.filter(kontest=kontest, user=request.user).exists():
            UserKontestRelation.objects.create(kontest=kontest, user=request.user)

    return render(request, 'kontest_detail.html', {
        'kontest':kontest,
        'pagename':'kontest'
    })

def kontest_urinishlar(request, kontest_id):
    kontest = get_object_or_404(Kontest, id=kontest_id)
    return render(request, 'kontest_urinishlar.html', {
        'kontest':kontest,
        'pagename':'kontest'
    })

def kontest_masalalar(request, kontest_id):
    kontest = get_object_or_404(Kontest, id=kontest_id)
    return render(request, 'kontest_masalalar.html', {
        'kontest':kontest,
        'pagename':'kontest'
    })

def kontest_qatnashuvchilar(request, kontest_id):
    kontest = get_object_or_404(Kontest, id=kontest_id)
    return render(request, 'kontest_qatnashuvchilar.html', {
        'kontest':kontest,
        'pagename':'kontest'
    })

@csrf_exempt
@login_required(login_url="/users/login/")
@check_contest_time
def masala_detail(request, masala_id):
    masala = get_object_or_404(Masala, id=masala_id)
    if masala.hidden:
        return redirect("/")
    if request.method == "POST" and request.user.is_authenticated:
        form = UserMasalaRelationForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.masala = masala
            obj.save()
            if obj.state == 'Waiting...':
                obj.get_script_result()
        else:
            print(form.errors)
    user_results = UserMasalaRelation.objects.filter(user=request.user, masala=masala)
    return render(request, 'masala_detail.html', {
        'masala':masala,
        'pagename':'kontest',
        'results':user_results
    })

def turnir_jadvali(request, kontest_id):
    kontest = get_object_or_404(Kontest, id=kontest_id)
    ratings = User.objects.filter(
        kontests__kontest_id=kontest_id,  # Filter users who participated in the contest
        ishlangan_masalalar__state='🟢 Passed'  # Filter users who passed at least one masala
    ).annotate(
        num_passed=models.Count('ishlangan_masalalar', filter=models.Q(ishlangan_masalalar__state='🟢 Passed')),  # Count passed masalalar for each user
        total_ball=models.Sum('ishlangan_masalalar__masala__ball', filter=models.Q(ishlangan_masalalar__state='🟢 Passed'))  # Sum of balls for passed masalalar
    ).order_by(
        '-total_ball'  # Order by total_ball descending
    )
    return render(request, 'turnir_jadvali.html', {
        'reyting':ratings,
        'kontest':kontest,
        'pagename':'kontest'
    })

def reyting(request):
    users = User.objects.filter(
        ishlangan_masalalar__state='🟢 Passed'
    ).annotate(
        num_passed=models.Count('ishlangan_masalalar', filter=models.Q(ishlangan_masalalar__state='🟢 Passed')),  # Count passed masalalar for each user
        total_ball=models.Sum('ishlangan_masalalar__masala__ball', filter=models.Q(ishlangan_masalalar__state='🟢 Passed'))  # Sum of balls for passed masalalar
    ).order_by(
        '-total_ball'  # Order by total_ball descending
    )
    paginator = Paginator(users, 25)
    page_num = request.GET.get('page', 0)
    page = paginator.get_page(page_num)

    return render(request, 'reyting.html', {
        'pagename':'kontest',
        'reyting':users,
        'page':page,
        'total_pages':list(range(paginator.num_pages)),
        'total_page_count':paginator.num_pages
    })
