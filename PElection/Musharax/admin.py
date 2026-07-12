from django.contrib import admin

# Register your models here.

from .models import musharax_DB

# @admin.register(musharax_DB)
class MusharaxAdmin(admin.ModelAdmin):
    list_display =['m_joined', 'm_name']
    search_fields =['m_joined', 'm_name']
    list_filter =['m_name']

    # def has_add_permission(self, request):
    #     return False

   
    # def has_change_permission(self, request, obj=None):
    #     return False

  
    # def has_delete_permission(self, request, obj=None):
    #     return False
    
admin.site.register(musharax_DB, MusharaxAdmin)