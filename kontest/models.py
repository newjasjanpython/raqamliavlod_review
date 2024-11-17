import os
import subprocess

from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from ckeditor.fields import RichTextField

from users.models import User
from django.conf import settings

from .utils import Code


@deconstructible
class PathAndRename:
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        if UserMasalaRelation.objects.last():
            newid = UserMasalaRelation.objects.order_by('id').last().id
        else:
            newid = 0
        newid = newid+1
        subprocess.run(["mkdir","-p",f"{settings.MEDIA_ROOT}/scripts/{newid}"])
        print(os.path.join(self.sub_path, str(newid), filename), 25)
        return os.path.join(self.sub_path, str(newid), filename)

# Usage: Pass 'uploads/' or any base directory you want
upload_to = PathAndRename('scripts/')


class Kontest(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image = models.ImageField(upload_to='kontest/')

    top = models.BooleanField(default=False)

    def get_state(self):
        time = self.end_time - timezone.now()
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        result = 'Tugatildi'
        if self.end_time > timezone.now():
            result = f"Kun: {time.days} Vaqt: {hours}:{minutes}:{seconds}"
        return result

    def total_time(self):
        return self.end_time - self.start_time

    def __str__(self):
        return self.title

class Masala(models.Model):
    user = None
    class Meta:
        verbose_name = "Masalalar"
        verbose_name_plural = verbose_name
    title = models.CharField(max_length=150)
    kirish = RichTextField()
    chiqish = RichTextField()
    description = RichTextField()
    hotira = models.IntegerField(default=150)
    muallif = models.CharField(max_length=150)
    qiyinchilik = models.CharField(
        max_length=150,
        choices=(
            ('Oson','Oson'),
            ("O'rta","O'rta"),
            ("Qiyin","Qiyin"),
            ("Murakkab","Murakkab"),
        )
    )
    timeout = models.DurationField(default=timezone.timedelta(seconds=10))
    kontest = models.ForeignKey(
        Kontest,
        on_delete=models.CASCADE,
        related_name='masalalar'
    )
    
    ball = models.IntegerField(default=5)
    hidden = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def umumiy_javoblar(self):
        return 4==self.objects.ishlaganlar.filter(user=self.user, masala=self, state='🟢 Passed').count()

    def togri_yechimlar(self):
        return UserMasalaRelation.objects.filter(state='🟢 Passed').count()
    
    def qatnashuvchilar(self):
        return self.ishlaganlar.values('user').distinct().count()



class UserKontestRelation(models.Model):
    kontest = models.ForeignKey(
        Kontest,
        on_delete=models.CASCADE,
        related_name='users'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='kontests'
    )

class UserMasalaRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ishlangan_masalalar',
    )
    masala = models.ForeignKey(
        Masala,
        on_delete=models.CASCADE,
        related_name='ishlaganlar'
    )
    language = models.CharField(
        max_length=150,
        choices=(
            ('C++','C++'),
            ('C','C'),
            ('Java', 'Java'),
            ('Python','Python')
        )
    )
    script = models.FileField(upload_to=upload_to)
    script_result = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        max_length=150,
        default='Waiting...'
    )
    class Meta:
        ordering = ["-time"]

    def get_script_result(self):
        try:
            print(self.masala.tests.all())
            inputs, outputs = [], []
            for test in self.masala.tests.all():
                inputs.append(test.kirish)
                outputs.append(test.output)
                print("Added test", test)
            with open(self.script.path) as f:
                code = Code(self.id, inputs, outputs, f.read())
            passed = False
            if code.precheck() == "Correct code":
                passed = code.check() == "Correct code"

            if passed:
                self.state = '🟢 Passed'
            else:
                self.state = '🔴 Failed'
        except Exception as err:
            raise err
            self.state = "🔴 timeout"
        self.save()

    def save(self):
        super().save()


class Test(models.Model):
    masala = models.ForeignKey(
        Masala,
        on_delete=models.CASCADE,
        related_name='tests'
    )
    kirish = models.TextField(max_length=150)
    output = models.CharField(max_length=150)
