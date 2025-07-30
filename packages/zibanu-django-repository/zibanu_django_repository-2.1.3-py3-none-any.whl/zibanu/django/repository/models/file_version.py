# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         19/06/25
# Project:      Zibanu Django
# Module Name:  file_version
# Description:
# ****************************************************************
import django
from .file import File
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models

class FileVersion(models.DatedModel):
    """
    File version model to storage old versions from the File model.
    """
    file = models.ForeignKey(File, on_delete=models.CASCADE, blank=False, null=False, related_name='file_versions', related_query_name='file_versions')
    uuid = models.UUIDField(blank=False, null=False, editable=False)
    version = models.IntegerField(null=False, blank=False, editable=False, validators=[MinValueValidator(1)])
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=False, blank=False)

    class Meta:
        """ Metaclass of FileVersion model"""
        verbose_name = _("File Version")
        verbose_name_plural = _("File Versions")
        if django.VERSION < (4, 1):
            constraints = [
                models.UniqueConstraint(fields=("file", "version"), name="UNQ_file_version")
            ]
        else:
            constraints = [
                models.UniqueConstraint(fields=("file", "version"), name="UNQ_file_version", violation_error_message=_("File version already exists."))
            ]
