# Geodata: A Django Package for Geographical Data

## Overview

Geodata is a Django package that provides models for regions, subregions, countries, states, and cities, populated with data from the countries-states-cities-database. It simplifies the integration of geographical data into Django projects, suitable for applications requiring location-based functionality.

Credit for the data goes to [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database.git)

## Installation

Install the package using pip:

```bash
pip install geodata
```

## Setup

Add 'geodata' to your INSTALLED_APPS in settings.py:

```python
INSTALLED_APPS = [
    # ...
    'geodata',
    # ...
]
```

Run migrations to create the database tables:

```bash
python manage.py migrate
```

## Loading Data

Populate the database with geographical data using the management command:

```bash
python manage.py load_geodata
```

This command loads regions, subregions, countries, states, and cities from JSON files included in the package.

### Performance Options

For faster loading during development, you can skip loading cities (which is the largest dataset):

```bash
python manage.py load_geodata --skip-cities
```

You can also adjust the batch size for bulk operations:

```bash
python manage.py load_geodata --batch-size 2000
```

## Models

The package provides the following models:

- **Region**: Represents a geographical region (e.g., Africa).
- **SubRegion**: Represents a subregion within a region (e.g., Western Africa).
- **Country**: Represents a country with details like ISO codes, capital, currency, etc.
- **State**: Represents a state or province within a country.
- **City**: Represents a city within a state and country, including latitude and longitude.

Each model includes fields as defined in the data source, with foreign key relationships to maintain the hierarchy. The models also include database indexes on commonly queried fields for improved performance.

### Key Features

- **Translations**: Region, SubRegion, and Country models include support for translations in multiple languages
- **Coordinates**: State and City models include a convenient `coordinates` property to access latitude and longitude as a tuple
- **Timezones**: Country model includes timezone data as a JSONField with a helper method `get_timezones()`
- **Database Indexes**: All models include appropriate indexes for optimized queries

## Usage Examples

### Querying Cities in a State

To retrieve all cities in a specific state:

```python
from geodata.models import State, City

state = State.objects.get(name='California')
cities = City.objects.filter(state=state)
for city in cities:
    print(city.name)
```

### Creating a Form with Country and City Fields

Use the models in a Django form:

```python
from django import forms
from geodata.models import Country, City

class LocationForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    city = forms.ModelChoiceField(queryset=City.objects.all())
```

### Filtering Cities by Country

To get cities in a specific country:

```python
from geodata.models import Country, City

country = Country.objects.get(name='United States')
cities = City.objects.filter(country=country)
```

### Working with Coordinates

```python
from geodata.models import City

city = City.objects.get(name='New York')
lat, lng = city.coordinates  # Returns tuple of (latitude, longitude)
```

### Accessing Translations

```python
from geodata.models import Country

country = Country.objects.get(name='Germany')
german_name = country.translations.get('de')  # Returns 'Deutschland'
```

## Data Source and License

The data is sourced from the [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database.git), licensed under the Open Database License. Users must comply with the license terms and independently verify the data for critical applications.

## Updating Data

The data is updated periodically. To refresh the data:

1. Download the latest JSON files from the repository.
2. Replace the files in the `geodata/data/` directory.
3. Re-run the load_geodata command:

```bash
python manage.py load_geodata
```



**Note**: This will update existing data, so back up your database if necessary.

## Performance Considerations

- The complete dataset is large, especially the cities data. Consider using the `--skip-cities` flag during development.
- Database indexes are provided on foreign keys and commonly queried fields to improve query performance.
- For large-scale applications, consider implementing caching strategies for frequently accessed data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This package is licensed under the MIT License.

## Changelog

### 1.1.1 (2025-07-05)

- Fixed data loading issues with optional fields:
  - Made `native` field in Country model optional
  - Made `latitude` and `longitude` fields in State model optional
  - Added proper handling of None values in coordinates
  - Added error handling for missing regions/subregions
- Improved data loading robustness:
  - Added warnings for missing region/subregion references
  - Better handling of incomplete data
  - More graceful error recovery during data loading

### 1.0.0

- Initial release
