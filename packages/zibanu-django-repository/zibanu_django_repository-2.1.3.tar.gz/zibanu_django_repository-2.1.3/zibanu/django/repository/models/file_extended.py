# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         15/02/25
# Project:      Zibanu Django
# Module Name:  file_extended
# Description:
# ****************************************************************
from .file import File
from .category import Category
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models
from zibanu.django.repository.lib.enums import AccessTypeEnum


class FileExtended(models.DatedModel):
    """
    File extended model to extend some properties from File model.
    """
    file = models.OneToOneField(File, on_delete=models.CASCADE, blank=False, null=False, related_query_name="file_extended", related_name="file_extended")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False, verbose_name=_("Category"), help_text=_("The category of the file"))
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("Title"), help_text=_("The title of the file"))
    metadata = models.JSONField(default=dict, blank=False, null=False, editable=False)
    access_type = models.IntegerField(choices=AccessTypeEnum.choices, default=AccessTypeEnum.PUBLIC, verbose_name=_("Access type"), help_text=_("The access type of the file"))
    published = models.BooleanField(default=False, verbose_name=_("Published"), help_text=_("The published status of the file"))
    # *****************************************************************************
    # COMMENT: ADD IP Address to extend information.
    # Modified by: macercha
    # Modified at: 2025-04-05, 17:28
    # *****************************************************************************
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP address"), help_text=_("The IP address of the file"), editable=False)

    class Meta:
        """
        Metaclass for FileExtended.
        """
        verbose_name = _("File Extended Properties")
        verbose_name_plural = _("File Extended Properties")
