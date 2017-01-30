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

from django import forms

from dpnk.forms import PrevNextMixin
from dpnk.models import UserAttendance, STATUS

from .models import PackageTransaction, TShirtSize


class TShirtUpdateForm(PrevNextMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ret_val = super().__init__(*args, **kwargs)
        self.fields['t_shirt_size'].required = True
        self.fields['t_shirt_size'].queryset = TShirtSize.objects.filter(campaign=self.instance.campaign, available=True)
        return ret_val

    class Meta:
        model = UserAttendance
        fields = ('t_shirt_size', )


class PackageTransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'] = forms.ChoiceField(choices=STATUS)

    class Meta:
        model = PackageTransaction
        fields = "__all__"