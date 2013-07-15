# Create your views here.
from django.shortcuts import render
from league.models import League, Team, Season


def home(request):
    return render(request, 'home.html', {'leagues': League.objects.all()})


def league(request, league_id):
    requested_league = League.objects.get(id=league_id)
    return render(request, 'league.html', {'league': requested_league})


def team(request, team_id):
    requested_team = Team.objects.get(id=team_id)
    return render(request, 'team.html', {'team': requested_team, 'division': requested_team.division,
                                         'season': requested_team.division.season,
                                         'league': requested_team.division.season.league})


def seasons(request, league_id):
    requested_league = League.objects.get(id=league_id)
    return render(request, 'seasons.html', {'league': requested_league})


def season(request, season_id):
    requested_season = Season.objects.get(id=season_id)
    return render(request, 'season.html', {'season': requested_season, 'league': requested_season.league})