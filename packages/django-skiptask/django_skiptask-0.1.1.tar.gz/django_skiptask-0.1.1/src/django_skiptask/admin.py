from django.contrib import admin

from . import models

admin.site.register(models.Queueable, admin.ModelAdmin)
admin.site.register(models.Task, admin.ModelAdmin)
admin.site.register(models.Attempt, admin.ModelAdmin)
