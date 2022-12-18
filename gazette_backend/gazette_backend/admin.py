from django.contrib import admin

from gazette_backend.models import LostPasswordToken, Edition, Article

admin.site.register(LostPasswordToken)
admin.site.register(Edition)
admin.site.register(Article)

