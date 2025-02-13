# -*- coding: utf-8 -*-

# Author: Hynek Hanke <hynek.hanke@auto-mat.cz>
# Author: Petr Dlouhý <petr.dlouhy@email.cz>
#
# Copyright (C) 2016 o.s. Auto*Mat
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
import datetime

from django import forms
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import escape
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from rank import Rank, UpperRank

from redactor.widgets import RedactorEditor

from .campaign import Campaign
from .city import City
from .commute_mode import CommuteMode
from .company import Company
from .user_profile import UserProfile
from .. import util


def default_commute_modes():
    return CommuteMode.objects.filter(slug__in=("bicycle", "by_foot"))


class Competition(models.Model):
    """Soutěžní kategorie"""

    CTYPES = (
        ("length", _("Výkonnost")),
        ("frequency", _("Pravidelnost")),
        ("questionnaire", _(u"Dotazník")),
    )

    CCOMPETITORTYPES = (
        ("single_user", _(u"Jednotliví soutěžící")),
        ("liberos", _(u"Liberos")),
        ("team", _(u"Týmy")),
        ("company", _(u"Soutěž organizací")),
    )

    class Meta:
        verbose_name = _(u"Soutěžní kategorie")
        verbose_name_plural = _(u"Soutěžní kategorie")
        ordering = ("-campaign", "-priority", "name")

    name = models.CharField(
        unique=False,
        verbose_name=_("Název soutěže"),
        max_length=160,
        null=False,
    )
    campaign = models.ForeignKey(
        Campaign,
        verbose_name=_(u"Kampaň"),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(
        unique=True,
        default="",
        verbose_name=u"Doména v URL",
        blank=False,
    )
    url = models.URLField(
        default="",
        verbose_name=_("Odkaz na web soutěže"),
        help_text=_("Na webu budou podrobná pravidla o soutěži."),
        null=True,
        blank=True,
    )
    date_from = models.DateField(
        verbose_name=_("Datum začátku soutěže"),
        help_text=_(
            "Od tohoto data (včetně) se počítají jízdy a je možné vyplňovat dotazník"
        ),
        default=None,
        null=True,
        blank=False,
    )
    date_to = models.DateField(
        verbose_name=_("Datum konce soutěže"),
        help_text=_(
            "Do tohoto data (včetně) se počítají jízdy a je možné vyplňovat dotazník"
        ),
        default=None,
        null=True,
        blank=False,
    )
    competition_type = models.CharField(
        verbose_name=_(u"Typ"),
        help_text=_(
            u"Určuje, zdali bude soutěž výkonnostní (na ujetou vzdálenost),"
            u' nebo na pravidelnost. Volba "Dotazník" slouží pro kreativní soutěže,'
            u" cyklozaměstnavatele roku a další dotazníky; je nutné definovat otázky."
        ),
        choices=CTYPES,
        max_length=16,
        null=False,
    )
    competitor_type = models.CharField(
        verbose_name=_("Počet soutěžících"),
        help_text=_(
            u"Určuje, zdali bude soutěž týmová, nebo pro jednotlivce. Ostatní volby vybírejte jen pokud víte, k čemu slouží."
        ),
        choices=CCOMPETITORTYPES,
        max_length=16,
        null=False,
    )
    commute_modes = models.ManyToManyField(
        CommuteMode,
        verbose_name=_("Způsoby dopravy"),
        help_text=_(
            "Můžete vybrat víc položek pomocí klávesy control. Většina soutěží je vypsána jako kolo + pěšky"
        ),
        blank=True,
        default=default_commute_modes,
    )
    city = models.ManyToManyField(
        City,
        verbose_name=_(u"Soutěž pouze pro města"),
        help_text=_(
            u"Soutěž bude probíhat ve vybraných městech. Pokud zůstane prázdné, soutěž probíhá ve všech městech."
        ),
        blank=True,
    )
    company = models.ForeignKey(
        Company,
        verbose_name=_(u"Soutěž pouze pro organizace"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    sex = models.CharField(
        verbose_name=_("Pohlaví soutěžících"),
        help_text=_(
            "Pokud chcete oddělit výsledky pro muže a ženy, je potřeba vypsat dvě soutěže - jednu pro muže a druhou pro ženy. "
            "Jinak nechte prázdné.",
        ),
        choices=UserProfile.GENDER,
        default=None,
        max_length=50,
        null=True,
        blank=True,
    )
    minimum_rides_base = models.PositiveIntegerField(
        verbose_name=_("Minimální základ počtu jízd"),
        help_text=_(
            "Minimální počet jízd, které je nutné si zapsat, aby bylo možné dosáhnout 100% jízd"
        ),
        default=28,
        blank=False,
        null=False,
    )
    public_answers = models.BooleanField(
        verbose_name=_(u"Zveřejňovat soutěžní odpovědi"),
        default=False,
        null=False,
    )
    is_public = models.BooleanField(
        verbose_name=_(u"Soutěž je veřejná"),
        help_text=_("Zobrazovat v přehledech soutěží a výsledků?"),
        default=True,
        null=False,
    )
    show_results = models.BooleanField(
        verbose_name=_("Zobrazovat výsledky soutěže"),
        help_text=_("Povolit možnost prohlížet výsledky soutěže."),
        default=True,
        null=False,
    )
    enable_likes = models.BooleanField(
        verbose_name=_("Povolit likování příspěvků dotazníku"),
        default=False,
        null=False,
    )
    entry_after_beginning_days = models.IntegerField(
        verbose_name=_(u"Prodloužené přihlášky"),
        help_text=_(u"Počet dní po začátku soutěže, kdy je ještě možné se přihlásit"),
        default=7,
        blank=False,
        null=False,
    )
    rules = models.TextField(
        verbose_name=_(u"Pravidla soutěže"),
        default=None,
        blank=True,
        null=True,
    )
    results_text = models.TextField(
        verbose_name=_(u"Text u výsledek"),
        default=None,
        blank=True,
        null=True,
    )
    mandatory = models.BooleanField(
        verbose_name=_("Povinný dotazník"),
        help_text=_("Dotazník je potřeba vyplnit před tím, než je možné zadávat jízdy"),
        default=False,
        null=False,
    )
    priority = models.IntegerField(
        _("Prorita v řazení"),
        help_text=_("Vyšší priorita -> řadí se dřív"),
        default=0,
        blank=False,
        null=False,
    )
    recreational = models.BooleanField(
        verbose_name=_("Započítávají se i rekreační jízdy?"),
        default=False,
    )
    show_charitative_choices = models.BooleanField(
        verbose_name=_("Ukázat volbu charitativní organizace ve výsledích"),
        default=False,
    )

    def get_minimum_rides_base(self):
        return self.minimum_rides_base

    def show_competition_results(self):
        if self.competition_type == "questionnaire" and not self.has_finished():
            return False
        return self.show_results

    def get_competitors(self):
        from .. import results

        return results.get_competitors(self)

    def get_competitors_count(self):
        return self.get_competitors().count()

    def get_results(self):
        from .. import results

        return results.get_results(self)

    def select_related_results(self, results):
        """
        Add select_related objects to the results queryeset
        which are needed to display results.
        """
        if self.competitor_type == "single_user" or self.competitor_type == "libero":
            results = results.select_related(
                "user_attendance__userprofile__user",
                "user_attendance__team__subsidiary__company",
                "user_attendance__team__subsidiary__city",
            )
        elif self.competitor_type == "team":
            results = results.select_related(
                "team__subsidiary__company",
                "team__subsidiary__city",
            )
        elif self.competitor_type == "company":
            results = results.select_related(
                "company",
            )
        return results

    def annotate_results_rank(self, results):
        """
        Annotate results list with lower_rank and upper_rank.
        The result cannot be filtered, so use get_result_id_rank_list function to get the rank list.
        """
        results = results.annotate(
            lower_rank=Rank("result"),
            upper_rank=UpperRank("result"),
        )
        return results

    def get_result_id_rank_dict(self, results):
        """
        Make dict {result_id: (lower_rank, upper_rank)} out from results annotated with their ranks.
        """
        return {
            i[0]: i[1:] for i in results.values_list("id", "lower_rank", "upper_rank")
        }

    def has_started(self):
        if self.date_from:
            return self.date_from <= util.today()
        else:
            return True

    def has_entry_not_opened(self):
        if self.date_from:
            return (
                self.date_from + datetime.timedelta(self.entry_after_beginning_days)
                <= util.today()
            )
        else:
            return False

    def has_finished(self):
        if self.date_to:
            return not self.date_to >= util.today()
        else:
            return False

    def is_actual(self):
        return self.has_started() and not self.has_finished()

    def recalculate_results(self):
        from .. import results

        return results.recalculate_result_competition(self)

    def get_company_querystring(self):
        """
        Returns string with wich is possible to filter results of this competition by company.
        """
        if self.competitor_type in ("single_user", "liberos"):
            return "user_attendance__team__subsidiary__company"
        elif self.competitor_type == "team":
            return "team__subsidiary__company"
        elif self.competitor_type == "company":
            return "company"

    def get_columns(self):
        columns = [("result_order", "get_sequence_range", _("Po&shy;řa&shy;dí"))]

        if (
            self.competitor_type not in ("single_user", "liberos")
            and self.competition_type != "questionnaire"
        ):
            average_string = _(" prů&shy;měr&shy;ně")
        else:
            average_string = ""

        columns.append(
            {
                "length": (
                    "result_value",
                    "get_result",
                    _("Ki&shy;lo&shy;me&shy;trů%s") % average_string,
                ),
                "frequency": (
                    "result_value",
                    "get_result_percentage",
                    _("%% jízd%s") % average_string,
                ),
                "questionnaire": (
                    "result_value",
                    "get_result",
                    _("Bo&shy;dů%s") % average_string,
                ),
            }[self.competition_type],
        )

        if self.competition_type == "frequency":
            columns.append(
                (
                    "result_divident",
                    "get_result_divident",
                    _("Po&shy;čet za&shy;po&shy;čí&shy;ta&shy;ných jí&shy;zd"),
                )
            )
            columns.append(
                (
                    "result_divisor",
                    "get_result_divisor",
                    _("Cel&shy;ko&shy;vý po&shy;čet cest"),
                )
            )
        elif self.competition_type == "length" and self.competitor_type == "team":
            columns.append(
                (
                    "result_divident",
                    "get_result_divident",
                    _(
                        "Po&shy;čet za&shy;po&shy;čí&shy;ta&shy;ných ki&shy;lo&shy;me&shy;trů"
                    ),
                )
            )

        if self.competitor_type not in ("single_user", "liberos", "company"):
            where = {
                "team": _("v&nbsp;tý&shy;mu"),
                "single_user": "",
                "liberos": "",
                "company": _("ve&nbsp;fir&shy;mě"),
            }[self.competitor_type]
            columns.append(
                (
                    "member_count",
                    "team__member_count",
                    _("Po&shy;čet sou&shy;tě&shy;ží&shy;cí&shy;ch %s") % where,
                )
            )

        competitor = {
            "team": "get_team_name",
            "single_user": "user_attendance",
            "liberos": "user_attendance",
            "company": "get_company",
        }[self.competitor_type]
        columns.append(("competitor", competitor, _("Sou&shy;tě&shy;ží&shy;cí")))

        if (
            self.competition_type == "length"
            and self.competitor_type == "single_user"
            and self.show_charitative_choices
        ):
            columns.append(
                ("result_value", "donation_icon", _("Charitativní organizace"))
            )

        if self.competitor_type not in ("team", "company"):
            columns.append(("team", "get_team_name", _("Tým")))

        if self.competitor_type != "company":
            columns.append(("company", "get_company", _("Spo&shy;leč&shy;nost")))

        if self.competitor_type in ("single_user", "liberos"):
            columns.append(("occupation", "get_occupation", _("Pro&shy;fe&shy;se")))
            columns.append(("sex", "get_sex", _("Po&shy;hla&shy;ví")))

        if self.competitor_type != "company":
            columns.append(("city", "get_city", _("Měs&shy;to")))

        return columns

    def has_admission(self, user_attendance):
        if not user_attendance.entered_competition():
            return False
        if self.competitor_type == "liberos" and not user_attendance.is_libero():
            return False
        if (
            self.company
            and user_attendance.team
            and self.company != user_attendance.team.subsidiary.company
        ):
            return False
        if (
            user_attendance.team
            and self.city.exists()
            and not self.city.filter(
                pk=user_attendance.team.subsidiary.city.pk
            ).exists()
        ):
            return False

        return True

    def commute_modes_list(self):
        return ", ".join([str(c) for c in self.commute_modes.all()])

    def city_list(self):
        return ", ".join([str(c) for c in self.city.all()])

    def type_string(self):
        CTYPES_STRINGS = {
            "questionnaire": _("dotazník"),
            "frequency": _("soutěž na pravidelnost"),
            "length": _("soutěž na vzdálenost"),
        }
        CCOMPETITORTYPES_STRINGS = {
            "single_user": _("jednotlivců"),
            "liberos": _("liberos"),
            "team": _("týmů"),
            "company": _("organizací"),
        }
        SEX_STRINGS = {
            "male": _("pro muže"),
            "female": _("pro ženy"),
        }
        if self.company:
            company_string_before = _("vnitrofiremní")
            company_string_after = _("organizace %s") % escape(self.company)
        else:
            company_string_before = ""
            company_string_after = ""

        cities = self.city.all()
        if cities:
            city_string = ungettext_lazy(
                "ve městě %(cities)s",
                "ve městech %(cities)s",
                len(cities),
            ) % {
                "cities": ", ".join([city.name for city in cities]),
            }
        else:
            city_string = ""

        if self.sex:
            sex_string = SEX_STRINGS[self.sex]
        else:
            sex_string = ""

        if self.competition_type != "questionnaire" and self.commute_modes.exists():
            commute_modes_string = "pro cesty s prostředky %s" % ", ".join(
                self.commute_modes.values_list("name", flat=True)
            )
        else:
            commute_modes_string = ""

        return " ".join(
            [
                str(prop)
                for prop in [
                    company_string_before,
                    CTYPES_STRINGS[self.competition_type],
                    CCOMPETITORTYPES_STRINGS[self.competitor_type],
                    company_string_after,
                    city_string,
                    sex_string,
                    commute_modes_string,
                ]
                if str(prop)
            ]
        ).strip()

    def __str__(self):
        return "%s" % self.name

    def clean(self):
        if self.date_to and self.date_from:
            if self.date_to < self.date_from:
                raise ValidationError(
                    {
                        "date_from": _(
                            "Datum začátku soutěže musí být menší, než datum konce soutěže"
                        )
                    }
                )


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        exclude = ()
        widgets = {
            "rules": RedactorEditor(),
            "results_text": RedactorEditor(),
        }

    def save(self, *args, **kwargs):
        competition = super().save(*args, **kwargs)
        if not hasattr(competition, "campaign"):
            competition.campaign = self.request.campaign
        return competition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self.instance, "campaign"):
            if hasattr(self, "request") and hasattr(self.request, "campaign"):
                self.initial["campaign"] = self.request.campaign

        if hasattr(self, "request") and not self.request.user.has_perm(
            "dpnk.can_edit_all_cities"
        ):
            self.fields[
                "city"
            ].queryset = self.request.user.userprofile.administrated_cities
            self.fields["city"].required = True


@receiver(post_save, sender=Competition)
def competition_post_save(sender, instance, **kwargs):
    from .. import tasks

    tasks.recalculate_competitions_results.apply_async(args=((instance.pk,),))
