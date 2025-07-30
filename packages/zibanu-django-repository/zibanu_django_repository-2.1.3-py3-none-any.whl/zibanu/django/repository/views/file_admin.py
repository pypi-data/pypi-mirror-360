# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         20/02/25
# Project:      Zibanu Django
# Module Name:  file_admin_view
# Description:
# ****************************************************************
from django import forms
from django.apps import apps
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from zibanu.django.lib import FileUtils
from zibanu.django.repository.lib.controllers import FileController
from zibanu.django.repository.models import Category
from zibanu.django.repository.models import File as FileModel


class FileAdminCustomForm(forms.ModelForm):
    """
    Custom form to edit file repository from admin.
    """
    source_file = forms.FileField(required=False)
    category = forms.TypedChoiceField(choices=[], coerce=int)
    title = forms.CharField(required=True, max_length=255, help_text=_("The title of the file"), label=_("Title"),
                            widget=forms.TextInput(attrs={"class": "form-control", "style": "max-width: 600px;"}))
    description = forms.CharField(required=True, max_length=255, help_text=_("The description of the file"),
                                  label=_("Description"), widget=forms.Textarea(attrs={"rows": 4, "cols": 80}))
    published = forms.BooleanField(required=False, help_text=_("Publish the file"), label=_("Publish"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        """ Metaclass of FileAdminCustomForm. """
        fields = [
            "title",
            "description",
            "category",
            "published",
            "source_file",
        ]

    def clean(self):
        """
        Override Clean method of FileAdminCustomForm.

        Returns
        -------
        None
        """
        self.cleaned_data = super(FileAdminCustomForm, self).clean()
        file = FileUtils(file=self.cleaned_data["source_file"])
        category = Category.objects.get(pk=self.cleaned_data.get("category"))
        self.cleaned_data["category"] = category

        # Validate
        if self.instance._state.adding and len(self.files) == 0:
            raise forms.ValidationError(_("No files selected."))

        # Validate if category is root.
        if category.is_root:
            raise ValidationError({"source_file": _("The category does not support files upload.")})

        # Validate file type.
        if file.is_valid:
            file_types = [] if category.file_types is None else category.file_types.split(",")
            if len(file_types) > 0 and file.file_suffix not in file_types:
                raise ValidationError({"source_file": _("The file type is not supported.")})

        # Validate if category allow files upload.
        if not category.files_allowed:
            raise ValidationError({"source_file": _("The category does not allow files upload.")})

        return self.cleaned_data


class FileAdminView(admin.ModelAdmin):
    """
    File admin view.
    """
    form = FileAdminCustomForm
    list_display = (
        "file_extended__title",
        "description",
        "file_extended__category",
        "file_extended__published",
        "generated_at"
    )
    list_filter = ("file_extended__category", "file_extended__published")
    sortable_by = ("file_extended__category", "file_extended__title", "generated_at")
    actions = ["publish_files", "unpublish_files"]
    ordering = ["generated_at"]
    list_per_page = 20
    search_fields = ["file_extended__title", "description"]

    @staticmethod
    def __get_category_choices() -> list:
        """
        Static and private method to load sorted choices list from Category model manager.
        Returns
        -------
        choices : list
        """
        app = apps.get_app_config("zb_repository")
        if app.is_ready:
            qs = Category.objects.get_categories_files_allowed(published=True)
            choices = [(x.id, x.__str__()) for x in sorted(qs.all(), key=lambda rcq: rcq.__str__())]
        else:
            choices = []
        return choices



    @staticmethod
    def file_extended__title(instance: FileModel) -> str:
        """ File extended title field to display. """
        if instance.file_extended is not None:
            title = instance.file_extended.title
        else:
            title = instance.uuid
        return title

    @staticmethod
    def file_extended__category(instance: FileModel) -> str:
        """ File extended category field to display. """
        if instance.file_extended is not None:
            category = instance.file_extended.category
        else:
            category = _("N/A")
        return category

    @staticmethod
    def file_extended__published(instance: FileModel) -> str:
        """ File extended published field to display. """
        html_str = "<img src='{}' alt={}/>"
        images_source = ["/static/admin/img/icon-no.svg", "/static/admin/img/icon-yes.svg"]
        if instance.file_extended is not None:
            published = instance.file_extended.published
        else:
            published = False

        return format_html(html_str.format(images_source[published], published))

    @admin.action(description=_("Publish selected files"))
    def publish_files(self, request, queryset):
        """ Admin action to publish selected files. """
        for instance in queryset:
            if instance.file_extended is not None:
                instance.file_extended.published = True
                instance.file_extended.save()

    @admin.action(description=_("Unpublish selected files"))
    def unpublish_files(self, request, queryset):
        """ Admin action to unpublish selected files. """
        for instance in queryset:
            if instance.file_extended is not None:
                instance.file_extended.published = False
                instance.file_extended.save()

    def get_form(self, request, obj: FileModel = None, **kwargs):
        """
        Get form object.

        Parameters
        ----------
        request: Request
            HTTP request object.
        obj: Model
            Instance of model.
        kwargs: dict[str, Any]
            Dictionary of keyword arguments.

        Returns
        -------
        Form:
            Form object.
        """
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        # *****************************************************************************
        # COMMENT: Add sorted choices load from Category model manager
        # Modified by: macercha
        # Modified at: 2025-05-13, 14:37
        # *****************************************************************************
        form.base_fields["category"] = forms.TypedChoiceField(choices = self.__get_category_choices(), coerce=int)
        if obj is not None and hasattr(obj, "file_extended") and obj.file_extended is not None:
            form.base_fields["title"].initial = obj.file_extended.title
            form.base_fields["category"].initial = obj.file_extended.category_id
            form.base_fields["published"].initial = obj.file_extended.published
        else:
            form.base_fields["title"].initial = ""
            form.base_fields["category"].initial = ""
            form.base_fields["published"].initial = True
        return form

    def save_model(self, request, obj, form, change):
        """
        Save model changes.

        Parameters
        ----------
        request: Request
            HTTP request object.
        obj: Model
            Instance of model.
        form: FileAdminCustomForm
            Form object.
        change: bool
            Flag to indicate whether change is needed.
        Returns
        -------
        None
        """
        # *****************************************************************************
        # COMMENT: Change all procedure to isolate code and use FileController class
        # Modified by: macercha
        # Modified at: 2025-03-05, 05:05
        # *****************************************************************************
        upload_file = form.cleaned_data.pop("source_file", None)
        file_data = {
            "description": form.cleaned_data.get("description"),
            "file_extended": {
                "title": form.cleaned_data.get("title"),
                "category": form.cleaned_data.get("category"),
                "published": form.cleaned_data.get("published")
            }
        }
        file_controller = FileController(pk=None, instance=obj)
        if upload_file:
            file_controller.save_from_file(upload_file, file_data)
        else:
            file_controller.save(file_data)
