# Create your views here.
from django.shortcuts import render
from league.models import League, Team, Division


def home(request):
    return render(request, 'home.html', {'leagues': League.objects.all()})


def league(request, league_id):
    requested_league = League.objects.get(id=league_id)
    return render(request, 'league.html', {'league': requested_league})


def team(request, team_id):
    requested_team = Team.objects.get(id=team_id)
    return render(request, 'team.html', {'team': requested_team, 'division': Division.objects.get(team=team_id)})