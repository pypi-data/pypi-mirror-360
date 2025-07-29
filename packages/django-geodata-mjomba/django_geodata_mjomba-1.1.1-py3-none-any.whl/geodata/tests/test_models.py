from django.test import TestCase
from geodata.models import Country, Region, SubRegion, State, City

class ModelTests(TestCase):
    def setUp(self):
        # Create test data matching real data structure
        # First create region (using ID 3 for Asia)
        self.region = Region.objects.create(
            id=3,
            name="Asia",
            wiki_data_id="Q48",
            translations={
                "ko": "아시아",
                "pt-BR": "Ásia",
                "pt": "Ásia",
                "nl": "Azië",
                "hr": "Azija",
                "fa": "آسیا",
                "de": "Asien",
                "es": "Asia",
                "fr": "Asie",
                "ja": "アジア",
                "it": "Asia",
                "zh-CN": "亚洲",
                "tr": "Asya",
                "ru": "Азия",
                "uk": "Азія"
            }
        )
        
        # Create subregion (using ID 14 for Southern Asia)
        self.subregion = SubRegion.objects.create(
            id=14,
            name="Southern Asia",
            region=self.region,
            wiki_data_id="Q23497",
            translations={
                "ko": "남아시아",
                "pt": "Sul da Ásia",
                "nl": "Zuid-Azië",
                "hr": "Južna Azija",
                "fa": "جنوب آسیا",
                "de": "Südasiens",
                "es": "Asia Meridional",
                "fr": "Asie du Sud",
                "ja": "南アジア",
                "it": "Asia meridionale",
                "zh-CN": "南亚",
                "ru": "Южная Азия",
                "uk": "Південна Азія"
            }
        )
        
        # Create country (using ID 1 for Afghanistan)
        self.country = Country.objects.create(
            id=1,
            name="Afghanistan",
            iso3="AFG",
            iso2="AF",
            numeric_code="004",
            phonecode="93",
            capital="Kabul",
            currency="AFN",
            currency_name="Afghan afghani",
            currency_symbol="؋",
            tld=".af",
            native="افغانستان",
            region=self.region,
            subregion=self.subregion,
            nationality="Afghan",
            timezones=[
                {
                    "zoneName": "Asia/Kabul",
                    "gmtOffset": 16200,
                    "gmtOffsetName": "UTC+04:30",
                    "abbreviation": "AFT"
                }
            ],
            translations={
                "ko": "아프가니스탄",
                "pt-BR": "Afeganistão",
                "pt": "Afeganistão",
                "nl": "Afghanistan",
                "hr": "Afganistan",
                "fa": "افغانستان",
                "de": "Afghanistan",
                "es": "Afganistán",
                "fr": "Afghanistan",
                "ja": "アフガニスタン",
                "it": "Afghanistan",
                "zh-CN": "阿富汗",
                "tr": "Afganistan",
                "ru": "Афганистан",
                "uk": "Афганістан"
            }
        )
        
        # Create state
        self.state = State.objects.create(
            id=1,
            name="Kabul",
            country=self.country,
            country_code="AF",
            country_name="Afghanistan",
            state_code="11",
            type="Province",
            latitude=34.5209,
            longitude=69.1753
        )
        
        # Create city
        self.city = City.objects.create(
            id=1,
            name="Kabul",
            state=self.state,
            state_code="11",
            state_name="Kabul",
            country=self.country,
            country_code="AF",
            country_name="Afghanistan",
            latitude=34.5209,
            longitude=69.1753,
            wiki_data_id="Q1804"
        )

    def test_country_creation(self):
        """Test that a Country can be created"""
        self.assertEqual(self.country.name, "Afghanistan")
        self.assertEqual(self.country.iso2, "AF")
        self.assertEqual(self.country.iso3, "AFG")
        self.assertEqual(self.country.region_id, 3)
        self.assertEqual(self.country.subregion_id, 14)
        self.assertEqual(self.country.translations["zh-CN"], "阿富汗")

    def test_region_creation(self):
        """Test that a Region can be created"""
        self.assertEqual(self.region.name, "Asia")
        self.assertEqual(self.region.id, 3)
        self.assertEqual(self.region.wiki_data_id, "Q48")
        self.assertEqual(self.region.translations["zh-CN"], "亚洲")

    def test_subregion_creation(self):
        """Test that a SubRegion can be created"""
        self.assertEqual(self.subregion.name, "Southern Asia")
        self.assertEqual(self.subregion.region_id, 3)
        self.assertEqual(self.subregion.id, 14)
        self.assertEqual(self.subregion.wiki_data_id, "Q23497")

    def test_state_creation(self):
        """Test that a State can be created"""
        self.assertEqual(self.state.name, "Kabul")
        self.assertEqual(self.state.country_id, 1)
        self.assertEqual(self.state.state_code, "11")
        self.assertEqual(self.state.type, "Province")
        self.assertEqual(self.state.latitude, 34.5209)
        self.assertEqual(self.state.longitude, 69.1753)

    def test_city_creation(self):
        """Test that a City can be created"""
        self.assertEqual(self.city.name, "Kabul")
        self.assertEqual(self.city.state_id, 1)
        self.assertEqual(self.city.country_id, 1)
        self.assertEqual(self.city.state_code, "11")
        self.assertEqual(self.city.latitude, 34.5209)
        self.assertEqual(self.city.longitude, 69.1753)
        self.assertEqual(self.city.wiki_data_id, "Q1804")
