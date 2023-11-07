# from django.contrib import admin
# from .models import *
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
# # Register your models here.

# class ChatSessionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'user', 'created_at')

# class UserAdmin(BaseUserAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         # If superuser, show all users, otherwise exclude superusers
#         if request.user.is_superuser:
#             return qs
#         return qs.filter(is_superuser=False)

#     def has_change_permission(self, request, obj=None):
#         has_class_permission = super().has_change_permission(request, obj)
#         if not has_class_permission:
#             return False
#         if obj is not None and obj.is_superuser and not request.user.is_superuser:
#             return False
#         return True

# # Unregister the original User admin and register the custom one
# # Register the ChatSession model with the custom admin class
# admin.site.unregister(User)
# admin.site.register(ChatSession, ChatSessionAdmin)
# admin.site.register(ChatHistory)
# admin.site.register(User, UserAdmin)

from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Your other admin classes...
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    
class UserAdmin(BaseUserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        # Exclude sensitive fields if the current user is not a superuser
        if not request.user.is_superuser:
            self.exclude = ('is_superuser', 'user_permissions', 'groups')
        else:
            self.exclude = ()
        return super(UserAdmin, self).get_form(request, obj, **kwargs)
    
    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser:
            fieldsets = [
                (None, {'fields': ('username',)}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
            ]
            if not obj:  # This means it's an add form, not a change form
                fieldsets.append(('Password', {'fields': ('password1', 'password2')}))
            fieldsets.append(('Important dates', {'fields': ('last_login', 'date_joined')}))
            return fieldsets
        return super().get_fieldsets(request, obj=obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False)

    def has_change_permission(self, request, obj=None):
        has_class_permission = super().has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and obj.is_superuser and not request.user.is_superuser:
            return False
        return True

    # Add this method to limit staff users from editing users with more privileges
    def has_module_permission(self, request):
        if request.user.is_superuser or request.user.has_perm('auth.view_user'):
            return True
        return False

# Unregister the original User admin and register the custom one
# Register the ChatSession model with the custom admin class
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(ChatSession, ChatSessionAdmin)
admin.site.register(ChatHistory)
# ... Register any other models you have
