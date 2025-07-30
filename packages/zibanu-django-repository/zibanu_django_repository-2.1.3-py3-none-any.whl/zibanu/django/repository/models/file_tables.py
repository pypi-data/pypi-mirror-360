# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/02/25
# Project:      Zibanu Django
# Module Name:  tables
# Description:
# ****************************************************************
from .file import File
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models


class FileTables(models.Model):
    """
    File table model storage.
    """
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_query_name="file_tables", related_name="file_tables")
    tables = models.JSONField(default=dict, blank=False, null=False, editable=False)

    class Meta:
        """ Metaclass for FileTables model. """
        verbose_name = _("File tables")
        verbose_name_plural = _("File tables")

