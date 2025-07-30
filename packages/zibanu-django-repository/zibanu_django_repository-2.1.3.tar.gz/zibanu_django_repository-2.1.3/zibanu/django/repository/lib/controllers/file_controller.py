# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/03/25
# Project:      Zibanu Django
# Module Name:  file_controller
# Description:
# ****************************************************************
import logging
import traceback
import os
import io
from uuid import uuid4
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from zibanu.django.lib import BaseModelController, FileUtils, CodeGenerator, get_ip_address, get_request_from_stack
from zibanu.django.repository.lib.classes import FileMetadata, FileThumbnail
from zibanu.django.repository.models import File
from typing import Any

class FileController(BaseModelController):
    """ FileController class """
    def __init__(self, pk: int = None, **kwargs: dict[str, ...]) -> None:
        """ Constructor for FileController class"""
        super().__init__(**kwargs)
        self._hash_method = settings.ZB_REPOSITORY_HASH_METHOD
        self._root_dir = settings.ZB_REPOSITORY_ROOT_DIR
        self._files_dir = settings.ZB_REPOSITORY_FILES_DIR
        self._thumbnail_dir = settings.ZB_REPOSITORY_THUMBNAILS_DIR
        self._multi_level_allowed = settings.ZB_REPOSITORY_MULTILEVEL_FILES_ALLOWED
        self._mixin_files_allowed = settings.ZB_REPOSITORY_MIX_FILES_CATS_ALLOWED
        self._versioning = settings.ZB_REPOSITORY_VERSIONING
        self._media_dir = settings.MEDIA_ROOT


    class Meta:
        """ Metaclass for FileController """
        model = File
        fields = ["id", "code", "uuid", "generated_at", "description", "file_type", "checksum", "owner_id"]
        related_fields = ["file_extended", "file_tables"]

    @staticmethod
    def __validate_file(attrs) -> bool:
        """
        Validate the file attributes to save or not.
        Parameters
        ----------
        attrs: dict
            Dictionary of file attributes.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        b_return = True
        file_extended = attrs.get("file_extended", {})
        file_type = attrs.get("file_type", None)

        if len(file_extended) > 0:
            category = file_extended.get("category", None)
            if category is not None:
                file_types = category.file_types
                if file_type is not None and file_types is not None and file_type not in file_types:
                    raise ValidationError(_(f"Invalid file type '{file_type}'"))
                # Validate that the file could not be loaded on root category.from
                if category.is_root:
                    raise ValidationError(_(f"The root category does not support files upload."))
                if not category.files_allowed:
                    raise ValidationError(_(f"The category does not support files upload."))
        return b_return

    @staticmethod
    def __get_metadata(file: FileUtils) -> dict:
        """
        Get metadata from file.

        Parameters
        ----------
        file: FileUtils
            File object with file properties.

        Returns
        -------
        dict
            Dictionary of file metadata.
        """
        f_meta = FileMetadata(file)
        return f_meta.metadata

    @staticmethod
    def __get_ip_address() -> str:
        """
        Get the IP Address of the uploaded file
        Returns
        -------
        str
            IP Address of the uploaded file.
        """
        try:
            request = get_request_from_stack()
            ip_address = get_ip_address(request)
        except:
            ip_address = ""
        return ip_address

    def __save_thumbnail(self, file: FileUtils) -> None:
        try:
            f_thumbnail = FileThumbnail(file.file, width=(150, 150))
            file_dir = os.path.join(self._root_dir, self._thumbnail_dir)
            # If thumbnail is valid, save it
            if f_thumbnail.is_valid:
                img_thumb = f_thumbnail.thumbnail
                thumb_file = FileUtils(file=img_thumb, file_dir=file_dir, overwrite=True, file_name=file.file_name)
                thumb_file.save()
            else:
                raise ValidationError(_("Invalid file to generate thumbnail."))
        except ValidationError:
            raise
        except Exception as e:
            logging.error(str(e))
            logging.debug(traceback.format_exc())


    def save_from_file(self, file: Any, attrs: dict[str, ...]) -> None:
        """
        Save and populate entities from the file.

        Parameters
        ----------
        file: Any
            File stream of bytes
        attrs: dict
            Dictionary of file attributes.

        Returns
        -------
        None
        """
        extract_metadata = False
        gen_thumbnail = False
        file_dir = os.path.join(self._root_dir, self._files_dir)
        file = FileUtils(file=file, hash_method=self._hash_method, file_dir=file_dir, overwrite=True)
        file_save = True
        # Load category to get flags
        category = attrs.get("file_extended", {}).get("category", None)
        if category is not None:
            # Load extract_metadata flag
            if hasattr(category, "extract_metadata"):
                extract_metadata = category.extract_metadata
            # Load gen_thumb flag
            if hasattr(category, "gen_thumb"):
                gen_thumbnail = category.gen_thumb


        if self.is_adding:
            # If it is a new file.
            code_gen = CodeGenerator(action="save_from_file")
            attrs["generated_at"] = file.created_at
            attrs["file_type"]  = file.file_suffix
            attrs["checksum"] = file.hash
            attrs["owner"] = self.request.user
            attrs["uuid"] = self._instance.uuid
            attrs["code"] = code_gen.get_alpha_numeric_code()
            attrs["mime_type"] = file.mime_type
        else:
            #If is it an old file.
            if self._instance.checksum != file.hash:
                file.created_at = self._instance.generated_at
                attrs["checksum"] = file.hash
                attrs["uuid"] = uuid4()
                attrs["file_type"] = file.file_suffix
                attrs["mime_type"] = file.mime_type
                attrs["owner"] = self.request.user
                # *****************************************************************************
                # COMMENT: Add the version file if the file exists and if VERSIONING system setting is True
                # Modified by: macercha
                # Modified at: 2025-06-19, 19:16
                # *****************************************************************************
                if self._versioning:
                    attrs["version"] = self._instance.version + 1
            else:
                file_save = False

        try:
            old_version_file = self._instance.version
            if file_save:
                # Set the properties of the file extended model.
                attrs["file_extended"]["ip_address"] = self.__get_ip_address()
                # Get metadata if the flag is True
                if extract_metadata:
                    attrs["file_extended"]["metadata"] = self.__get_metadata(file)

                # *****************************************************************************
                # COMMENT: Set the properties of the file version model, if the versioning system setting is True
                # Modified by: macercha
                # Modified at: 2025-06-19, 19:22
                # *****************************************************************************
                if self._versioning and not self.is_adding:
                    attrs["file_versions"] = []
                    # Load the pre-existing versions of the file
                    if hasattr(self._instance, "file_versions") and self._instance.file_versions is not None:
                        for file_version in self._instance.file_versions.all():
                            attrs["file_versions"].append(
                                {
                                    "id": file_version.id,
                                    "uuid": file_version.uuid,
                                    "owner": file_version.owner,
                                    "version": file_version.version
                                }
                            )

                    attrs["file_versions"].append(
                        {
                            "uuid": self._instance.uuid,
                            "owner": self.request.user,
                            "version": self._instance.version
                        }
                    )

            # Validate attrs to save in db.
            if self.__validate_file(attrs):
                self.save(attrs)
            # Save the file only if the new is different from the old.
            if file_save:
                file.file_name = self._instance.file_name
                # Get the thumbnail image if the flag is True
                if gen_thumbnail:
                    self.__save_thumbnail(file)
                file.save()
        except IOError as e:
            logging.error(str(e))
            logging.debug(traceback.format_exc())
            raise IOError(_("Error saving file"))
        except Exception as e:
            logging.error(str(e))
            logging.debug(traceback.format_exc())
            raise e



