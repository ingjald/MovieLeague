from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MovieLeague.views.home', name='home'),
    # url(r'^MovieLeague/', include('MovieLeague.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('social_auth.urls')),

    (r'^$', 'league.views.home'),
    url(r'^league/(?P<league_id>\d*)/seasons', 'league.views.seasons', name="seasons"),
    url(r'^season/(?P<season_id>\d*)', 'league.views.season', name="season"),
    url(r'^league/(?P<league_id>\d*)', 'league.views.league', name="league"),
    url(r'^team/(?P<team_id>\d*)', 'league.views.team', name="team"),
    url(r'^logout/(?P<next_page>.*)/$', logout, name="auth_logout"),
)
