from django.contrib import admin

from .models import Kontest, Masala, UserKontestRelation, UserMasalaRelation, Test


class TestAdmin(admin.TabularInline):
    model = Test

class MasalaAdmin(admin.ModelAdmin):
    inlines = [TestAdmin]

admin.site.register(Kontest)
admin.site.register(Masala, MasalaAdmin)
admin.site.register(UserKontestRelation)
admin.site.register(UserMasalaRelation)
# admin.site.register(Test)
