import os
import subprocess

from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from ckeditor.fields import RichTextField

from users.models import User
from django.conf import settings


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
            self_folder = os.path.join(settings.MEDIA_ROOT, "scripts", str(self.id))
            passed = True
            print(self_folder, self.id, 145)
            for num, test in enumerate(self.masala.tests.all()):
                subprocess.run(["touch",str(os.path.join(settings.MEDIA_ROOT, "scripts", str(self.id), f"input{num}.txt"))])
                with open(str(os.path.join(settings.MEDIA_ROOT, "scripts", str(self.id), f"input{num}.txt")), "w") as txt:
                        txt.write(test.kirish)
                if self.language == 'C++':
                    result = subprocess.run(["docker", "run", "--rm", "-v", f"{self_folder}:/scripts", "gcc:latest", "sh", "-c", f"g++ /scripts/{os.path.basename(self.script.url)} -o /scripts/result && /scripts/result < /scripts/input{num}.txt"], check=True, capture_output=True)
                    self.script_result = result.stdout.decode().strip()
                    if self.script_result == test.output:
                        passed = True
                    else:
                        passed = False
                elif self.language == 'C':
                    result = subprocess.run(["docker", "run", "--rm", "-v", f"{self_folder}:/scripts", "gcc:latest", "sh", "-c", f"gcc /scripts/{os.path.basename(self.script.url)} -o /scripts/result && /scripts/result < /scripts/input{num}.txt"], check=True, capture_output=True)
                    self.script_result = result.stdout.decode().strip()
                    if self.script_result == test.output:
                        passed = True
                    else:
                        passed = False
                elif self.language == 'Java':
                    result = subprocess.run(["docker", "run", "--rm", "-v", f"{self_folder}:/scripts", "openjdk:latest","sh","-c",f"javac /scripts/{os.path.basename(self.script.url)} && java -cp /scripts {os.path.basename(self.script.url).split('.')[0]} < /scripts/input{num}.txt"], check=True, capture_output=True)
                    self.script_result = result.stdout.decode().strip()
                    if self.script_result == test.output:
                        passed = True
                    else:
                        passed = False
                elif self.language == 'Python':
                    result = subprocess.run(["docker", "run", "--rm", "-v", f"{self_folder}:/scripts", "python:3.9", "sh", "-c", f"python /scripts/{os.path.basename(self.script.url)} < /scripts/input{num}.txt"], check=True, capture_output=True)
                    self.script_result = result.stdout.decode().strip()
                    if self.script_result == test.output:
                        passed = True
                    else:
                        passed = False
            if passed:
                self.state = '🟢 Passed'
            else:
                self.state = '🔴 Failed'
        except Exception as err:
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
    hidden = models.BooleanField(default=True)