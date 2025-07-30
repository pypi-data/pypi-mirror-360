# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/02/25
# Project:      Zibanu Django
# Module Name:  file
# Description:
# ****************************************************************
from django.db.models.signals import post_delete
from django.dispatch import receiver
from zibanu.django.repository.models import FileExtended, File


@receiver(post_delete, sender=FileExtended)
def file_extended_post_delete(sender, instance, **kwargs):
    """
    Receiver function for post_delete signal in FileExtended model.

    Parameters
    ----------
    sender: Model
        Source from this function is called.
    instance: FileExtended
        Instance from this function is called.
    kwargs: dict
        Keyword arguments passed to the receiver function.

    Returns
    -------
    None
    """
    file = instance.file
    file.delete()
