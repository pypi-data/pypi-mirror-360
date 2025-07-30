# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/02/25
# Project:      Zibanu Django
# Module Name:  admin_categories_view
# Description:
# ****************************************************************
import logging
from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from zibanu.django.lib.utils import object_to_list
from zibanu.django.repository.models import Category


class CategoriesAdminView(admin.ModelAdmin):
    """ Category Model class."""
    list_display = ("name", "parent", "published", "level")
    fieldsets = (
        (None, {"fields": ("name", "parent")}),
        (_("Features"), {
            "fields": ["gen_thumb", "gen_ml", "extract_metadata", "extract_tables", "file_types", ("sort_by", "sort_type")],
            "classes": ["collapse"],
        }),
        (_("Status"), {"fields": ("published", )})
    )
    actions = ["publish_categories", "unpublish_categories"]
    list_filter = ["parent", "level"]
    sortable_by = ["name", "parent", "published", "level"]
    search_fields = ["name", "parent__name", "parent__parent__name"]
    list_select_related = ["parent"]
    list_per_page = 20

    @staticmethod
    def __get_category_choices() -> list:
        app = apps.get_app_config("zb_repository")
        if app.is_ready:
            qs = Category.objects.get_only_parents()
            choices = [(x.id, x.__str__()) for x in sorted(qs.all(), key=lambda rcq: rcq.__str__())]
        else:
            choices = []
        choices.insert(0, (0, _("None")))
        return choices


    @admin.action(description=_("Publish the selected categorie/s."))
    def publish_categories(self, request: Request, queryset: QuerySet) -> None:
        """
        Method to publish selected categories and its children.
        Parameters
        ----------
        request:
            HTTP request object

        queryset:
            Set of selected categories to do the action on.

        Returns
        -------
        None
        """
        queryset.update(published=True)
        for child in queryset:
            Category.objects.set_children_publish(child.id, True)

    @admin.action(description=_("Unpublish the selected categorie/s."))
    def unpublish_categories(self, request: Request, queryset: QuerySet) -> None:
        """
        Method to unpublish selected categories and its children.
        Parameters
        ----------
        request:
            HTTP request object
        queryset:
            Set of selected categories to do the action on.

        Returns
        -------
        None
        """
        with transaction.atomic():
            queryset.update(published=False)
            for child in queryset:
                Category.objects.set_children_publish(child.id, False)


    def get_form(self, request, obj: Category = None, **kwargs):
        # *****************************************************************************
        # COMMENT: Override clean method to replace factory clean method.
        # Modified by: macercha
        # Modified at: 2025-05-14, 11:39
        # *****************************************************************************
        def override_clean(target_form):
            """ Override method to clean the form before saving it. """
            if target_form.cleaned_data["parent"] == 0:
                target_form.cleaned_data["parent"] = None
            else:
                target_form.cleaned_data["parent"] = Category.objects.get(id=target_form.cleaned_data["parent"])
            return target_form.cleaned_data

        form = super().get_form(request, obj, **kwargs)
        form.base_fields["parent"] = forms.TypedChoiceField(choices=self.__get_category_choices(), coerce=int)
        clean_method = getattr(form, "clean", None)
        if callable(clean_method):
            setattr(form, "clean", override_clean)
        return form


    def save_model(self, request, obj, form, change):
        """ Override save model method. """

        try:
            super().save_model(request, obj, form, change)
        except ValidationError as exc:
            error_list = object_to_list(exc.messages)
            if len(error_list) > 0:
                for message_error in error_list:
                    messages.error(request, message_error)
                    logging.error(message_error)
        except Exception as exc:
            messages.error(request, str(exc))
            logging.error(str(exc))
