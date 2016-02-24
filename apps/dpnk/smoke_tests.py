
from project import urls
from nose_parameterized import parameterized
from dpnk import models, views
from dpnk.models import Team, UserAttendance
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.test import TestCase, RequestFactory, Client
from django.test.utils import override_settings
from django.utils.translation import activate
from model_mommy import mommy
import datetime

activate('cs')
views = [
    reverse('payment', urls),
    reverse('profil', urls),
    reverse('zmenit_tym'),
    reverse('upravit_trasu'),
    reverse('upravit_profil'),
    reverse('zmenit_triko'),
    reverse('working_schedule'),
    reverse('company_admin_pay_for_users'),
    reverse('invoices'),
    reverse('edit_company'),
    reverse('company_admin_competitions'),
    reverse('company_structure'),
    reverse('company_admin_competition'),
    reverse('company_admin_application'),
    reverse('register_admin'),
    reverse('emission_calculator'),
    reverse('package'),
    reverse('typ_platby'),
    reverse('zmenit_triko'),
    reverse('upravit_trasu'),
    reverse('working_schedule'),
    reverse('competitions'),
    reverse('jizdy'),
    reverse('other_team_members_results'),
    reverse('team_members'),
    reverse('zaslat_zadost_clenstvi'),
    reverse('pozvanky'),
    reverse('registration_access'),
    reverse('registrace'),
    reverse('edit_team'),
    reverse('questionnaire', kwargs={'questionnaire_slug': 'quest'}),
    reverse('edit_subsidiary', kwargs={'pk': 1}),
    reverse('payment_beneficiary'),
    'error404.txt',
    reverse(views.daily_distance_json),
    reverse(views.daily_chart),
    reverse(views.statistics, kwargs={'variable': 'ujeta-vzdalenost'}),
    reverse(views.statistics, kwargs={'variable': 'ujeta-vzdalenost-dnes'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-cest'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-cest-dnes'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-zaplacenych'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-prihlasenych'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-soutezicich'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-spolecnosti'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-pobocek'}),
    reverse(views.statistics, kwargs={'variable': 'pocet-soutezicich-firma'}),
]


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class ViewSmokeTests(TestCase):
    fixtures = ['campaign', 'views', 'users']

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST="testing-campaign.testserver")
        self.assertTrue(self.client.login(username='test', password='test'))
        call_command('denorm_init')
        call_command('denorm_rebuild')

    def tearDown(self):
        call_command('denorm_drop')

    def verify_views(self, view, status_code_map):
        status_code = status_code_map[view] if view in status_code_map else 200
        address = view
        response = self.client.get(address, follow=True)
        filename = view.replace("/", "_")
        if response.status_code != status_code:
            with open("error_%s.html" % filename, "w") as f:
                f.write(response.content.decode())
        self.assertEqual(response.status_code, status_code, "%s view failed, the failed page is saved to error_%s.html file." % (view, filename))

    @parameterized.expand(views)
    def test_dpnk_views(self, view):
        """
        test if the user pages work
        """
        status_code_map = {
            reverse('profil'): 200,
            reverse('registration_access'): 200,
            reverse('jizdy'): 403,
            'error404.txt': 404,
        }

        self.verify_views(view, status_code_map)

    @parameterized.expand(views)
    def test_dpnk_views_registered(self, view):
        """
        test if the user pages work after user registration
        """
        user_attendance = UserAttendance.objects.get(userprofile__user__username='test')
        user_attendance.track = 'LINESTRING(0 0,-1 1)'
        user_attendance.t_shirt_size = mommy.make(models.TShirtSize)
        team = Team.objects.get(id=1)
        user_attendance.team = team
        mommy.make(models.Payment, user_attendance=user_attendance, amount=160, status=99)
        user_attendance.save()

        status_code_map = {
            reverse('profil'): 200,
            reverse('registration_access'): 200,
            reverse('typ_platby'): 403,
            'error404.txt': 404,
        }

        self.verify_views(view, status_code_map)