#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.
#  ********************************************************************************
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with this program.  If not, see
#  <https://www.gnu.org/licenses/>.
#   ********************************************************************************
#  Este programa es software libre: puede redistribuirlo y/o modificarlo bajo los términos de la Licencia General
#  Pública de GNU publicada por la Free Software Foundation, ya sea la versión 3 de la Licencia, o (a su elección)
#  cualquier versión posterior.
#
#  Este programa se distribuye con la esperanza de que sea útil pero SIN NINGUNA GARANTÍA; incluso sin la garantía
#  implícita de MERCANTIBILIDAD o CALIFICADA PARA UN PROPÓSITO EN PARTICULAR. Vea la Licencia General Pública de GNU
#  para más detalles.
#
#  Usted ha debido de recibir una copia de la Licencia General Pública de GNU junto con este programa. Si no, vea
#  <http://www.gnu.org/licenses/>.
#  ********************************************************************************

from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import gettext_lazy as _
from zibanu.django.repository.models import Category

from djangocms_zb_repository.lib import Choices


# Create your models here.

class ZibanuRepositoryPluginModel(CMSPlugin):
    """
    Model representing the Filer Repository entity within the Plugin.
    """
    order = models.CharField(_("Order By"), max_length=50, choices=Choices.ORDER_CHOICES,
                             default=Choices.CREATED_AT_DESC)
    pagination = models.IntegerField(_("Pagination"), help_text=_("Result by page"), default=10)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_("Filter by category"),
                                 related_name="zb_repository_plugin_categories",
                                 related_query_name="zb_repository_plugin_category")
    template = models.CharField(_("Template"), max_length=150, choices=Choices.TEMPLATES_CHOICES,
                                default=Choices.TEMPLATES_CHOICES[0][0],
                                help_text=_("(HTML) Alternative template for the design of list files.")
                                )
    target = models.CharField(_("Link Target"), max_length=7, null=True, blank=True,
                              choices=Choices.TARGET)
