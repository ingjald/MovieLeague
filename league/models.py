from django.db import models


class User(models.Model):
    name = models.CharField(max_length=32)


class Movie(models.Model):
    name = models.CharField(max_length=255)
    release_date = models.DateField()

    def get_value_on_date(self, date):
        filtered = self.moviegrossupdates_set.exclude(date__gt=date)
        if filtered.count() > 0:
            return filtered.latest().gross
        return 0


class MovieGrossUpdates(models.Model):
    movie = models.ForeignKey(Movie)
    date = models.DateField()
    gross = models.BigIntegerField()

    class Meta:
        get_latest_by = 'date'


class MovieMembership(models.Model):
    movie = models.ForeignKey(Movie)
    team = models.ForeignKey('Team')
    price = models.IntegerField()


class League(models.Model):
    commissioner = models.ForeignKey(User, related_name='owned_leagues_set')
    players = models.ManyToManyField(User)


class Season(models.Model):
    league = models.ForeignKey(League)
    start_date = models.DateField()
    end_date = models.DateField()


class Division(models.Model):
    season = models.ForeignKey(Season)


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
            value += movie.moviegrossupdates_set.latest().gross
        return value

    def get_value_for_date(self, date):
        value = 0
        for movie in self.movies.all():
            value += movie.get_value_on_date(date)
        return value