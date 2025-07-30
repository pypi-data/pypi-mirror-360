# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/02/23 16:27
# Project:      Zibanu Django Project
# Module Name:  document_generator
# Description:
# ****************************************************************
import logging
import os
import traceback
import uuid
import hashlib
from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateDoesNotExist
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from typing import Any
from xhtml2pdf import pisa

from zibanu.django.db.models import QuerySet
from zibanu.django.lib import CodeGenerator
from zibanu.django.repository.lib.utils import get_path
from zibanu.django.repository.models import File
from rest_framework.request import Request


class DocumentGenerator:
    """
    Class to generate a new document PDF document from django template definition.
    """

    def __init__(self, template_prefix: str, custom_dir: str = None, file_uuid: str = None) -> None:
        """
        Class constructor

        Parameters
        ----------
        template_prefix: Path template prefix
        custom_dir: Custom dir for save pdf document
        file_uuid: UUID to assign to the document.
        """
        self.__custom_dir = custom_dir
        self.__template_prefix = template_prefix
        self.__description = ""
        self.__generated = None

        if not template_prefix.endswith("/"):
            self.__template_prefix += "/"

        if template_prefix.startswith("/"):
            self.__template_prefix = self.__template_prefix[1:]

        if hasattr(settings, "MEDIA_ROOT"):
            self.__directory = self.__get_directory()
        else:
            logging.critical(_("The 'MEDIA_ROOT' setting has not been defined."))
            logging.debug(traceback.format_exc())
            raise ValueError(_("The 'MEDIA_ROOT' setting has not been defined."))

    @property
    def description(self) -> str:
        """
        Property with document's description.

        Returns
        -------
        description: String with document's description.
        """
        return self.__description

    @property
    def generated_at(self) -> datetime:
        """
        Property to get the field "generated_at" from document.

        Returns
        -------
        generated_at: DateTime value from document's generated_at field.
        """
        return self.__generated

    def __get_directory(self, **kwargs) -> str:
        """
        Private method to get the full path from document, year and month parameters in **kwargs

        Parameters
        ----------
        **kwargs: Dictionary with parameters. The valid parameters are, document, year and month.

        Returns
        -------
        path: String with representative path.
        """
        year = date.today().year
        month = date.today().month
        directory_base = get_path(settings.ZB_REPOSITORY_ROOT_DIR, settings.ZB_REPOSITORY_FILES_DIR, custom_dir=kwargs.get("custom_dir", None), use_media=True)
        file = kwargs.get("file", None)
        if file is None:
            # Legacy code
            file = kwargs.get("document", None)

        if file is not None and isinstance(file, File):
            file = kwargs.get("document")
            year = file.generated_at.year
            month = file.generated_at.month
        elif {"year", "month"} <= kwargs.keys():
            year = kwargs.get("year")
            month = kwargs.get("month")

        directory_base = get_path(directory_base, str(year), str(month))
        return directory_base

    def __get_qs(self, kwargs) -> QuerySet:
        """
        Private method to construct a query set filtered by uuid or code.

        Parameters
        ----------
        **kwargs: Dictionary with keys uuid or code for construct the filter.

        Returns
        -------
        queryset: Queryset from document model
        """

        if "uuid" in kwargs:
            file_qs = File.objects.get_by_uuid(kwargs.get("uuid"))
        elif "code" in kwargs:
            file_qs = File.objects.get_by_code(kwargs.get("code"))
        else:
            raise ValueError(_("Key to get document does not found."))
        return file_qs

    def generate_from_template(self, template_name: str, context: dict, **kwargs: dict[str: Any]) -> str:
        """
        Method to generate a document from django template.

        Parameters
        ----------
        template_name: Template name to construct the pdf document.
        context: Context dictionary to override context constructor.
        **kwargs: Dictionary with vars to template like "description", "request", "key" and "user". User is mandatory.

        Returns
        -------
        hex: String with hex uuid from generated document.
        """
        try:
            # Load vars from kwargs
            # Changes by Macercha
            # 2025-02-13
            description: str = kwargs.get("description", "")
            request: Request|None = kwargs.get("request", None)
            key = kwargs.get("key", "code")
            if request is None:
                user = kwargs.get("user", None)
                if user is None:
                    raise ValueError(_("User is required."))
            else:
                user = request.user
            # Created directory if it does not exist
            directory = self.__get_directory()
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Get validation code from key or create it
            # Modified by macercha at 2023/06/03
            if key in context:
                validation_code = context.get(key)
            else:
                code_generator = CodeGenerator(action="rep_doc_generator")
                validation_code = code_generator.get_alpha_numeric_code(length=10)
            # Set uuid for filename and uuid file
            file_uuid = uuid.uuid4()
            # Set filename with path and uuid and create it
            file_name = get_path(directory, file_uuid.hex + ".pdf")
            # Load template and render it
            template_name = self.__template_prefix + template_name
            template = get_template(template_name)
            rendered = template.render(context=context, request=request)
            # Generate pdf
            file_handler = open(file_name, "w+b")
            pisa_status = pisa.CreatePDF(rendered, file_handler)
            if not pisa_status.err:
                # Create hash from file.
                if settings.ZB_REPOSITORY_HASH_METHOD == "sha256":
                    file_hash = hashlib.sha256(file_handler.read()).hexdigest()
                elif settings.ZB_REPOSITORY_HASH_METHOD == "sha1":
                    file_hash = hashlib.sha1(file_handler.read()).hexdigest()
                elif settings.ZB_REPOSITORY_HASH_METHOD == "sha224":
                    file_hash = hashlib.sha224(file_handler.read()).hexdigest()
                else:
                    file_hash = hashlib.md5(file_handler.read()).hexdigest()
                file = File(code=validation_code, uuid=file_uuid, owner=user, description=description, checksum=file_hash)
                file.save()
                file_handler.close()
            else:
                file_handler.close()
                os.remove(file_name)
                logging.error(_("Error generating pdf file"))
                raise Exception(_("Error generating pdf file"))
        except OSError:
            logging.critical(_("The file cannot be created."))
            raise OSError(_("The file cannot be created."))
        except TemplateDoesNotExist:
            raise TemplateDoesNotExist(_("Template %s does not exist." % template_name))
        except TemplateSyntaxError:
            raise TemplateSyntaxError(_("Syntax error in the template %s") % template_name)
        else:
            return file_uuid.hex

    def get_file(self, user, **kwargs) -> str:
        """
        Get a file pathname of document filtering from user (mandatory) and uuid or code values.

        Parameters
        ----------
        user: User object to get the document.
        **kwargs: Dictionary with "uuid" or "code" keys to get the right document.

        Returns
        -------
        path_filename: Document path filename
        """
        if user is None:
            raise ValueError(_("User is required."))

        document_qs = self.__get_qs(kwargs)

        if document_qs.count() > 0:
            document = document_qs.first()
            self.__description = document.description
            self.__generated = document.generated_at
            if user == document.owner:
                path_filename = os.path.join(self.__get_directory(document=document), document.uuid.hex + '.pdf')
                if not os.path.exists(path_filename):
                    raise ObjectDoesNotExist(_("Document file does not exist."))
            else:
                raise ValidationError(_("User does not have permissions to get this document."))
        else:
            raise ObjectDoesNotExist(_("Document does not exist."))
        return path_filename

    def get_document(self, **kwargs) -> File:
        """
        Get a document from defined filters in **kwargs

        Parameters
        ----------
        **kwargs: Dictionary with keys and values for filter construct.

        Returns
        -------
        document: Document object that matches the filter.
        """
        return self.__get_qs(kwargs).first()
