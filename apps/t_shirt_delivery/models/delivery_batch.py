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
import collections
import datetime
import subprocess
from io import StringIO

from author.decorators import with_author

from django.contrib.gis.db import models
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from dpnk.models import Subsidiary

from .package_transaction import PackageTransaction, Status
from .t_shirt_size import TShirtSize
from .team_package import TeamPackage
from .. import batch_csv
from ..gls.generate_gls_pdf import generate_pdf


@with_author
class DeliveryBatch(models.Model):
    """Dávka objednávek"""

    created = models.DateTimeField(
        verbose_name=_("Datum vytvoření"),
        default=datetime.datetime.now,
        null=False,
    )
    campaign = models.ForeignKey(
        "dpnk.Campaign",
        verbose_name=_("Kampaň"),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    customer_sheets = models.FileField(
        verbose_name=_("Zákaznické listy"),
        upload_to="customer_sheets",
        blank=True,
        null=True,
        max_length=512,
    )
    tnt_order = models.FileField(
        verbose_name=_("CSV objednávka"),
        upload_to="csv_delivery",
        blank=True,
        null=True,
        max_length=512,
    )
    order_pdf = models.FileField(
        verbose_name=_("PDF objednávky"),
        upload_to="pdf_delivery",
        blank=True,
        null=True,
        max_length=512,
    )
    combined_opt_pdf = models.FileField(
        verbose_name=_("Kombinované PDF pro OPT"),
        upload_to="pdf_opt_delivery",
        blank=True,
        null=True,
        max_length=512,
    )
    dispatched = models.BooleanField(
        verbose_name=_("Vyřízeno"),
        blank=False,
        null=False,
        default=False,
    )
    note = models.CharField(
        verbose_name=_("Krátká poznámka"),
        max_length=255,
        null=True,
        blank=True,
    )
    pickup_date = models.DateField(
        verbose_name=_("Datum vyzvednutí"),
        default=datetime.datetime.now,
        null=False,
    )

    class Meta:
        verbose_name = _("Dávka objednávek")
        verbose_name_plural = _("Dávky objednávek")
        db_table = "t_shirt_delivery_deliverybatch"

    def __str__(self):
        return "id %s vytvořená %s" % (
            self.id,
            self.created.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def box_count(self):
        return self.subsidiarybox_set.count()

    def team_package_count(self):
        return TeamPackage.objects.filter(box__delivery_batch=self).count()

    def submit_gls_order_pdf(self):
        pdf_filename, pdf_ext = generate_pdf(self.tnt_order, self)
        with open(pdf_filename, "rb+") as f:
            date_time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"batch_{self.id}_{date_time_str}.{pdf_ext}"
            self.order_pdf.save(filename, f)
        self.save()
        subprocess.call(["rm", "tmp_gls/", "-r"])

    def t_shirt_count(self):
        return PackageTransaction.objects.filter(
            team_package__box__delivery_batch=self
        ).count()

    def t_shirt_size_counts(self, campaign=None):
        if hasattr(self, "campaign"):
            campaign = self.campaign
        if not self.pk:
            package_transactions = campaign.user_attendances_for_delivery()
            t_shirts = TShirtSize.objects.filter(
                userattendance__in=package_transactions
            )
            t_shirts = t_shirts.annotate(size_count=models.Count("userattendance"))
        else:
            package_transactions = PackageTransaction.objects.filter(
                team_package__box__delivery_batch=self
            )
            t_shirts = TShirtSize.objects.filter(
                packagetransaction__in=package_transactions
            )
            t_shirts = t_shirts.annotate(size_count=models.Count("packagetransaction"))
        t_shirt_counts = t_shirts.values_list("name", "size_count")
        ordered_t_shirt_counts = collections.OrderedDict(
            [
                (size.name, 0)
                for size in TShirtSize.objects.filter(
                    campaign=campaign,
                ).order_by("name")
            ]
        )
        for count in t_shirt_counts:
            ordered_t_shirt_counts[count[0]] = count[1]
        return ordered_t_shirt_counts.items()

    @transaction.atomic
    def add_packages(self, user_attendances=None):
        from .team_package import TeamPackage
        from .package_transaction import PackageTransaction
        from .subsidiary_box import SubsidiaryBox

        if not user_attendances:
            user_attendances = self.campaign.user_attendances_for_delivery()
        for subsidiary in (
            Subsidiary.objects.filter(teams__users__in=user_attendances)
            .order_by("city__slug")
            .distinct()
        ):
            t_shirt_count_in_box = None
            subsidiary_box = None
            for team in subsidiary.teams.filter(users__in=user_attendances).distinct():
                if (
                    t_shirt_count_in_box is None
                    or t_shirt_count_in_box + team.members().count()
                    > self.campaign.package_max_count
                ):
                    if subsidiary_box is not None:
                        subsidiary_box.add_packages_on_save = True
                        subsidiary_box.save()
                    subsidiary_box = SubsidiaryBox(
                        delivery_batch=self,
                        subsidiary=subsidiary,
                    )
                    subsidiary_box.add_packages_on_save = False
                    subsidiary_box.save()
                    t_shirt_count_in_box = 0

                t_shirt_count_in_package = None
                for user_attendance in (
                    user_attendances.distinct() & team.all_members().distinct()
                ):
                    if user_attendance.t_shirt_size.ship:
                        if (
                            t_shirt_count_in_package is None
                            or t_shirt_count_in_package >= 5
                        ):
                            team_package = TeamPackage.objects.create(
                                box=subsidiary_box,
                                team=team,
                            )
                            t_shirt_count_in_package = 0
                        t_shirt_count_in_package += 1
                        t_shirt_count_in_box += 1
                        PackageTransaction.objects.create(
                            team_package=team_package,
                            user_attendance=user_attendance,
                            status=Status.PACKAGE_ACCEPTED_FOR_ASSEMBLY,
                        )
            subsidiary_box.add_packages_on_save = True
            subsidiary_box.save()


@receiver(post_save, sender=DeliveryBatch)
def create_delivery_files(sender, instance, created, **kwargs):
    if created and getattr(instance, "add_packages_on_save", True):
        instance.add_packages()

    if not instance.tnt_order and getattr(instance, "add_packages_on_save", True):
        buf = StringIO()
        batch_csv.generate_csv(buf, instance)
        file_name = "delivery_batch_%s_%s.csv" % (
            instance.pk,
            instance.created.strftime("%Y-%m-%d"),
        )
        buf.seek(0)
        read_content = buf.read()
        read_content = read_content.encode("utf-8")
        temp_read = ContentFile(read_content, name=file_name)
        instance.tnt_order.save(file_name, temp_read)
        instance.save()
