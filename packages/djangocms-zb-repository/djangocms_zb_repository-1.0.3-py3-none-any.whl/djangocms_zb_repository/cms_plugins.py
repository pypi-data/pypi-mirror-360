# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Córdoba"
# Date:         24/02/2025 8:32 a. m.
# Project:      django_cms_plugins
# Module Name:  cms_plugins
# Description:  
# ****************************************************************

import os
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db.models import Q
from django.http import Http404
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

from .models import ZibanuRepositoryPluginModel

from zibanu.django.repository.models import File, Category


@plugin_pool.register_plugin
class DjangoCMSZibanuRepositoryPlugin(CMSPluginBase):
    name = _("Zibanu Repository Extension")
    module = "Zibanu"
    cache = False
    model = ZibanuRepositoryPluginModel

    fieldsets = (
        (_("Main Options"), {
            'fields': ('order', ('pagination', 'category'))
        }),
        (_('Advance Options'), {
            'classes': ('collapse',),
            'fields': (('template', 'target'),),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(published=True)
        return super(DjangoCMSZibanuRepositoryPlugin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def _get_render_template(self, context, instance, placeholder):
        """
        Private method to replace default template in CMS
        :param context: Context CMS Var
        :param instance: Model instance
        :param placeholder: Placeholder
        :return: str: Name of new template
        """
        base_dir = f"djangocms_zb_repository/default/"
        base_template = "plugin.html"
        if instance.template:
            base_dir = f"djangocms_zb_repository/{instance.template}/"

        return os.path.join(base_dir, base_template)

    def get_render_template(self, context, instance, placeholder):
        return self._get_render_template(context, instance, placeholder)

    def render(self, context, instance, placeholder):
        """
        Override method to render template
        :param context: Context CMS Var
        :param instance: Model instance
        :param placeholder: Placeholder
        :return: context
        """
        user = context['request'].user
        file_id = context['request'].POST.get('file_id')
        if file_id is not None and user.is_authenticated and user.has_perms(
                ["zb_repository.change.fileextended", "zb_repository.change.file"]):
            file_instance = File.objects.filter(id=file_id).first()
            if file_instance is not None:
                file_instance.file_extended.published = not file_instance.file_extended.published
                file_instance.file_extended.save()
                file_instance.save()
        categories = Category.objects.get_children(category_id=instance.category_id, published=True)
        files = File.objects.all().order_by("-file_extended__published", instance.order)
        full_category_name = ""
        category_filter = context['request'].GET.get('category')
        search = context['request'].GET.get('search')
        if not user.is_authenticated:
            files = files.filter(file_extended__published=True)
        if category_filter:
            category = Category.objects.filter(id=category_filter).first()
            if category is not None:
                full_category_name = str(category).replace(instance.category.name, "")[3:]
            files = files.filter(file_extended__category_id=int(category_filter))
        if search is not None and len(search) > 0:
            files_search = File.objects.none()
            for word in search.split(" "):
                files_search = files_search.union(
                    files.filter(Q(description__icontains=word) | Q(file_extended__title__icontains=word)))
            files = files_search
        if category_filter is None and search is None:
            files = []
        page = context['request'].GET.get('page', 1)
        try:
            paginator = Paginator(files, instance.pagination)
            files = paginator.get_page(page)
        except:
            raise Http404
        context = super().render(context, instance, placeholder)
        context.update({
            "categories": categories,
            "files": files,
            "paginator": paginator,
            "full_category_name": full_category_name,
            "category_model": Category,
            "file_model": File
        })
        return context
