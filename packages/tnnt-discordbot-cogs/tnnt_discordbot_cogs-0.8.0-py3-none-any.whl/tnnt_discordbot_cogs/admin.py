"""
Terra Nanotech Discordbot Cogs - Admin Configuration
"""

# Third Party
from solo.admin import SingletonModelAdmin

# Django
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.models.setting import Setting


@admin.register(Setting)
class SettingAdmin(SingletonModelAdmin):
    """
    Setting Admin
    """

    fieldsets = (
        (
            _("Recruitment Cog Settings"),
            {
                "fields": [
                    "applicant_role_name",
                    "applicant_role_id",
                    "recruiting_channel",
                    "recruiter_role_id",
                    "leadership_role_id",
                ]
            },
        ),
        (
            _("Welcome Cog Settings"),
            {
                "fields": [
                    "welcome_channel_authenticated",
                    "welcome_channel_unauthenticated",
                    "welcome_roles_excluded",
                ]
            },
        ),
    )
