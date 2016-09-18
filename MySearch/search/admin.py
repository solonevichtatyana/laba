from django.contrib import admin
from .models import URLIndex, URL, Word

# Register your models here.


admin.site.register(URL)
admin.site.register(Word)
