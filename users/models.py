from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_image = models.ImageField(upload_to="pfiles/")
    
    def __str__(self):
        return self.first_name
    
    def get_all_balls(self):
        res = self.ishlangan_masalalar.filter(state='🟢 Passed').aggregate(models.Sum('masala__ball'))['masala__ball__sum']
        # self.ishlangan_masalalar.filter(state='🟢 Passed').annotate(sum_ball=Sum('masala__ball')).first()
        return res if res else 0