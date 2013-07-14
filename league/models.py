from django.contrib.auth.models import User
from django.db import models


class Movie(models.Model):
    name = models.CharField(max_length=255)
    release_date = models.DateField()

    def get_value(self):
        if self.moviegrossupdate_set.count() > 0:
            return self.moviegrossupdate_set.latest().gross
        return 0

    def get_value_on_date(self, date):
        filtered = self.moviegrossupdate_set.exclude(date__gt=date)
        if filtered.count() > 0:
            return filtered.latest().gross
        return 0

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['release_date']


class MovieGrossUpdate(models.Model):
    movie = models.ForeignKey(Movie)
    date = models.DateField()
    gross = models.BigIntegerField()

    class Meta:
        get_latest_by = 'date'


class MovieExternalId(models.Model):
    movie = models.ForeignKey(Movie)
    source = models.TextField(max_length=32)
    identifier = models.TextField(max_length=255)


class MovieMembership(models.Model):
    movie = models.ForeignKey(Movie)
    team = models.ForeignKey('Team')
    price = models.IntegerField()


class League(models.Model):
    commissioner = models.ForeignKey(User, related_name='owned_leagues_set')
    players = models.ManyToManyField(User)
    name = models.TextField(max_length=50)

    def __unicode__(self):
        return self.name


class Season(models.Model):
    league = models.ForeignKey(League)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return self.league.name + ", " + str(self.start_date) + " to " + str(self.end_date)


class Division(models.Model):
    season = models.ForeignKey(Season)
    name = models.TextField(max_length=50)

    def sorted_teams(self):
        return sorted(list(Team.objects.all()), key=lambda x: x.get_team_value(), reverse=True)

    def __unicode__(self):
        return self.name


class Team(models.Model):
    owner = models.ForeignKey(User)
    movies = models.ManyToManyField(Movie, through=MovieMembership)
    division = models.ForeignKey(Division)

    def get_team_cost(self):
        cost = 0
        for movie_membership in self.moviemembership_set.all():
            cost += movie_membership.price
        return cost

    def get_team_value(self):
        value = 0
        for movie in self.movies.all():
            if movie.moviegrossupdate_set.count() > 0:
                value += movie.get_value()
        return value

    def get_team_value_for_date(self, date):
        value = 0
        for movie in self.movies.all():
            value += movie.get_value_on_date(date)
        return value

    def __unicode__(self):
        return self.owner.username