# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
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

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from dpnk.test.mommy_recipes import CampaignRecipe, UserAttendanceRecipe
from dpnk.test.util import print_response  # noqa

from model_mommy import mommy

import settings


class AdminTestBase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client(HTTP_HOST="testing-campaign.example.com", HTTP_REFERER="test-referer")
        self.user = mommy.make(
            "auth.User",
            is_superuser=True,
            is_staff=True,
            username="foo_username",
        )
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[0])


class DeliveryBatchAdminMasschangeTests(AdminTestBase):
    def test_deliverybatch_masschange(self):
        mommy.make(
            "t_shirt_delivery.DeliveryBatch",
            campaign=CampaignRecipe.make(name="Testing campaign"),
            dispatched="2017-01-01",
            id=1,
        )
        address = reverse('admin:t_shirt_delivery_deliverybatch_changelist')
        post_data = {
            'action': 'mass_update',
            '_selected_action': '1',
        }
        response = self.client.post(address, post_data)
        self.assertContains(response, 'Zákaznické listy:')


class PackageTransactionTests(AdminTestBase):
    def setUp(self):
        super().setUp()
        self.user_attendance = UserAttendanceRecipe.make(
            userprofile__user__email="foo@email.cz",
            userprofile__user__first_name="Null",
            userprofile__user__last_name="User",
            team__subsidiary__address_street="Foo street",
            team__subsidiary__address_psc=11111,
            team__subsidiary__address_city="Foo city",
            team__subsidiary__company__name="Foo company",
            userprofile__telephone="123321123",
            id=3,
        )
        mommy.make(
            "dpnk.Payment",
            user_attendance=self.user_attendance,
            realized="2015-11-12 18:18:40",
            pay_type="c",
            status=99,
        )
        mommy.make(
            "price_level.PriceLevel",
            takes_effect_on=datetime.date(year=2010, month=2, day=1),
            pricable=self.user_attendance.campaign,
        )
        self.user_attendance.save()
        mommy.make(
            "PackageTransaction",
            delivery_batch__campaign=self.user_attendance.campaign,
            delivery_batch__created=datetime.date(year=2015, month=11, day=12),
            delivery_batch__id=1,
            t_shirt_size__campaign=self.user_attendance.campaign,
            t_shirt_size__name="Foo size",
            created="2015-11-12 18:18:40",
            realized="2015-11-12 18:18:40",
            tracking_number=11112117,
            status=99,
            user_attendance=self.user_attendance,
            author=self.user,
            id=7,
        )

    def test_packagetransaction_export(self):
        """
        Test PackageTransactionAdmin export without company
        admin set.
        """
        address = "/admin/t_shirt_delivery/packagetransaction/export/?o=3"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        print_response(response)
        self.assertContains(
            response,
            "7,1,2015-11-12 18:18:40,3,Null User,123321123,"
            "foo@email.cz,2015-11-12 18:18:40,"
            "2015-11-12 18:18:40,99,Foo street ,11111,"
            "Foo city,Foo company,,"
            "Foo size,1,111121170,1-151112-000007,"
            "foo_username",
        )

    def test_packagetransaction_export_company_admin(self):
        """
        Test PackageTransactionAdmin export with company
        admin set.
        """
        mommy.make(
            "dpnk.CompanyAdmin",
            userprofile__user__email="foo_ca@email.cz",
            campaign=self.user_attendance.campaign,
            administrated_company=self.user_attendance.team.subsidiary.company,
            company_admin_approved="approved",
        )
        self.user_attendance.save()
        address = "/admin/t_shirt_delivery/packagetransaction/export/?o=3"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(
            response,
            "7,1,2015-11-12 18:18:40,3,Null User,123321123,"
            "foo@email.cz,2015-11-12 18:18:40,"
            "2015-11-12 18:18:40,99,Foo street ,11111,"
            "Foo city,Foo company,foo_ca@email.cz,"
            "Foo size,1,111121170,1-151112-000007,"
            "foo_username",
        )


class DeliveryBatchAdminTests(AdminTestBase):
    def setUp(self):
        super().setUp()
        campaign = CampaignRecipe.make(
            name="Testing campaign",
        )
        t_shirt_size = mommy.make(
            "TShirtSize",
            campaign=campaign,
            name="Testing t-shirt size",
        )
        delivery_batch = mommy.make(
            "DeliveryBatch",
            campaign=campaign,
            id=1,
        )
        mommy.make(
            "PackageTransaction",
            delivery_batch=delivery_batch,
            t_shirt_size=t_shirt_size,
            _quantity=2,
        )

    def test_deliverybatch_admin_changelist(self):
        address = reverse('admin:t_shirt_delivery_deliverybatch_changelist')
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Testing campaign")
        self.assertContains(response, "field-customer_sheets__url")
        self.assertContains(response, "<span>Testing t-shirt size</span>", html=True)

    def test_deliverybatch_admin_change(self):
        address = reverse(
            'admin:t_shirt_delivery_deliverybatch_change',
            args=(1,),
        )
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Testing t-shirt size: 2")
        self.assertContains(response, "Testing campaign")

    def test_deliverybatch_admin_add(self):
        address = reverse('admin:t_shirt_delivery_deliverybatch_add')
        response = self.client.get(address, follow=True)
        self.assertContains(
            response,
            "<div>"
            "<label>Trik k odeslání:</label>"
            "<p>0</p>"
            "</div>",
            html=True,
        )
        self.assertContains(
            response,
            "<div>"
            "<label>Velikosti trik:</label>"
            "<p>-</p>"
            "</div>",
            html=True,
        )
