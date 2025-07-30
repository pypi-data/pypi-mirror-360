# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         12/04/25
# Project:      Zibanu Django
# Module Name:  sort_type
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models

class SortType(models.IntegerChoices):
    """ Generic sort type enumerator. """
    ASC = 0, _("Ascending")
    DESC = 1, _("Descending")