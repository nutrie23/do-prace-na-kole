# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2017 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from collections import OrderedDict

from betterforms.multiform import MultiModelForm

from django import forms
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from dpnk.forms import PrevNextMixin
from dpnk.models import PACKAGE_STATUSES, UserAttendance, UserProfile

from .models import PackageTransaction, TShirtSize


class ShirtUserAttendanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ret_val = super().__init__(*args, **kwargs)
        self.fields["t_shirt_size"].required = True
        self.fields["t_shirt_size"].queryset = TShirtSize.objects.filter(
            campaign=self.instance.campaign, available=True
        )
        self.fields["t_shirt_size"].label_from_instance = lambda i: i.user_string()
        self.fields["t_shirt_size"].label = _("Vyberte velikost trika")
        self.fields["t_shirt_size"].help_text = format_html(
            _("Podívejte se na {}."),
            format_html(
                "<a target='_blank' href='http://www.dopracenakole.cz/trika'>{}</a>",
                _("vzhled a velikosti triček"),
            ),
        )
        return ret_val

    class Meta:
        model = UserAttendance
        fields = ("t_shirt_size",)


class TelephoneUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["telephone"].label = _("Vyplňte telefonní číslo")
        self.fields["telephone"].help_text = None
        self.fields["telephone_opt_in"].choices = [
            (
                True,
                _(
                    "Chci vědět vše. Včetně novinek ohledně podpory cyklistů ve městech."
                ),
            ),
            (False, _("Chci pouze dostat zprávu o stavu balíčku a registrace.")),
        ]
        self.fields["telephone_opt_in"].label = ""

    class Meta:
        model = UserProfile
        fields = (
            "telephone",
            "telephone_opt_in",
        )
        widgets = {
            "telephone_opt_in": forms.RadioSelect(attrs={"required": True}),
        }


class TShirtUpdateForm(PrevNextMixin, MultiModelForm):
    form_classes = OrderedDict(
        [
            ("userprofile", TelephoneUpdateForm),
            ("userattendance", ShirtUserAttendanceForm),
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_class = "noAsterisks"
        self.helper.form_id = "t-shirt-update-form"


class PackageTransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"] = forms.ChoiceField(choices=tuple(PACKAGE_STATUSES))

    class Meta:
        model = PackageTransaction
        fields = "__all__"
