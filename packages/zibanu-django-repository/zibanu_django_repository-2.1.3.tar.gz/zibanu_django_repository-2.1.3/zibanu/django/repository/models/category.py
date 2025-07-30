# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/02/25
# Project:      Zibanu Django
# Module Name:  category
# Description:
# ****************************************************************
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from zibanu.django.db import models
from zibanu.django.repository.lib.enums import SortType, SortBy
from zibanu.django.repository.lib.managers.category import CategoryManager


class Category(models.Model):
    """
    Category model
    """
    name = models.CharField(max_length=150, null=False, blank=False, verbose_name=_("Name"), help_text=_("Name of category"))
    level = models.IntegerField(default=0, null=False, blank=False, verbose_name=_("Level"), validators=[MinValueValidator(0)], help_text=_("Level of category."), editable=False)
    gen_thumb = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Generate thumbnails"), help_text=_("Generate thumbnails for this category if file type is compatible."))
    gen_ml = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Generate ML files"), help_text=_("Generate ML files for this category. Only for image files."))
    extract_metadata = models.BooleanField(default=True, null=False, blank=False, verbose_name=_("Generate metadata"), help_text=_("Generate metadata for this category if file type is compatible."))
    extract_tables = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Extract tables"), help_text=_("Extract tables for this category. Only for pdf files."))
    file_types = models.CharField(blank=True, null=True, max_length=150, verbose_name=_("File types allowed"), help_text=_("File types allowed for this category."), validators=[RegexValidator(r"^(?:[a-z0-9]{2,6})(?:\s*,\s*[a-z0-9]{2,6})*$")])
    published = models.BooleanField(default=True, null=False, blank=False, verbose_name=_("Published"), help_text=_("Publish this category"))
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("Parent category"), help_text=_("Parent category"))
    uuid = models.UUIDField(default=uuid4, editable=False, help_text=_("UUID for this category"), unique=True, verbose_name=_("UUID"))
    # *****************************************************************************
    # COMMENT: Add sorting features
    # Modified by: macercha
    # Modified at: 2025-04-12, 16:20
    # *****************************************************************************
    sort_by = models.IntegerField(default=SortBy.NAME, choices=SortBy.choices, verbose_name=_("Sort by"), help_text=_("Sort by this category"))
    sort_type = models.IntegerField(default=SortType.ASC, choices=SortType.choices, verbose_name=_("Sort type"), help_text=_("Sort type category"))
    # Set manager
    objects = CategoryManager()

    class Meta:
        """
        Metaclass for Category model
        """
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return (self.parent.__str__() + " // " if self.parent else "") + self.name

    @property
    def is_root(self):
        """ Property to indicate if this category is a root category. """
        return self.parent is None

    @property
    def has_children(self) -> bool:
        """ Property to indicate if this category has children categories published. """
        return Category.objects.get_children_count(self.id, True) > 0

    @property
    def has_files(self) -> bool:
        """ Property to indicate if this category has files published. """
        from zibanu.django.repository.models.file import File
        return File.objects.get_by_category(self.id).count() > 0

    @property
    def root_category(self):
        """ Property to get the root category of this category. """
        return Category.objects.get_root_category(self.id)

    @property
    def files_allowed(self) -> bool:
        b_return = True
        from django.conf import settings
        mixin_files_allowed = settings.ZB_REPOSITORY_MIX_FILES_CATS_ALLOWED
        multi_level_allowed = settings.ZB_REPOSITORY_MULTILEVEL_FILES_ALLOWED
        max_level_allowed = settings.ZB_REPOSITORY_MAX_LEVEL_ALLOWED
        # If not multi level allowed and this category does not max level.
        if not multi_level_allowed and self.level < max_level_allowed:
            b_return = False
        else:
            # If mixin files and categories are not allowed and self category has children categories.
            if not mixin_files_allowed and self.has_children:
                b_return = False
        return b_return

    def clean(self) -> None:
        """
        Override method to do validation of entity record.

        Returns
        -------
        None
        """
        from django.conf import settings
        max_level_allowed = settings.ZB_REPOSITORY_MAX_LEVEL_ALLOWED - 1

        # Validate level and root definition.
        if self.is_root:
            self.level = 0
            self.gen_thumb = False
            self.gen_ml = False
            self.extract_metadata = False
            self.extract_tables = False
            self.file_types = None
        else:
            try:
                parent = Category.objects.get(id=self.parent.id)
                self.level = parent.level + 1
            except Category.DoesNotExist:
                raise ValidationError({"parent": _("Parent category does not exist.")})

        if self.level > max_level_allowed:
            raise ValidationError( _("The levels of this category is not allowed."))

        # If not multilevel files allowed.
        if not settings.ZB_REPOSITORY_MULTILEVEL_FILES_ALLOWED:
            if self.level < max_level_allowed:
                if self.gen_ml or self.gen_thumb or self.extract_metadata or self.extract_tables or self.file_types:
                    raise ValidationError({"parent": _("This category cannot contains files. Level is lower than the maximum level set.")})

        if not settings.ZB_REPOSITORY_MIX_FILES_CATS_ALLOWED:
            if self.parent is not None and self.parent.has_files:
                raise ValidationError({"parent": _("Parent category has files and cannot contains sub-categories.")})

        if self.file_types is not None:
            self.file_types = self.file_types.lower()
        # Validate extract tables only for pdf files.
        if self.extract_tables:
            if self.file_types is None:
                raise ValidationError({"extract_tables": _("File types must be defined to enable extract tables.")})
            if "pdf" not in self.file_types:
                raise ValidationError({"extract_tables": _("Extract tables is not supported for this file types.")})
        # Invokes super class method
        super().clean()

    def save(self, *args, **kwargs) -> None:
        """
        Override method to do cascade published update.

        Parameters
        ----------
        args: tuple
            Non-qualified arguments to pass to super()
        kwargs: dict[str, Any]
            Keyword arguments to pass to super()
        Returns
        -------
        None
        """
        if not self._state.adding:
            Category.objects.set_children_publish(self.id, self.published)
        super().save(*args, **kwargs)