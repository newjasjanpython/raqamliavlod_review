from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_image = models.ImageField(upload_to="pfiles/", null=True, blank=True)
    telefon = models.CharField(max_length=20, default="Kiritilmagan")
    telegram = models.CharField(max_length=150, default="Kiritilmagan")
    viloyat = models.CharField(max_length=100, default="Kiritilmagan")
    tuman = models.CharField(max_length=100, default="Kiritilmagan")
    maktab = models.CharField(max_length=300, default="Kiritilmagan")
    def __str__(self):
        return self.first_name
    
    def get_all_balls(self):
        res = self.ishlangan_masalalar.filter(state='🟢 Passed').aggregate(models.Sum('masala__ball'))['masala__ball__sum']
        # self.ishlangan_masalalar.filter(state='🟢 Passed').annotate(sum_ball=Sum('masala__ball')).first()
        return res if res else 0
