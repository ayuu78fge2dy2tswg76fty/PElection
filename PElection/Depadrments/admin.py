from django.contrib import admin

# Register your models here.

from .models import depadrments_DB

# @admin.register(depadrments_DB)
class DepadrmentsAdmin(admin.ModelAdmin):
    list_display =[ 'd_name']
    search_fields =[ 'd_name']
    list_filter =['d_name']

    # def has_add_permission(self, request):
    #     return False

   
    # def has_change_permission(self, request, obj=None):
    #     return False

  
    # def has_delete_permission(self, request, obj=None):
    #     return False
admin.site.register(depadrments_DB, DepadrmentsAdmin)

    

