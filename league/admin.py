from league.models import League, Season, Division, Team, Movie
from django.contrib import admin


class LeagueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'commissioner', 'short_description', 'long_description']})
    ]


class SeasonAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['league', 'name', 'movies']}),
        ('Dates', {'fields': ['start_date', 'end_date']})
    ]


class DivisionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['season', 'name', 'sort_order', 'currency_unit', 'max_currency']})
    ]


class MovieMembershipAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'team', 'movie'})
    ]


class MovieMembershipInline(admin.TabularInline):
    model = Team.movies.through


class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['division', 'owner']})
    ]
    inlines = [MovieMembershipInline]


class MovieAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'release_date']})
    ]


admin.site.register(League, LeagueAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Movie, MovieAdmin)