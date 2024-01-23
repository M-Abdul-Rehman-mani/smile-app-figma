from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (MyUser,UserProfile_step1,UserProfile_step2, UserProfile_step3,DailyQuoteModel,
                     StreakSystem,UserSmileModel,GoalsSettingModel,UserLevelModel, ActivitiesModel)

class UserAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email","id", "name","tc", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name","tc"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name","tc", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email","id"]
    filter_horizontal = []

# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)


@admin.register(UserProfile_step1)
class Step1Admin(admin.ModelAdmin):
    fields = ['step1_age', 'step1_gender', 'step1_username','step_1','user']
    list_display = ['user','step1_age', 'step1_gender', 'step1_username','step_1']

@admin.register(UserProfile_step2)
class Step2Admin(admin.ModelAdmin):
    fields = ['step2_relationship', 'step2_children', 'step2_professional_status','step_2','user']
    list_display = ['user','step2_relationship', 'step2_children', 'step2_professional_status','step_2']


@admin.register(UserProfile_step3)
class Step3Admin(admin.ModelAdmin):
    fields = ['step3_data','step_3','user']
    list_display = ['user','step3_data','step_3']


  

admin.site.register(UserSmileModel)

admin.site.register(StreakSystem)
admin.site.register(GoalsSettingModel)
admin.site.register(UserLevelModel)

admin.site.register(ActivitiesModel)
admin.site.register(DailyQuoteModel)