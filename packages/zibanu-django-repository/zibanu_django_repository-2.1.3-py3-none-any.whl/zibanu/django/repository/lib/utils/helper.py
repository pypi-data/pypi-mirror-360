# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/02/25
# Project:      Zibanu Django
# Module Name:  helper
# Description:
# ****************************************************************
import os
from datetime import datetime
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def get_path(*args, **kwargs) -> str:
    use_media = kwargs.pop("use_media", False)
    custom_dir = kwargs.pop("custom_dir", None)
    use_date = kwargs.pop("use_date", False)
    # Analyze custom_dir
    if custom_dir is None:
        custom_dir = ""
    else:
        use_media = False

    if use_media:
        # Validate MEDIA_ROOT to use media directory.
        if not hasattr(settings, "MEDIA_ROOT"):
            raise ValueError(_("The 'MEDIA_ROOT' setting has not been defined."))
        full_path = os.path.join(settings.MEDIA_ROOT, *args)
    else:
        full_path = os.path.join(custom_dir, *args)
    return str(full_path) + "/"

