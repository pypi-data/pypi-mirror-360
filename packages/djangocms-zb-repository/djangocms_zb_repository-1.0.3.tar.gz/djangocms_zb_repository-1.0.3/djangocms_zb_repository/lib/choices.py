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
# Date:         24/02/2025 8:08 a. m.
# Project:      django_cms_plugins
# Module Name:  choices
# Description:  
# ****************************************************************

from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Choices:
    CREATED_AT_ASC = "generated_at"
    CREATED_AT_DESC = "-generated_at"
    TITLE_ASC = "file_extended__title"
    TITLE_DESC = "-file_extended__title"

    ORDER_CHOICES = (
        (CREATED_AT_ASC, _("[Date Generated] From the oldest to the most recent")),
        (CREATED_AT_DESC, _("[Date Generated] From the most recent to the oldest")),
        (TITLE_ASC, _("[Title] A-Z")),
        (TITLE_DESC, _("[Title] Z-A"))
    )

    TARGET = (
        ("_blank", "_blank"),
        ("_parent", "_parent"),
        ("_self", "_self"),
        ("_top", "_top"),
    )

    TEMPLATES_CHOICES = [
        ('default', _('Default')),
    ]
    TEMPLATES_CHOICES += getattr(
        settings,
        'DJANGOCMS_ZB_REPOSITORY_TEMPLATES',
        [],
    )
