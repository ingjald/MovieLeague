"""
Unit tests for data model
"""

from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase

import models


class ModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@example.com', password='password')
        self.user.save()
        self.movie = models.Movie(name="Test Movie", release_date=date(2013, 7, 1))
        self.movie.save()

    def test_user(self):
        """
        Sanity check to make sure user was created and committed to the database properly
        """
        user_from_db = models.User.objects.all()[0]
        self.assertEqual(user_from_db.username, "test")
        self.assertEqual(self.user, user_from_db)

    def test_movie_no_gross(self):
        """
        Tests a movie's gross without any updates having been added.
        """
        self.assertEqual(self.movie.get_value_on_date(date(2013, 6, 30)), 0)
        self.assertEqual(self.movie.get_value_on_date(date(2013, 7, 1)), 0)
        self.assertEqual(self.movie.get_value_on_date(date(2013, 7, 2)), 0)
        self.assertEqual(self.movie.get_value(), 0)

    def test_movie_gross_updates(self):
        """
        Tests the addition of updates to a movie's gross and ensures that they're ordered properly.
        """
        movie = models.Movie(name="Gross Updates Test Movie", release_date=date(2013, 7, 1))
        movie.save()
        self.assertEqual(self.movie.get_value_on_date(date(2013, 7, 2)), 0)
        gross_update = models.MovieGrossUpdate(movie=movie, date=date(2013, 7, 2), gross=1000, source="source1")
        gross_update.save()
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 2)), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 1)), 0)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 3)), 1000)
        gross_update_2 = models.MovieGrossUpdate(movie=movie, date=date(2013, 7, 5), gross=8000, source="source1")
        gross_update_2.save()
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 2)), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 1)), 0)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 4)), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 5)), 8000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 6)), 8000)
        gross_update_3 = models.MovieGrossUpdate(movie=movie, date=date(2013, 7, 3), gross=4000, source="source1")
        gross_update_3.save()
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 2)), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 1)), 0)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 3)), 4000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 4)), 4000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 5)), 8000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 6)), 8000)

    def test_movie_gross_updates_by_source(self):
        """
        Tests the addition of updates to a movie's gross and ensures that they're ordered properly.
        """
        movie = models.Movie(name="Gross Updates Test Movie", release_date=date(2013, 7, 1))
        movie.save()
        self.assertEqual(self.movie.get_value_on_date(date(2013, 7, 2)), 0)
        gross_update = models.MovieGrossUpdate(movie=movie, date=date(2013, 7, 2), gross=1000, source="source1")
        gross_update.save()
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 2), source="source1"), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 1), source="source1"), 0)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 3), source="source1"), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 3), source="source2"), 0)
        gross_update_2 = models.MovieGrossUpdate(movie=movie, date=date(2013, 7, 5), gross=8000, source="source2")
        gross_update_2.save()
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 4), source="source1"), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 5), source="source1"), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 6), source="source1"), 1000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 4), source="source2"), 0)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 5), source="source2"), 8000)
        self.assertEqual(movie.get_value_on_date(date(2013, 7, 6), source="source2"), 8000)

    def test_team(self):
        """
        Tests a team's cost and value
        """
        league = models.League(commissioner=self.user)
        league.save()
        season = models.Season(league=league, start_date=date(2013, 1, 1), end_date=date(2014, 1, 1))
        season.save()
        division = models.Division(season=season)
        division.save()
        team = models.Team(owner=self.user, division=division)
        team.save()
        movie1 = models.Movie(name="Team Test Movie 1", release_date=date(2013, 7, 1))
        movie1.save()
        mm = models.MovieMembership(movie=movie1, team=team, price=15)
        mm.save()
        self.assertEqual(team.get_team_cost(), 15)
        self.assertEqual(team.get_team_value(), 0)

        gross_update = models.MovieGrossUpdate(movie=movie1, date=date(2013, 7, 3), gross=2500)
        gross_update.save()
        self.assertEqual(team.get_team_value(), 2500)

        movie2 = models.Movie(name="Team Test Movie 2", release_date=date(2013, 7, 3))
        movie2.save()
        mm2 = models.MovieMembership(movie=movie2, team=team, price=31)
        mm2.save()
        self.assertEqual(team.get_team_cost(), 46)
        self.assertEqual(team.get_team_value(), 2500)

        gross_update_2 = models.MovieGrossUpdate(movie=movie2, date=date(2013, 7, 7), gross=4000)
        gross_update_2.save()
        self.assertEqual(team.get_team_value(), 6500)
        self.assertEqual(team.get_team_value_for_date(date(2013, 7, 4)), 2500)

        gross_update_3 = models.MovieGrossUpdate(movie=movie1, date=date(2013, 7, 6), gross=4500)
        gross_update_3.save()
        self.assertEqual(team.get_team_value(), 8500)
        self.assertEqual(team.get_team_value_for_date(date(2013, 7, 6)), 4500)

        gross_update_4 = models.MovieGrossUpdate(movie=movie2, date=date(2013, 7, 6), gross=3000)
        gross_update_4.save()
        self.assertEqual(team.get_team_value(), 8500, "Team value not changed by adding an update prior to the latest")