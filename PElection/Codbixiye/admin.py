from django.contrib import admin

# Register your models here.

from .models import codbixiye_DB

# @admin.register(codbixiye_DB)
class codbixiyeAdmin(admin.ModelAdmin):
    list_display =['c_id', 'c_department', 'c_musharax']
    list_filter =['c_department', 'c_musharax']
    search_fields =['c_id']

admin.site.register(codbixiye_DB, codbixiyeAdmin)
    

