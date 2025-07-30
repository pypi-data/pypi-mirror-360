# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/02/23 16:11
# Project:      Zibanu Django Project
# Module Name:  apps
# Description:
# ****************************************************************
import threading
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ZbDjangoRepository(AppConfig):
    """
    Inherited class from django.apps.AppConfig to define configuration for zibanu.django.repository app.
    """
    default_auto_field = 'django.db.models.AutoField'
    name = "zibanu.django.repository"
    label = "zb_repository"
    verbose_name = _("Zibanu Django Repository")
    is_ready = False

    def ready(self):
        """
        Override method used for django application loader after the application has been loaded successfully.

        Returns
        -------
        None

        Settings
        -------
        ZB_REPOSITORY_ROOT_DIR: Name of directory to store the generated documents in MEDIA_ROOT path. Default "ZbRepository"
        """
        default_icon_classes = {
            "default": "fa-regular fa-file",
            "pdf": "fa-regular fa-file-pdf",
            "word": "fa-regular fa-file-word",
            "excel": "fa-regular fa-file-excel",
            "powerpoint": "fa-regular fa-file-powerpoint",
            "image": "fa-regular fa-file-image"
        }
        settings.ZB_REPOSITORY_ROOT_DIR = getattr(settings, "ZB_REPOSITORY_ROOT_DIR", "ZbRepository")
        settings.ZB_REPOSITORY_FILES_DIR = getattr(settings, "ZB_REPOSITORY_FILES_DIR", "ZbFiles")
        settings.ZB_REPOSITORY_THUMBNAILS_DIR = getattr(settings, "ZB_REPOSITORY_THUMBNAILS_DIR", "ZbThumbnails")
        settings.ZB_REPOSITORY_ML_DIR = getattr(settings, "ZB_REPOSITORY_ML_DIR", "ZbML")
        settings.ZB_REPOSITORY_MAX_LEVEL_ALLOWED = getattr(settings, "ZB_REPOSITORY_MAX_LEVEL_ALLOWED", 3)
        settings.ZB_REPOSITORY_MULTILEVEL_FILES_ALLOWED = getattr(settings, "ZB_REPOSITORY_MULTILEVEL_FILES_ALLOWED", True)
        settings.ZB_REPOSITORY_MIX_FILES_CATS_ALLOWED = getattr(settings, "ZB_REPOSITORY_MIX_FILES_CATS_ALLOWED", False)
        settings.ZB_REPOSITORY_HASH_METHOD = getattr(settings, "ZB_REPOSITORY_HASH_METHOD", "md5")
        settings.ZB_REPOSITORY_ICON_CLASSES = getattr(settings, "ZB_REPOSITORY_ICON_CLASSES", default_icon_classes)
        # *****************************************************************************
        # COMMENT: Add a new setting to allow fila versioning system
        # Modified by: macercha
        # Modified at: 2025-06-19, 19:05
        # *****************************************************************************
        settings.ZB_REPOSITORY_VERSIONING = getattr(settings, "ZB_REPOSITORY_VERSIONING", True)

        # *****************************************************************************
        # COMMENT: Add a method to connect some signals with receivers functions.
        # Modified by: macercha
        # Modified at: 2025-03-31, 21:39
        # *****************************************************************************
        # Set a thread to connect signals with receivers.
        th_ready = threading.Thread(target=self.after_ready, name="Zibanu Repository AfterReady Thread")
        th_ready.start()

    def after_ready(self):
        """
        After ready thread event to call signals factory.

        Returns
        -------
        None
        """
        ready_is_set = self.apps.ready_event.wait()
        if ready_is_set and self.apps.ready:
            self.signals_factory()
        self.is_ready = True

    @staticmethod
    def signals_factory():
        """
        Signals factory method to connect some models signals with the receivers.

        Returns
        -------
        None
        """
        from django.db.models.signals import post_delete
        from zibanu.django.repository.lib.receivers import file_extended_post_delete
        post_delete.connect(file_extended_post_delete, sender="zb_repository.fileextended")