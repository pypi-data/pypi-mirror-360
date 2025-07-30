"""
Settings model for the TNNT Discord bot.
"""

# Standard Library
from typing import Any

# Third Party
from solo.models import SingletonModel

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth Discord Bot
from aadiscordbot.models import Channels


class Setting(SingletonModel):
    """
    Settings model for the TNNT Discord bot.
    This model is used to store settings that are not expected to change frequently.
    """

    class Field(models.TextChoices):
        """
        Choices for the setting field.
        """

        APPLICANT_ROLE_NAME = "applicant_role_name", _("Applicant Role Name")
        APPLICANT_ROLE_ID = "applicant_role_id", _("Applicant Role ID")
        RECRUITING_CHANNEL = "recruiting_channel", _("Recruiting Channel")
        RECRUITER_ROLE_ID = "recruiter_role_id", _("Recruiter Role ID")
        LEADERSHIP_ROLE_ID = "leadership_role_id", _("Leadership Role ID")
        WELCOME_CHANNEL_AUTHENTICATED = "welcome_channel_authenticated", _(
            "Welcome Channel (Authenticated User)"
        )
        WELCOME_CHANNEL_UNAUTHENTICATED = "welcome_channel_unauthenticated", _(
            "Welcome Channel (Unauthenticated User)"
        )
        WELCOME_ROLES_EXCLUDED = "welcome_roles_excluded", _("Roles Excluded")

    # Recruitment Cog Settings
    applicant_role_name = models.CharField(
        max_length=100,
        default="",
        verbose_name=Field.APPLICANT_ROLE_NAME.label,  # pylint: disable=no-member,
        help_text=_("The name of the role for applicants in the Discord server."),
    )

    applicant_role_id = models.PositiveBigIntegerField(
        null=True,
        default=None,
        verbose_name=Field.APPLICANT_ROLE_ID.label,  # pylint: disable=no-member
        help_text=_("The ID of the role for applicants in the Discord server."),
    )

    recruiting_channel = models.ForeignKey(
        to=Channels,
        related_name="+",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=Field.RECRUITING_CHANNEL.label,  # pylint: disable=no-member
        help_text=_("The channel used for recruiting in the Discord server."),
    )

    recruiter_role_id = models.PositiveBigIntegerField(
        null=True,
        default=None,
        verbose_name=Field.RECRUITER_ROLE_ID.label,  # pylint: disable=no-member
        help_text=_("The ID of the role for recruiters in the Discord server."),
    )

    leadership_role_id = models.PositiveBigIntegerField(
        null=True,
        default=None,
        verbose_name=Field.LEADERSHIP_ROLE_ID.label,  # pylint: disable=no-member
        help_text=_("The ID of the role for leadership in the Discord server."),
    )

    # Welcome Cog Settings
    welcome_channel_authenticated = models.ForeignKey(
        to=Channels,
        related_name="+",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=Field.WELCOME_CHANNEL_AUTHENTICATED.label,  # pylint: disable=no-member
        help_text=_(
            "The channel to send welcome messages for authenticated users in the Discord server."
        ),
    )

    welcome_channel_unauthenticated = models.ForeignKey(
        to=Channels,
        related_name="+",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=Field.WELCOME_CHANNEL_UNAUTHENTICATED.label,  # pylint: disable=no-member
        help_text=_(
            "The channel to send welcome messages for unauthenticated users in the Discord server."
        ),
    )

    welcome_roles_excluded = models.CharField(
        max_length=255,
        default="Member",
        verbose_name=Field.WELCOME_ROLES_EXCLUDED.label,  # pylint: disable=no-member
        help_text=_(
            "Comma-separated list of Discord roles that are excluded from the welcome message."
        ),
    )

    class Meta:
        """
        Meta options for the Setting model.
        """

        default_permissions = ()
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")

    def __str__(self):
        """
        String representation of the Setting model.

        :return:
        :rtype:
        """

        return str(_("Settings"))

    @staticmethod
    def get_setting(setting_key: str) -> Any:
        """
        Get the setting value for a given setting key

        :param setting_key: The setting key
        :type setting_key: str
        :return: The setting value
        :rtype: Any
        """

        try:
            return getattr(Setting.get_solo(), setting_key)
        except AttributeError as exc:
            raise KeyError(f"Setting key '{setting_key}' does not exist.") from exc
