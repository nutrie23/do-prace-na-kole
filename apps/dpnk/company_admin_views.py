# -*- coding: utf-8 -*-
# Author: Petr Dlouhý <petr.dlouhy@email.cz>
#
# Copyright (C) 2013 o.s. Auto*Mat
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

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404
import datetime
from django.conf import settings
from django.views.generic.edit import UpdateView, FormView, CreateView
from django.views.generic.base import TemplateView
from .decorators import must_be_competitor, must_have_team, request_condition, must_be_company_admin, must_be_in_phase
from .company_admin_forms import SelectUsersPayForm, CompanyForm, CompanyAdminApplicationForm, CompanyAdminForm, CompanyCompetitionForm, SubsidiaryForm
from . import company_admin_forms
from .email import company_admin_register_competitor_mail, company_admin_register_no_competitor_mail
from django.core.urlresolvers import reverse_lazy
from .string_lazy import format_lazy
from .models import Company, CompanyAdmin, Competition, Campaign, UserProfile, Subsidiary
from .views import RegistrationViewMixin
from . import models
from .util import mark_safe_lazy
from registration.backends.simple.views import RegistrationView
import logging
logger = logging.getLogger(__name__)


class CompanyStructure(TemplateView):
    template_name = 'company_admin/structure.html'

    @method_decorator(login_required)
    @must_be_company_admin
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(CompanyStructure, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(CompanyStructure, self).get_context_data(*args, **kwargs)
        context_data['company'] = self.company_admin.administrated_company
        context_data['campaign'] = self.company_admin.campaign
        return context_data


class SelectUsersPayView(FormView):
    template_name = 'base_generic_company_admin_form.html'
    form_class = SelectUsersPayForm
    success_url = reverse_lazy('company_structure')

    def get_initial(self):
        return {
            'company_admin': self.company_admin,
        }

    def form_valid(self, form):
        paing_for = form.cleaned_data['paing_for']
        for userprofile in paing_for:
            for payment in userprofile.payments().all():
                if payment.pay_type == 'fc':
                    payment.status = models.Status.COMPANY_ACCEPTS
                    payment.description = payment.description + "\nFA %s odsouhlasil dne %s" % (self.request.user.username, datetime.datetime.now())
                    payment.save()
                    break
        logger.info("Company admin %s is paing for following users: %s" % (self.request.user, map(lambda x: x, paing_for)))
        return super(SelectUsersPayView, self).form_valid(form)

    @method_decorator(login_required)
    @must_be_company_admin
    @must_be_in_phase("payment")
    @request_condition(lambda r, a, k: not k['company_admin'].can_confirm_payments, _(u"Potvrzování plateb nemáte povoleno"))
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(SelectUsersPayView, self).dispatch(request, *args, **kwargs)


class CompanyEditView(UpdateView):
    template_name = 'base_generic_company_admin_form.html'
    form_class = CompanyForm
    model = Company
    success_url = reverse_lazy('company_structure')

    @method_decorator(login_required)
    @must_be_company_admin
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(CompanyEditView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.company_admin.administrated_company


class CompanyAdminApplicationView(RegistrationView):
    template_name = 'company_admin/registration.html'
    form_class = CompanyAdminApplicationForm
    model = CompanyAdmin
    success_url = reverse_lazy('company_structure')

    def get_initial(self):
        return {
            'campaign': Campaign.objects.get(slug=self.request.subdomain),
        }

    def form_valid(self, form):
        ret_val = super().form_valid(form)
        new_user = self.request.user
        admin = CompanyAdmin(
            motivation_company_admin=form.cleaned_data['motivation_company_admin'],
            administrated_company=form.cleaned_data['administrated_company'],
            campaign=form.cleaned_data['campaign'],
            user=new_user,
        )
        admin.save()

        userprofile = UserProfile(
            user=new_user,
            telephone=form.cleaned_data['telephone'],
        )
        userprofile.save()
        company_admin_register_no_competitor_mail(admin, form.cleaned_data['administrated_company'])
        return ret_val


class CompanyAdminView(RegistrationViewMixin, UpdateView):
    template_name = 'submenu_payment.html'
    form_class = CompanyAdminForm
    model = CompanyAdmin
    success_url = 'profil'
    registration_phase = "typ_platby"
    title = _("Chci se stát správcem organizce")

    @method_decorator(login_required)
    @must_be_competitor
    @must_have_team
    def dispatch(self, request, *args, **kwargs):
        return super(CompanyAdminView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(CompanyAdminView, self).get_context_data(*args, **kwargs)
        old_company_admin = self.user_attendance.team.subsidiary.company.company_admin.filter(campaign=self.user_attendance.campaign).first()
        if old_company_admin and old_company_admin != self.company_admin:
            return {'fullpage_error_message': _(u"Vaše organizce již svého koordinátora má: %s." % old_company_admin)}
        return context_data

    def get_object(self, queryset=None):
        campaign = self.user_attendance.campaign
        try:
            self.company_admin = self.request.user.company_admin.get(campaign=campaign)
        except CompanyAdmin.DoesNotExist:
            self.company_admin = CompanyAdmin(user=self.request.user, campaign=campaign)
        self.company_admin.administrated_company = self.user_attendance.team.subsidiary.company
        return self.company_admin

    def form_valid(self, form):
        ret_val = super(CompanyAdminView, self).form_valid(form)
        company_admin_register_competitor_mail(self.user_attendance)
        return ret_val


class EditSubsidiaryView(UpdateView):
    template_name = 'base_generic_company_admin_form.html'
    form_class = SubsidiaryForm
    success_url = reverse_lazy('company_structure')
    model = Subsidiary

    @method_decorator(login_required)
    @must_be_company_admin
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(EditSubsidiaryView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super(EditSubsidiaryView, self).get_queryset().filter(company=self.company_admin.administrated_company)


class CompanyCompetitionView(UpdateView):
    template_name = 'base_generic_company_admin_form.html'
    form_class = CompanyCompetitionForm
    model = Competition
    success_url = reverse_lazy('company_admin_competitions')

    @method_decorator(login_required)
    @must_be_company_admin
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(CompanyCompetitionView, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        try:
            return super(CompanyCompetitionView, self).get(*args, **kwargs)
        except Http404 as e:
            return HttpResponse(e.message)

    def get_object(self, queryset=None):
        company = self.company_admin.administrated_company
        competition_slug = self.kwargs.get('competition_slug', None)
        campaign = self.company_admin.campaign
        if competition_slug:
            competition = get_object_or_404(Competition.objects, slug=competition_slug)
            if competition.company != company:
                raise Http404(_(u"<div class='text-warning'>K editování této soutěže nemáte oprávnění.</div>"))
        else:
            if Competition.objects.filter(company=company, campaign=campaign).count() >= settings.MAX_COMPETITIONS_PER_COMPANY:
                raise Http404(_(u"<div class='text-warning'>Překročen maximální počet soutěží pro organizaci.</div>"))
            phase = campaign.phase('competition')
            competition = Competition(company=company, campaign=campaign, date_from=phase.date_from, date_to=phase.date_to)
        return competition


class CompanyCompetitionsShowView(TemplateView):
    template_name = 'company_admin/competitions.html'

    @method_decorator(login_required)
    @must_be_company_admin
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(CompanyCompetitionsShowView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(CompanyCompetitionsShowView, self).get_context_data(**kwargs)
        context_data['competitions'] = self.company_admin.administrated_company.competition_set.filter(campaign=self.company_admin.campaign)
        return context_data


class InvoicesView(CreateView):
    template_name = 'company_admin/create_invoice.html'
    template_name_created = 'company_admin/invoices.html'
    form_class = company_admin_forms.CreateInvoiceForm
    success_url = reverse_lazy('invoices')

    def get_initial(self):
        campaign = Campaign.objects.get(slug=self.request.subdomain)
        return {
            'campaign': campaign,
        }

    def get_template_names(self):
        if self.company_admin.company_has_invoices():
            return self.template_name_created
        else:
            return self.template_name

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.company_admin.administrated_company
        self.object.campaign = self.company_admin.campaign
        self.object.save()
        return super(InvoicesView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(InvoicesView, self).get_context_data(*args, **kwargs)
        payments = models.payments_to_invoice(self.company_admin.administrated_company, self.company_admin.campaign)
        context['payments'] = payments
        context['company'] = self.company_admin.administrated_company

        context['invoices'] = self.company_admin.administrated_company.invoice_set.filter(campaign=self.company_admin.campaign)
        return context

    @method_decorator(login_required)
    @must_be_in_phase("invoices")
    @must_be_company_admin
    @request_condition(
        lambda r, a, k: not k['company_admin'].administrated_company.has_filled_contact_information(),
        mark_safe_lazy(format_lazy(
            _(u"Před vystavením faktury prosím <a href='{addr}'>vyplňte údaje o vaší firmě</a>"),
            addr=reverse_lazy('edit_company'))))
    @request_condition(lambda r, a, k: not k['company_admin'].can_confirm_payments, _(u"Vystavování faktur nemáte povoleno"))
    def dispatch(self, request, *args, **kwargs):
        self.company_admin = kwargs['company_admin']
        return super(InvoicesView, self).dispatch(request, *args, **kwargs)
