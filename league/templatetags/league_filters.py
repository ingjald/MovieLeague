from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter(name='relegation')
def relegation_css(value):
    if value.is_promoted():
        return "class=\"promoted\""
    elif value.is_relegated():
        return "class=\"relegated\""
    else:
        return ""

@register.filter
def team_cost(value):
    return value.division.currency_unit + " " + intcomma(value.get_team_cost())

@register.filter
def movie_membership_cost(value):
    return value.team.division.currency_unit + " " + intcomma(value.price)