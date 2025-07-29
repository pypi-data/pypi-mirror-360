import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from geodata.models import Region, SubRegion, Country, State, City


class Command(BaseCommand):
    help = 'Load geographical data from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-cities',
            action='store_true',
            help='Skip loading cities (useful for faster loading during development)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk operations',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Define paths to JSON files
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        regions_file = os.path.join(base_path, 'regions.json')
        subregions_file = os.path.join(base_path, 'subregions.json')
        countries_file = os.path.join(base_path, 'countries.json')
        states_file = os.path.join(base_path, 'states.json')
        cities_file = os.path.join(base_path, 'cities.json')
        
        batch_size = options['batch_size']
        skip_cities = options['skip_cities']

        self.stdout.write('Loading geographical data...')

        try:
            # Load regions
            self.stdout.write('Loading regions...')
            with open(regions_file, encoding='utf-8') as f:
                regions_data = json.load(f)
                for region_data in regions_data:
                    Region.objects.update_or_create(
                        id=region_data['id'],
                        defaults={
                            'name': region_data['name'],
                            'wiki_data_id': region_data.get('wikiDataId'),
                            'translations': region_data.get('translations', {})
                        }
                    )

            # Load subregions
            self.stdout.write('Loading subregions...')
            with open(subregions_file, encoding='utf-8') as f:
                subregions_data = json.load(f)
                for subregion_data in subregions_data:
                    try:
                        region = Region.objects.get(id=subregion_data['region_id'])
                        SubRegion.objects.update_or_create(
                            id=subregion_data['id'],
                            defaults={
                                'name': subregion_data['name'],
                                'region': region,
                                'wiki_data_id': subregion_data.get('wikiDataId'),
                                'translations': subregion_data.get('translations', {})
                            }
                        )
                    except Region.DoesNotExist:
                        self.stdout.write(self.style.ERROR(
                            f"Warning: Region {subregion_data['region_id']} not found for subregion {subregion_data['id']}"
                        ))
                        continue

            # Load countries
            self.stdout.write('Loading countries...')
            with open(countries_file, encoding='utf-8') as f:
                countries_data = json.load(f)
                for country_data in countries_data:
                    try:
                        region = Region.objects.get(id=country_data['region_id'])
                        subregion = SubRegion.objects.get(
                            id=country_data['subregion_id'])
                        Country.objects.update_or_create(
                            id=country_data['id'],
                            defaults={
                                'name': country_data['name'],
                                'iso3': country_data['iso3'],
                                'iso2': country_data['iso2'],
                                'numeric_code': country_data['numeric_code'],
                                'phonecode': country_data['phonecode'],
                                'capital': country_data['capital'],
                                'currency': country_data['currency'],
                                'currency_name': country_data['currency_name'],
                                'currency_symbol': country_data['currency_symbol'],
                                'tld': country_data['tld'],
                                'native': country_data.get('native', ''),  # Provide empty string as default
                                'nationality': country_data['nationality'],
                                'timezones': country_data['timezones'],
                                'translations': country_data.get('translations', {}),
                                'region': region,
                                'subregion': subregion
                            }
                        )
                    except Region.DoesNotExist:
                        self.stdout.write(self.style.ERROR(
                            f"Warning: Region {country_data['region_id']} not found for country {country_data['id']}"
                        ))
                        continue
                    except SubRegion.DoesNotExist:
                        self.stdout.write(self.style.ERROR(
                            f"Warning: SubRegion {country_data['subregion_id']} not found for country {country_data['id']}"
                        ))
                        continue

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {str(e)}"))
            raise

        # Load states
        self.stdout.write('Loading states...')
        with open(states_file, encoding='utf-8') as f:
            states_data = json.load(f)
            states_to_create = []
            country_cache = {}
            
            for i, state_data in enumerate(states_data):
                country_id = state_data['country_id']
                if country_id not in country_cache:
                    country_cache[country_id] = Country.objects.get(id=country_id)
                
                country = country_cache[country_id]
                
                # Check if state already exists
                if not State.objects.filter(id=state_data['id']).exists():
                    state = State(
                        id=state_data['id'],
                        name=state_data['name'],
                        country=country,
                        country_code=state_data['country_code'],
                        country_name=state_data['country_name'],
                        state_code=state_data.get('state_code'),
                        type=state_data['type'],
                        latitude=float(state_data['latitude']) if state_data['latitude'] is not None else None,
                        longitude=float(state_data['longitude']) if state_data['longitude'] is not None else None
                    )
                    states_to_create.append(state)
                
                # Bulk create in batches
                if len(states_to_create) >= batch_size or i == len(states_data) - 1:
                    if states_to_create:
                        State.objects.bulk_create(states_to_create)
                        self.stdout.write(f'Created {len(states_to_create)} states')
                        states_to_create = []

        # Load cities (optional)
        if skip_cities:
            self.stdout.write(self.style.WARNING('Skipping cities loading (--skip-cities flag used)'))
        else:
            self.stdout.write('Loading cities (this may take a while)...')
            with open(cities_file, encoding='utf-8') as f:
                cities_data = json.load(f)
                cities_to_create = []
                state_cache = {}
                country_cache = {}
                
                for i, city_data in enumerate(cities_data):
                    state_id = city_data['state_id']
                    country_id = city_data['country_id']
                    
                    # Use cache to avoid repeated database queries
                    if state_id not in state_cache:
                        state_cache[state_id] = State.objects.get(id=state_id)
                    if country_id not in country_cache:
                        country_cache[country_id] = Country.objects.get(id=country_id)
                    
                    state = state_cache[state_id]
                    country = country_cache[country_id]
                    
                    # Check if city already exists
                    if not City.objects.filter(id=city_data['id']).exists():
                        city = City(
                            id=city_data['id'],
                            name=city_data['name'],
                            state=state,
                            state_code=city_data.get('state_code'),
                            state_name=city_data['state_name'],
                            country=country,
                            country_code=city_data['country_code'],
                            country_name=city_data['country_name'],
                            latitude=float(city_data['latitude']),
                            longitude=float(city_data['longitude']),
                            wiki_data_id=city_data.get('wikiDataId')
                        )
                        cities_to_create.append(city)
                    
                    # Bulk create in batches
                    if len(cities_to_create) >= batch_size or i == len(cities_data) - 1:
                        if cities_to_create:
                            City.objects.bulk_create(cities_to_create)
                            self.stdout.write(f'Created {len(cities_to_create)} cities')
                            cities_to_create = []

        self.stdout.write(self.style.SUCCESS('Geographical data loaded successfully'))

