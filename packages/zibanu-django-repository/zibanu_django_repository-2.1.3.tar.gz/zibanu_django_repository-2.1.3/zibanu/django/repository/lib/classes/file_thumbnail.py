# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         9/04/25
# Project:      Zibanu Django
# Module Name:  file_thumbnail
# Description:
# ****************************************************************
import logging
from django.core.files import File
from PIL import Image
from tempfile import TemporaryFile

class FileThumbnail:
    """ FileThumbnail class """
    def __init__(self, file: File, width: tuple[int, int] = (100, 100)):
        """ FileThumbnail constructor """
        self.__file = file
        self.__valid_file = False
        self.__size = width
        self.__thumbnail = self.__create_thumbnail()


    @property
    def is_valid(self):
        """ Si valid property to indicate that file is a valid image. """
        return self.__valid_file

    @property
    def thumbnail(self):
        """ Thumbnail image created with this class. """
        return self.__thumbnail


    def __create_thumbnail(self):
        tmp_file = None
        try:
            if self.__file is not None and isinstance(self.__file, File):
                img = Image.open(self.__file)
                img.thumbnail(self.__size)
                tmp_file = TemporaryFile()
                img.save(tmp_file, format=img.format)
        except Exception as e:
            logging.error(str(e))
            tmp_file = None
        else:
            self.__valid_file = True
        finally:
            return tmp_file