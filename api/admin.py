"""
Admin site configuration.

Registering models with the admin site allows manual data management
through Django's built-in admin interface (Lecture 6, slides 9-10).
I've added list_display, search, and filter options to make the admin
panel practical for reviewing and editing records.
"""

from django.contrib import admin
from .models import Team, Player, Match, PlayerMatchStatistic


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'country', 'founded_year', 'stadium')
    list_filter = ('country',)
    search_fields = ('name', 'short_name')
    ordering = ('name',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'position', 'nationality', 'jersey_number')
    list_filter = ('position', 'team', 'nationality')
    search_fields = ('name', 'nationality')
    ordering = ('team', 'jersey_number')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'home_team', 'home_score', 'away_score', 'away_team',
        'date', 'season', 'status',
    )
    list_filter = ('season', 'status')
    search_fields = ('home_team__name', 'away_team__name', 'venue')
    ordering = ('-date',)


@admin.register(PlayerMatchStatistic)
class PlayerMatchStatisticAdmin(admin.ModelAdmin):
    list_display = (
        'player', 'match', 'goals', 'assists',
        'minutes_played', 'yellow_cards', 'red_cards',
    )
    list_filter = ('match__season',)
    search_fields = ('player__name',)
    ordering = ('-match__date',)
