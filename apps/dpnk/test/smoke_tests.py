
from project import urls
from nose_parameterized import parameterized
from dpnk import views, util
from dpnk.models import UserAttendance, Team
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.test import TestCase, RequestFactory, Client
from django.test.utils import override_settings
from django.utils.translation import activate
import datetime

activate('cs')
views = [
    "/rest/gpx/",
    "%s?uid=1" % reverse('admin_questionnaire_answers', kwargs={'competition_slug': "FQ-LB"}),
    reverse('admin_questionnaire_results', kwargs={'competition_slug': "FQ-LB"}),
    reverse('admin_draw_results', kwargs={'competition_slug': "FQ-LB"}),
    reverse('admin_draw_results', kwargs={'competition_slug': "vykonnost"}),
    reverse('admin_draw_results', kwargs={'competition_slug': "quest"}),
    reverse('admin_draw_results', kwargs={'competition_slug': "TF"}),
    "%s?question=1" % reverse('admin_answers', urls),
    reverse('login'),
    reverse('admin_questions', urls),
    reverse('payment', urls),
    reverse('profil', urls),
    reverse('zmenit_tym'),
    reverse('upravit_trasu'),
    reverse('upravit_profil'),
    reverse('zmenit_triko'),
    reverse('company_admin_pay_for_users'),
    reverse('invoices'),
    reverse('edit_company'),
    reverse('rides_details'),
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
    reverse('competitions'),
    reverse('competition-rules-city', kwargs={'city_slug': "testing-city"}),
    reverse('competition_results', kwargs={'competition_slug': "FQ-LB"}),
    reverse('competition_results', kwargs={'competition_slug': "quest"}),
    reverse('competition_results', kwargs={'competition_slug': "vykonnost"}),
    reverse('competition_results', kwargs={'competition_slug': "TF"}),
    reverse('questionnaire_answers_all', kwargs={'competition_slug': "FQ-LB"}),
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
class BaseViewsTests(TestCase):
    fixtures = ['campaign', 'auth_user', 'users', 'test_results_data', 'trips']

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST="testing-campaign.testserver")
        self.assertTrue(self.client.login(username='test', password='test'))
        call_command('denorm_init')
        util.rebuild_denorm_models(Team.objects.filter(pk=1))
        util.rebuild_denorm_models(UserAttendance.objects.get(pk=1115).team.all_members())

    def tearDown(self):
        call_command('denorm_drop')

    def verify_views(self, view, status_code=200):
        response = self.client.get(view, follow=True)
        filename = view.replace("/", "_")
        if response.status_code != status_code:
            with open("error_%s.html" % filename, "w") as f:
                f.write(response.content.decode())
        self.assertEqual(response.status_code, status_code, "%s view failed, the failed page is saved to error_%s.html file." % (view, filename))


class ViewSmokeTests(BaseViewsTests):
    @parameterized.expand(views)
    def test_dpnk_views(self, view):
        status_code_map = {
            'error404.txt': 404,
        }
        status_code = status_code_map[view] if view in status_code_map else 200
        self.verify_views(view, status_code)


class ViewSmokeTestsRegistered(BaseViewsTests):
    fixtures = ['campaign', 'auth_user', 'users', 'batches', 'transactions', 'test_results_data', 'trips']

    def setUp(self):
        super().setUp()
        user_attendance = UserAttendance.objects.get(pk=1115)
        self.assertTrue(user_attendance.entered_competition())

    @parameterized.expand(views)
    def test_dpnk_views(self, view):
        status_code_map = {
            reverse('typ_platby'): 403,
            'error404.txt': 404,
        }
        status_code = status_code_map[view] if view in status_code_map else 200
        self.verify_views(view, status_code)
