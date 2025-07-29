from django.db import models
import json


class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    wiki_data_id = models.CharField(max_length=255, blank=True, null=True)
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return self.name


class SubRegion(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name='subregions')
    wiki_data_id = models.CharField(max_length=255, blank=True, null=True)
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "SubRegion"
        verbose_name_plural = "SubRegions"
        indexes = [
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return self.name


class Country(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=3)
    iso2 = models.CharField(max_length=2)
    numeric_code = models.CharField(max_length=3)
    phonecode = models.CharField(max_length=10)
    capital = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    currency_name = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=255)
    tld = models.CharField(max_length=255)
    native = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name='countries')
    subregion = models.ForeignKey(
        SubRegion, on_delete=models.CASCADE, related_name='countries')
    nationality = models.CharField(max_length=255)
    timezones = models.JSONField(default=list)
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['subregion']),
            models.Index(fields=['iso2']),
            models.Index(fields=['iso3']),
        ]

    def __str__(self):
        return self.name
        
    def get_timezones(self):
        """Return timezones as a Python object"""
        if isinstance(self.timezones, str):
            return json.loads(self.timezones)
        return self.timezones


class State(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='states')
    country_code = models.CharField(max_length=2)
    # country_name field is redundant since we have the country relation
    # but keeping for backwards compatibility
    country_name = models.CharField(max_length=255)
    state_code = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['country_code']),
            models.Index(fields=['state_code']),
        ]

    def __str__(self):
        return self.name
        
    @property
    def coordinates(self):
        """Return coordinates as a tuple"""
        return (self.latitude, self.longitude)


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='cities')
    state_code = models.CharField(max_length=255, blank=True, null=True)
    # state_name field is redundant since we have the state relation
    # but keeping for backwards compatibility
    state_name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='cities')
    country_code = models.CharField(max_length=2)
    # country_name field is redundant since we have the country relation
    # but keeping for backwards compatibility
    country_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    wiki_data_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['country']),
            models.Index(fields=['country_code']),
            models.Index(fields=['state_code']),
        ]

    def __str__(self):
        return self.name
        
    @property
    def coordinates(self):
        """Return coordinates as a tuple"""
        return (self.latitude, self.longitude)
