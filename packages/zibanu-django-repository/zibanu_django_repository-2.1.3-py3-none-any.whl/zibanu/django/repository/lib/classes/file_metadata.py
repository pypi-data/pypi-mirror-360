# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/04/25
# Project:      Zibanu Django
# Module Name:  file_metadata
# Description:
# ****************************************************************
import logging
import traceback
import zipfile
import xml.dom.minidom
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from zibanu.django.lib import FileUtils


class FileMetadata:
    def __init__(self, file: FileUtils):
        self.__file = file
        self.__file_bytes = file.file
        self.__metadata = {}
        self.__load_metadata()


    @property
    def metadata(self):
        return self.__metadata

    def __office_metadata(self, document: str = "office") -> dict:
        """
        Private method to load from office files (docx, pptx,
        Returns
        -------
        dict
            Dictionary of metadata.
        """
        try:
            zip_file = zipfile.ZipFile(self.__file.file, mode="r")
            if document == "office":
                doc = xml.dom.minidom.parseString(zip_file.read('docProps/core.xml'))
                doc_elements = doc.documentElement.childNodes
            else:
                doc = xml.dom.minidom.parseString(zip_file.read('meta.xml'))
                if len(doc.documentElement.childNodes) > 0:
                    doc_elements = doc.documentElement.childNodes[0].childNodes
                else:
                    doc_elements = []
            metadata = {}
            for element in doc_elements:
                if len(element.childNodes) > 0:
                    metadata[element.localName] = element.childNodes[0].data
        except:
            metadata = {}
        return metadata

    def __load_metadata(self):
        office_documents = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ]
        open_documents = [
            "application/vnd.oasis.opendocument.text",
            "application/vnd.oasis.opendocument.spreadsheet",
            "application/vnd.oasis.opendocument.presentation"
        ]
        images = [
            "image/jpeg",
            "image/png",
            "image/jpx",
            "image/apng",
            "image/bmp",
            "image/gif",
            "image/heic",
            "image/tiff",
            "image/avif"
        ]
        if self.__file.mime_type == "application/pdf":
            try:
                from pypdf import PdfReader
                pdf = PdfReader(self.__file.file)
                for key, value in pdf.metadata.items():
                    self.__metadata[key.replace("/", "")] = value
            except Exception as e:
                logging.error(str(e))
                logging.debug(traceback.format_exc())
                self.__metadata = {}
        elif self.__file.mime_type in office_documents:
            self.__metadata = self.__office_metadata(document="office")
        elif self.__file.mime_type in open_documents:
            self.__metadata = self.__office_metadata(document="open")
        elif self.__file.mime_type in images:
            try:
                from PIL import Image, ExifTags
                image = Image.open(self.__file.file)
                exif_data = image.getexif()
                # For each tag_id load data and convert if necessary.
                for tag_id in exif_data:
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    data  = exif_data.get(tag_id)
                    if isinstance(data, object):
                        data = str(data)
                    if isinstance(data, bytes):
                        data = data.decode()
                    self.__metadata[tag] = data
            except Exception as e:
                logging.error(str(e))
                logging.debug(traceback.format_exc())
                self.__metadata = {}