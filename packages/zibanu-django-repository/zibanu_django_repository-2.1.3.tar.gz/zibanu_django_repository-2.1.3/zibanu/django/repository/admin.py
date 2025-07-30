# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/02/25
# Project:      Zibanu Django
# Module Name:  admin
# Description:
# ****************************************************************
from django.contrib import admin
from zibanu.django.repository.views import CategoriesAdminView, FileAdminView
from zibanu.django.repository.models import Category, File

admin.site.register(Category, CategoriesAdminView)
admin.site.register(File, FileAdminView)