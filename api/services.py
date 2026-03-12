"""
Service-layer helpers for analytical endpoints.

This module implements the business logic for all five analytics endpoints,
keeping views thin and logic testable in isolation. Each public function
accepts validated keyword arguments and returns a plain Python dict that
the calling view serialises to JSON.

Functions:
    build_leaderboard_payload  -- ranked goals/assists leaderboard
    build_team_performance_payload -- league standings with points
    build_head_to_head_payload -- historical record between two teams
    build_season_summary_payload -- season-wide aggregated statistics
    build_player_profile_payload -- career totals and per-season breakdown
"""

from django.db.models import Avg, Count, F, Q, Sum
from rest_framework.exceptions import NotFound, ValidationError

from .models import Match, Player, PlayerMatchStatistic, Team
from .validators import (
    parse_limited_positive_int,
    parse_positive_int,
    validate_season_code,
)


LEADERBOARD_METRICS = {'goals', 'assists'}


def build_leaderboard_payload(*, metric='goals', season=None, limit=None):
    """
    Return the leaderboard response body.
    """
    if metric not in LEADERBOARD_METRICS:
        raise ValidationError({
            'metric': 'Must be one of: assists, goals.',
        })

    season = validate_season_code(season, field_name='season')
    limit = parse_limited_positive_int(
        limit, field_name='limit', default=10, maximum=50
    )

    stat_filter = {}
    if season:
        stat_filter['match__season'] = season

    leaderboard = (
        PlayerMatchStatistic.objects
        .filter(**stat_filter)
        .values(
            'player__id',
            'player__name',
            'player__team__name',
            'player__team__short_name',
            'player__position',
        )
        .annotate(
            total=Sum(metric),
            matches_played=Count('id'),
        )
        .order_by('-total', 'player__name')[:limit]
    )

    return {
        'metric': metric,
        'season': season or 'all',
        'results': [
            {
                'rank': index + 1,
                'player_id': entry['player__id'],
                'player_name': entry['player__name'],
                'team': entry['player__team__name'],
                'team_short': entry['player__team__short_name'],
                'position': entry['player__position'],
                'total': entry['total'] or 0,
                'matches_played': entry['matches_played'],
            }
            for index, entry in enumerate(leaderboard)
        ],
    }


def build_team_performance_payload(*, season=None, team_id=None):
    """
    Return standings and form data for one or more teams.
    """
    season = validate_season_code(season, field_name='season')
    team_id = parse_positive_int(team_id, field_name='team')

    teams = Team.objects.all()
    if team_id is not None:
        teams = teams.filter(id=team_id)
        if not teams.exists():
            raise NotFound('Team not found.')

    match_qs = Match.objects.filter(status='COMPLETED')
    if season:
        match_qs = match_qs.filter(season=season)

    results = []
    for team in teams:
        home_matches = match_qs.filter(home_team=team)
        away_matches = match_qs.filter(away_team=team)

        home_wins = home_matches.filter(home_score__gt=F('away_score')).count()
        home_draws = home_matches.filter(home_score=F('away_score')).count()
        home_losses = home_matches.filter(home_score__lt=F('away_score')).count()

        away_wins = away_matches.filter(away_score__gt=F('home_score')).count()
        away_draws = away_matches.filter(away_score=F('home_score')).count()
        away_losses = away_matches.filter(away_score__lt=F('home_score')).count()

        goals_scored_home = home_matches.aggregate(s=Sum('home_score'))['s'] or 0
        goals_scored_away = away_matches.aggregate(s=Sum('away_score'))['s'] or 0
        goals_conceded_home = (
            home_matches.aggregate(s=Sum('away_score'))['s'] or 0
        )
        goals_conceded_away = (
            away_matches.aggregate(s=Sum('home_score'))['s'] or 0
        )

        total_wins = home_wins + away_wins
        total_draws = home_draws + away_draws
        total_losses = home_losses + away_losses
        total_played = total_wins + total_draws + total_losses
        points = (total_wins * 3) + total_draws

        results.append({
            'team_id': team.id,
            'team_name': team.name,
            'short_name': team.short_name,
            'played': total_played,
            'wins': total_wins,
            'draws': total_draws,
            'losses': total_losses,
            'goals_scored': goals_scored_home + goals_scored_away,
            'goals_conceded': goals_conceded_home + goals_conceded_away,
            'goal_difference': (
                (goals_scored_home + goals_scored_away)
                - (goals_conceded_home + goals_conceded_away)
            ),
            'points': points,
        })

    results.sort(key=lambda item: (-item['points'], -item['goal_difference']))

    return {
        'season': season or 'all',
        'standings': results,
    }


def build_head_to_head_payload(*, team1_id=None, team2_id=None, season=None):
    """
    Return the historical record between two teams.
    """
    season = validate_season_code(season, field_name='season')
    team1_id = parse_positive_int(team1_id, field_name='team1', required=True)
    team2_id = parse_positive_int(team2_id, field_name='team2', required=True)

    if team1_id == team2_id:
        raise ValidationError({
            'team2': 'team1 and team2 must reference different teams.',
        })

    try:
        team1 = Team.objects.get(id=team1_id)
        team2 = Team.objects.get(id=team2_id)
    except Team.DoesNotExist as exc:
        raise NotFound('One or both teams not found.') from exc

    matches = (
        Match.objects.filter(status='COMPLETED')
        .filter(
            (Q(home_team=team1) & Q(away_team=team2))
            | (Q(home_team=team2) & Q(away_team=team1))
        )
        .order_by('-date')
    )
    if season:
        matches = matches.filter(season=season)

    team1_wins = 0
    team2_wins = 0
    draws = 0
    team1_goals = 0
    team2_goals = 0
    match_history = []

    for match in matches:
        if match.home_team_id == team1.id:
            team1_score, team2_score = match.home_score, match.away_score
        else:
            team1_score, team2_score = match.away_score, match.home_score

        team1_goals += team1_score
        team2_goals += team2_score

        if team1_score > team2_score:
            team1_wins += 1
        elif team2_score > team1_score:
            team2_wins += 1
        else:
            draws += 1

        match_history.append({
            'match_id': match.id,
            'date': match.date.strftime('%Y-%m-%d'),
            'venue': match.venue,
            'score': (
                f'{match.home_team.short_name} {match.home_score} - '
                f'{match.away_score} {match.away_team.short_name}'
            ),
        })

    return {
        'team1': {'id': team1.id, 'name': team1.name},
        'team2': {'id': team2.id, 'name': team2.name},
        'total_matches': len(match_history),
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'draws': draws,
        'team1_total_goals': team1_goals,
        'team2_total_goals': team2_goals,
        'matches': match_history,
    }


def build_season_summary_payload(*, season=None):
    """
    Return season-level aggregates.
    """
    season = validate_season_code(season, field_name='season', required=True)

    completed = Match.objects.filter(season=season, status='COMPLETED')
    total_matches = completed.count()

    if total_matches == 0:
        return {
            'season': season,
            'total_matches': 0,
            'message': 'No completed matches found for this season.',
        }

    agg = completed.aggregate(
        total_home_goals=Sum('home_score'),
        total_away_goals=Sum('away_score'),
    )
    total_goals = (agg['total_home_goals'] or 0) + (agg['total_away_goals'] or 0)
    avg_goals = round(total_goals / total_matches, 2)

    top_scorer = (
        PlayerMatchStatistic.objects
        .filter(match__season=season)
        .values('player__id', 'player__name', 'player__team__short_name')
        .annotate(total_goals=Sum('goals'))
        .order_by('-total_goals', 'player__name')
        .first()
    )

    top_assister = (
        PlayerMatchStatistic.objects
        .filter(match__season=season)
        .values('player__id', 'player__name', 'player__team__short_name')
        .annotate(total_assists=Sum('assists'))
        .order_by('-total_assists', 'player__name')
        .first()
    )

    return {
        'season': season,
        'total_matches': total_matches,
        'total_goals': total_goals,
        'average_goals_per_match': avg_goals,
        'top_scorer': {
            'player_id': top_scorer['player__id'],
            'name': top_scorer['player__name'],
            'team': top_scorer['player__team__short_name'],
            'goals': top_scorer['total_goals'],
        } if top_scorer else None,
        'top_assister': {
            'player_id': top_assister['player__id'],
            'name': top_assister['player__name'],
            'team': top_assister['player__team__short_name'],
            'assists': top_assister['total_assists'],
        } if top_assister else None,
    }


def build_player_profile_payload(*, player_id):
    """
    Return a single player's career totals and season splits.
    """
    try:
        player = Player.objects.select_related('team').get(id=player_id)
    except Player.DoesNotExist as exc:
        raise NotFound('Player not found.') from exc

    stats = player.match_stats.all()
    totals = stats.aggregate(
        total_goals=Sum('goals'),
        total_assists=Sum('assists'),
        total_yellow=Sum('yellow_cards'),
        total_red=Sum('red_cards'),
        total_minutes=Sum('minutes_played'),
        appearances=Count('id'),
        avg_minutes=Avg('minutes_played'),
    )

    seasons = (
        stats
        .values('match__season')
        .annotate(
            goals=Sum('goals'),
            assists=Sum('assists'),
            appearances=Count('id'),
        )
        .order_by('match__season')
    )

    return {
        'player': {
            'id': player.id,
            'name': player.name,
            'team': player.team.name,
            'position': player.get_position_display(),
            'nationality': player.nationality,
            'jersey_number': player.jersey_number,
        },
        'career_totals': {
            'appearances': totals['appearances'] or 0,
            'goals': totals['total_goals'] or 0,
            'assists': totals['total_assists'] or 0,
            'yellow_cards': totals['total_yellow'] or 0,
            'red_cards': totals['total_red'] or 0,
            'total_minutes': totals['total_minutes'] or 0,
            'avg_minutes_per_match': round(totals['avg_minutes'] or 0, 1),
        },
        'by_season': [
            {
                'season': season_row['match__season'],
                'appearances': season_row['appearances'],
                'goals': season_row['goals'],
                'assists': season_row['assists'],
            }
            for season_row in seasons
        ],
    }
