from model_mommy import mommy


class Competitions:
    def __init__(self, campaigns, companies, commute_modes, **kwargs):
        self.c2010_competition_individual_frequency = mommy.make(
            campaign = campaigns.campaign,
            city = [],
            company = companies.company,
            competitor_type = "single_user",
            date_from = "2010-11-01",
            date_to = "2010-11-15",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Pravidelnost jednotlivců",
            public_answers = False,
            rules = None,
            sex = None,
            slug = "pravidelnost-jednotlivcu",
            competition_type = "frequency",
            minimum_rides_base = 23,
            url = "http://www.dopracenakole.net/url/",
            commute_modes = [commute_modes.bicycle, commute_modes.by_foot],
        )

        self.questionnaire = mommy.make(  # was pk=4
            "dpnk.competition",
            campaign = 339,
            city = [],
            company = None,
            competitor_type = "single_user",
            date_from = "2010-11-01",
            date_to = "2010-12-02",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Dotazník",
            public_answers = True,
            rules = None,
            sex = None,
            slug = "quest",
            competition_type = "questionnaire",
            url = "http://www.dopracenakole.net/url/",
        )

        self.competition_team_questionnaire = mommy.make(  # was pk=13
            "dpnk.competition",
            campaign = 339,
            city = [1],
            company = None,
            competitor_type = "team",
            date_from = "2010-11-01",
            date_to = "2010-12-02",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Dotazník týmů",
            public_answers = True,
            rules = None,
            sex = None,
            slug = "team-questionnaire",
            competition_type = "questionnaire",
            url = "http://www.dopracenakole.net/url/",
        )

        self.competition_mens_performance = mommy.make(  # was pk=5
            "dpnk.competition",
            campaign = 339,
            city = [1],
            company = None,
            competitor_type = "single_user",
            date_from = "2010-11-01",
            date_to = "2010-12-30",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Výkonnost",
            public_answers = False,
            rules = None,
            sex = "male",
            slug = "vykonnost",
            competition_type = "length",
            url = "http://www.dopracenakole.net/url/",
            commute_modes = [1, 2],
        )

        self.competition_team_performance = mommy.make(  # was pk=9
            "dpnk.competition",
            campaign = 339,
            city = [1],
            company = None,
            competitor_type = "team",
            date_from = "2010-11-01",
            date_to = "2010-12-30",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Výkonnost týmů",
            public_answers = False,
            rules = None,
            sex = "male",
            slug = "vykonnost-tymu",
            competition_type = "length",
            url = "http://www.dopracenakole.net/url/",
            commute_modes = [1 2],
        )

        self.city_performance = mommy.make(  # was pk=6
            "dpnk.competition",
            campaign = 339,
            city = [1],
            company = None,
            competitor_type = "single_user",
            date_from = "2010-11-01",
            date_to = "2010-12-30",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Výkonnost ve městě",
            public_answers = False,
            rules = "Competition vykonnostr rules",
            sex = None,
            slug = "vykonnost-mesto",
            competition_type = "length",
            url = "http://www.dopracenakole.net/url/",
            commute_modes = [1 2],
        )

        self.company_performance = mommy.make(  # was pk=8
            "dpnk.competition",
            campaign = 339,
            city = [1],
            company = None,
            competitor_type = "company",
            date_from = "2010-11-01",
            date_to = "2010-12-30",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Výkonnost společností",
            public_answers = False,
            rules = "Competition rules",
            sex = None,
            slug = "vykonnost-spolecnosti",
            competition_type = "length",
            url = "http://www.dopracenakole.net/url/",
            commute_modes = [1 2],
        )

        self.company_regularity = mommy.make(  # was pk=10
            "dpnk.competition",
            campaign = 339,
            city = [1],
            company = 1,
            competitor_type = "company",
            date_from = "2010-11-01",
            date_to = "2010-12-30",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Pravidelnost společností",
            public_answers = False,
            rules = "Competition rules",
            sex = None,
            slug = "pravidelnost-spolecnosti",
            competition_type = "frequency",
            url = "http://www.dopracenakole.net/url/",
            commute_modes = [1 2],
        )

        self.company_questionnaire = mommy.make(  # was pk=11
            "dpnk.competition",
            campaign = 339,
            city = [],
            company = None,
            competitor_type = "company",
            date_from = "2010-11-01",
            date_to = "2010-12-30",
            entry_after_beginning_days = 7,
            is_public = True,
            name = "Dotazník společností",
            public_answers = False,
            rules = "Competition rules",
            sex = None,
            slug = "dotaznik-spolecnosti",
            competition_type = "questionnaire",
            url = "http://www.dopracenakole.net/url/",
        )

    {
        "fields": {
            "campaign": 339,
            "city": [],
            "company": 1,
            "competitor_type": "team",
            "date_from": "2013-05-01",
            "date_to": "2013-06-02",
            "entry_after_beginning_days": 7,
            "is_public": true,
            "name": "Pravidelnost společnosti",
            "public_answers": false,
            "rules": null,
            "sex": null,
            "slug": "FA-testing-campaign-pravidelnost-spolecnosti",
            "competition_type": "frequency",
            "url": "http://www.dopracenakole.net/url/"
        },
        "model": "dpnk.competition",
        "pk": 7
    }
