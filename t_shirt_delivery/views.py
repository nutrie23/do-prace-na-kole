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


from braces.views import LoginRequiredMixin

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import UpdateView

from dpnk.models import UserAttendance
from dpnk.views import RegistrationViewMixin

from .forms import TShirtUpdateForm


class ChangeTShirtView(RegistrationViewMixin, LoginRequiredMixin, UpdateView):
    template_name = 'registration/change_tshirt.html'
    form_class = TShirtUpdateForm
    model = UserAttendance
    success_message = _(u"Velikost trička úspěšně nastavena")
    next_url = 'typ_platby'
    prev_url = 'zmenit_tym'
    registration_phase = "zmenit_triko"
    title = _(u"Upravit velikost trička")

    def get_object(self):
        return self.user_attendance

    def dispatch(self, request, *args, **kwargs):
        if request.user_attendance:
            if not request.user_attendance.team_complete():
                raise PermissionDenied(_("Velikost trička nemůžete měnit, dokud nemáte zvolený tým."))
            if request.user_attendance.package_shipped():
                raise PermissionDenied(_("Vaše tričko již je na cestě k vám, už se na něj můžete těšit."))

            if not request.user_attendance.campaign.has_any_tshirt:
                if request.user_attendance.has_admission_fee():
                    return redirect(reverse('typ_platby'))
                else:
                    return redirect(reverse('profil'))
        return super().dispatch(request, *args, **kwargs)
