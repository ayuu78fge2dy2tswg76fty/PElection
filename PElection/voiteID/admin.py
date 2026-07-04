from django.contrib import admin
from .models import ID_DB


class IDAdmin(admin.ModelAdmin):
    list_display = ["_c_id", "_is_used", "_created_at"]

   
    # def has_add_permission(self, request):
    #     return False

   
    # def has_change_permission(self, request, obj=None):
    #     return False

  
    # def has_delete_permission(self, request, obj=None):
    #     return False
admin.site.register(ID_DB, IDAdmin)