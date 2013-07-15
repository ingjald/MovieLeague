from django.contrib.auth.models import User
from django.db import models

import datetime


class Movie(models.Model):
    name = models.CharField(max_length=255)
    release_date = models.DateField()

    def _get_source_filtered_updates(self, source=None):
        if source:
            return self.moviegrossupdate_set.filter(source=source)
        return self.moviegrossupdate_set

    def get_value(self, source=None):
        source_filtered_updates = self._get_source_filtered_updates(source=source)
        if source_filtered_updates.count() > 0:
            return source_filtered_updates.latest().gross
        return 0

    def get_value_on_date(self, date, source=None):
        source_filtered_updates = self._get_source_filtered_updates(source=source)
        date_filtered_updates = source_filtered_updates.exclude(date__gt=date)
        if date_filtered_updates.count() > 0:
            return date_filtered_updates.latest().gross
        return 0

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['release_date']


class MovieExternalId(models.Model):
    movie = models.ForeignKey(Movie)
    source = models.TextField(max_length=32)
    identifier = models.TextField(max_length=255)


class MovieGrossUpdate(models.Model):
    movie = models.ForeignKey(Movie)
    date = models.DateField()
    gross = models.BigIntegerField()
    source = models.TextField(max_length=255)

    class Meta:
        get_latest_by = 'date'


class MovieMembership(models.Model):
    movie = models.ForeignKey(Movie)
    team = models.ForeignKey('Team')
    price = models.IntegerField()

    def value_on_team(self):
        end_date = self.team.division.season.end_date
        return self.movie.get_value_on_date(end_date)

    def efficiency(self):
        return self.value_on_team()/self.price

    class Meta:
        ordering = ['movie']


class League(models.Model):
    commissioner = models.ForeignKey(User, related_name='owned_leagues_set')
    players = models.ManyToManyField(User)
    name = models.TextField(max_length=50)
    short_description = models.TextField(max_length=50)
    long_description = models.TextField(max_length=255)

    def __unicode__(self):
        return self.name


class Season(models.Model):
    league = models.ForeignKey(League)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.TextField(max_length=100)
    movies = models.ManyToManyField(Movie)

    def has_ended(self):
        return datetime.date.today > self.end_date

    def _annotate_values(self, movie_list):
        annotated_movies = []
        for movie in movie_list:
            annotated_movies.append((movie, movie.get_value_on_date(self.end_date)))
        return annotated_movies

    def released_movies(self):
        return self._annotate_values(self.movies.exclude(release_date__gt=datetime.date.today()))

    def unreleased_movies(self):
        return self._annotate_values(self.movies.filter(release_date__gt=datetime.date.today()))

    def __unicode__(self):
        return self.name + ", " + str(self.start_date) + " to " + str(self.end_date)

    class Meta:
        get_latest_by = 'start_date'


class Division(models.Model):
    season = models.ForeignKey(Season)
    name = models.TextField(max_length=50)
    sort_order = models.PositiveSmallIntegerField()
    currency_unit = models.TextField(max_length=10)
    max_currency = models.IntegerField()
    num_relegated = models.SmallIntegerField()
    num_promoted = models.SmallIntegerField()

    def sorted_teams(self):
        return sorted(sorted(list(Team.objects.filter(division=self)), key=lambda x: x.get_team_cost()),
                      key=lambda x: x.get_team_value(), reverse=True)

    def get_leader(self):
        top_teams = self.sorted_teams()
        if len(top_teams) > 0:
            return top_teams[0]
        else:
            return None

    def is_relegation_enabled(self):
        return self.num_relegated > 0

    def is_promotion_enabled(self):
        return self.num_promoted > 0

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sort_order']


class Team(models.Model):
    owner = models.ForeignKey(User)
    movies = models.ManyToManyField(Movie, through=MovieMembership)
    division = models.ForeignKey(Division)
    name = models.TextField(max_length=50, blank=True, null=True)

    def get_team_cost(self):
        cost = 0
        for movie_membership in self.moviemembership_set.all():
            cost += movie_membership.price
        return cost

    def get_team_value(self):
        value = 0
        for movie in self.movies.all():
            if movie.moviegrossupdate_set.count() > 0:
                value += movie.get_value_on_date(self.division.season.end_date)
        return value

    def get_team_value_for_date(self, date):
        value = 0
        for movie in self.movies.all():
            value += movie.get_value_on_date(date)
        return value

    def get_name(self):
        if self.name and len(self.name) > 0:
            return self.name
        else:
            return self.owner.username

    def get_position(self, reverse=False):
        sorted_division = self.division.sorted_teams()
        if reverse:
            sorted_division.reverse()
        position = sorted_division.index(self)
        return position

    def is_promoted(self):
        return self.get_position() < self.division.num_promoted

    def is_relegated(self):
        return self.get_position(reverse=True) < self.division.num_relegated

    def __unicode__(self):
        return self.get_name()