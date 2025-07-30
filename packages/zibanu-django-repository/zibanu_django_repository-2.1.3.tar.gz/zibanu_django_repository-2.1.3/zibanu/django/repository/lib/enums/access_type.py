# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         17/02/25
# Project:      Zibanu Django
# Module Name:  access_type
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models

class AccessTypeEnum(models.IntegerChoices):
    PUBLIC = 0, _("Public")
    READ_ONLY = 1, _("Read only")
    AUTHENTICATED = 2, _("Authenticated")
