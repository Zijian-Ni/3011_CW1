"""
Test suite for the SportsPulse API.

Covers:
  - Model creation and constraints
  - Authentication (register, login, token usage)
  - Full CRUD on all four resources (Team, Player, Match, Statistic)
  - Query parameter filtering
  - Analytics endpoints
  - Error handling and validation
  - Status codes conforming to HTTP conventions (Lecture 2)

Run with: python manage.py test api
"""

from datetime import datetime, timezone
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Team, Player, Match, PlayerMatchStatistic


class BaseTestCase(TestCase):
    """
    Shared setup for all test classes.
    Creates two teams, players, a match, and statistics so that
    tests have realistic data to work with.
    """

    def setUp(self):
        # Create a test user and token for authenticated requests
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

        # Two teams
        self.team1 = Team.objects.create(
            name='Arsenal', short_name='ARS',
            country='England', founded_year=1886,
            stadium='Emirates Stadium',
        )
        self.team2 = Team.objects.create(
            name='Chelsea', short_name='CHE',
            country='England', founded_year=1905,
            stadium='Stamford Bridge',
        )

        # Players
        self.player1 = Player.objects.create(
            name='Bukayo Saka', team=self.team1,
            position='FW', nationality='England',
            jersey_number=7,
        )
        self.player2 = Player.objects.create(
            name='Cole Palmer', team=self.team2,
            position='MF', nationality='England',
            jersey_number=20,
        )

        # A completed match
        self.match = Match.objects.create(
            home_team=self.team1, away_team=self.team2,
            date=datetime(2025, 1, 15, 15, 0, tzinfo=timezone.utc),
            venue='Emirates Stadium', season='2024/2025',
            home_score=2, away_score=1, status='COMPLETED',
        )

        # Statistics for the match
        self.stat1 = PlayerMatchStatistic.objects.create(
            player=self.player1, match=self.match,
            goals=2, assists=0, minutes_played=90,
            yellow_cards=1, red_cards=0,
            shots_on_target=3, passes_completed=40, tackles=2, saves=0,
        )
        self.stat2 = PlayerMatchStatistic.objects.create(
            player=self.player2, match=self.match,
            goals=1, assists=1, minutes_played=85,
            yellow_cards=0, red_cards=0,
            shots_on_target=2, passes_completed=55, tackles=3, saves=0,
        )

    def auth_client(self):
        """Return a client with the test user's token set."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        return self.client


# ═══════════════════════════════════════════════════════════
#  Model Tests
# ═══════════════════════════════════════════════════════════

class TeamModelTest(BaseTestCase):
    """Tests for the Team model."""

    def test_team_str(self):
        self.assertEqual(str(self.team1), 'Arsenal (ARS)')

    def test_team_unique_name(self):
        """Duplicate team name should raise an integrity error."""
        with self.assertRaises(Exception):
            Team.objects.create(name='Arsenal', short_name='AR2')

    def test_team_unique_short_name(self):
        with self.assertRaises(Exception):
            Team.objects.create(name='New Team', short_name='ARS')


class PlayerModelTest(BaseTestCase):
    """Tests for the Player model."""

    def test_player_str(self):
        self.assertIn('Bukayo Saka', str(self.player1))

    def test_unique_jersey_per_team(self):
        """Two players on the same team cannot share a jersey number."""
        with self.assertRaises(Exception):
            Player.objects.create(
                name='Duplicate Jersey', team=self.team1,
                position='MF', jersey_number=7,
            )


class MatchModelTest(BaseTestCase):
    """Tests for the Match model."""

    def test_match_str(self):
        s = str(self.match)
        self.assertIn('ARS', s)
        self.assertIn('CHE', s)

    def test_result_summary_home_win(self):
        self.assertEqual(self.match.result_summary, 'HOME_WIN')

    def test_result_summary_draw(self):
        self.match.home_score = 1
        self.match.away_score = 1
        self.assertEqual(self.match.result_summary, 'DRAW')

    def test_result_summary_pending(self):
        self.match.status = 'SCHEDULED'
        self.assertEqual(self.match.result_summary, 'PENDING')


# ═══════════════════════════════════════════════════════════
#  Authentication Tests
# ═══════════════════════════════════════════════════════════

class AuthTest(BaseTestCase):
    """Tests for registration and login endpoints."""

    def test_register_success(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass1',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'newuser')

    def test_register_short_password(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'shortpw',
            'password': 'short',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'testuser',  # already exists
            'password': 'anotherpass1',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'nobody',
            'password': 'whatever',
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ═══════════════════════════════════════════════════════════
#  Team CRUD Tests
# ═══════════════════════════════════════════════════════════

class TeamCRUDTest(BaseTestCase):
    """Tests for Team CRUD operations and status codes."""

    def test_list_teams_unauthenticated(self):
        """GET list should work without auth (read-only public access)."""
        resp = self.client.get('/api/teams/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_retrieve_team(self):
        resp = self.client.get(f'/api/teams/{self.team1.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Arsenal')
        self.assertIn('player_count', resp.data)

    def test_create_team_unauthenticated_fails(self):
        """POST without token should return 401."""
        resp = self.client.post('/api/teams/', {'name': 'Spurs', 'short_name': 'TOT'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_team_authenticated(self):
        client = self.auth_client()
        resp = client.post('/api/teams/', {
            'name': 'Tottenham Hotspur',
            'short_name': 'TOT',
            'country': 'England',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], 'Tottenham Hotspur')

    def test_update_team(self):
        client = self.auth_client()
        resp = client.patch(f'/api/teams/{self.team1.id}/', {
            'stadium': 'New Emirates',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['stadium'], 'New Emirates')

    def test_delete_team(self):
        client = self.auth_client()
        resp = client.delete(f'/api/teams/{self.team2.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(id=self.team2.id).exists())

    def test_filter_teams_by_country(self):
        Team.objects.create(name='Barcelona', short_name='BAR', country='Spain')
        resp = self.client.get('/api/teams/?country=Spain')
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['name'], 'Barcelona')

    def test_search_teams(self):
        resp = self.client.get('/api/teams/?search=ars')
        self.assertEqual(resp.data['count'], 1)

    def test_retrieve_nonexistent_team(self):
        resp = self.client.get('/api/teams/9999/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_players_action(self):
        resp = self.client.get(f'/api/teams/{self.team1.id}/players/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], 'Bukayo Saka')


# ═══════════════════════════════════════════════════════════
#  Player CRUD Tests
# ═══════════════════════════════════════════════════════════

class PlayerCRUDTest(BaseTestCase):
    """Tests for Player CRUD operations."""

    def test_list_players(self):
        resp = self.client.get('/api/players/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_create_player(self):
        client = self.auth_client()
        resp = client.post('/api/players/', {
            'name': 'Martin Odegaard',
            'team': self.team1.id,
            'position': 'MF',
            'nationality': 'Norway',
            'jersey_number': 8,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_filter_players_by_team(self):
        resp = self.client.get(f'/api/players/?team={self.team1.id}')
        self.assertEqual(resp.data['count'], 1)

    def test_filter_players_by_position(self):
        resp = self.client.get('/api/players/?position=FW')
        self.assertEqual(resp.data['count'], 1)

    def test_filter_players_invalid_team_param(self):
        resp = self.client.get('/api/players/?team=abc')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_players_invalid_position_param(self):
        resp = self.client.get('/api/players/?position=CB')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_player(self):
        client = self.auth_client()
        resp = client.patch(f'/api/players/{self.player1.id}/', {
            'jersey_number': 10,
            'team': self.team1.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_player(self):
        client = self.auth_client()
        resp = client.delete(f'/api/players/{self.player2.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════
#  Match CRUD Tests
# ═══════════════════════════════════════════════════════════

class MatchCRUDTest(BaseTestCase):
    """Tests for Match CRUD operations."""

    def test_list_matches(self):
        resp = self.client.get('/api/matches/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_create_match(self):
        client = self.auth_client()
        resp = client.post('/api/matches/', {
            'home_team': self.team2.id,
            'away_team': self.team1.id,
            'date': '2025-03-20T18:00:00Z',
            'season': '2024/2025',
            'venue': 'Stamford Bridge',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_match_same_team_fails(self):
        """A team cannot play against itself — validation check."""
        client = self.auth_client()
        resp = client.post('/api/matches/', {
            'home_team': self.team1.id,
            'away_team': self.team1.id,
            'date': '2025-04-01T15:00:00Z',
            'season': '2024/2025',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_match_invalid_season_format(self):
        client = self.auth_client()
        resp = client.post('/api/matches/', {
            'home_team': self.team2.id,
            'away_team': self.team1.id,
            'date': '2025-04-01T15:00:00Z',
            'season': '2024-2025',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_matches_by_season(self):
        resp = self.client.get('/api/matches/?season=2024/2025')
        self.assertEqual(resp.data['count'], 1)

    def test_filter_matches_by_team(self):
        resp = self.client.get(f'/api/matches/?team={self.team1.id}')
        self.assertEqual(resp.data['count'], 1)

    def test_filter_matches_invalid_team_param(self):
        resp = self.client.get('/api/matches/?team=home')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_matches_invalid_status_param(self):
        resp = self.client.get('/api/matches/?status=FINISHED')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_match_score(self):
        client = self.auth_client()
        resp = client.patch(f'/api/matches/{self.match.id}/', {
            'home_score': 3,
            'home_team': self.team1.id,
            'away_team': self.team2.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['home_score'], 3)

    def test_delete_match(self):
        client = self.auth_client()
        resp = client.delete(f'/api/matches/{self.match.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════
#  PlayerMatchStatistic CRUD Tests
# ═══════════════════════════════════════════════════════════

class StatisticCRUDTest(BaseTestCase):
    """Tests for PlayerMatchStatistic CRUD."""

    def test_list_statistics(self):
        resp = self.client.get('/api/statistics/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_create_statistic(self):
        # Create a new player and match first
        new_player = Player.objects.create(
            name='Declan Rice', team=self.team1,
            position='MF', jersey_number=41,
        )
        client = self.auth_client()
        resp = client.post('/api/statistics/', {
            'player': new_player.id,
            'match': self.match.id,
            'goals': 0,
            'assists': 1,
            'minutes_played': 90,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_filter_statistics_by_player(self):
        resp = self.client.get(f'/api/statistics/?player={self.player1.id}')
        self.assertEqual(resp.data['count'], 1)

    def test_filter_statistics_invalid_player_param(self):
        resp = self.client.get('/api/statistics/?player=nope')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_statistics_by_match(self):
        resp = self.client.get(f'/api/statistics/?match={self.match.id}')
        self.assertEqual(resp.data['count'], 2)

    def test_update_statistic(self):
        client = self.auth_client()
        resp = client.patch(f'/api/statistics/{self.stat1.id}/', {
            'goals': 3,
            'player': self.player1.id,
            'match': self.match.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['goals'], 3)

    def test_delete_statistic(self):
        client = self.auth_client()
        resp = client.delete(f'/api/statistics/{self.stat2.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════
#  Analytics Tests
# ═══════════════════════════════════════════════════════════

class LeaderboardTest(BaseTestCase):
    """Tests for the leaderboard analytics endpoint."""

    def test_leaderboard_goals(self):
        resp = self.client.get('/api/analytics/leaderboard/?metric=goals')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['metric'], 'goals')
        results = resp.data['results']
        self.assertEqual(len(results), 2)
        # Saka scored 2, Palmer scored 1 — Saka should be first
        self.assertEqual(results[0]['player_name'], 'Bukayo Saka')
        self.assertEqual(results[0]['total'], 2)

    def test_leaderboard_assists(self):
        resp = self.client.get('/api/analytics/leaderboard/?metric=assists')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data['results']
        # Palmer has 1 assist, Saka has 0
        self.assertEqual(results[0]['player_name'], 'Cole Palmer')

    def test_leaderboard_invalid_metric(self):
        resp = self.client.get('/api/analytics/leaderboard/?metric=fouls')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leaderboard_invalid_season_format(self):
        resp = self.client.get('/api/analytics/leaderboard/?season=2024-2025')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leaderboard_invalid_limit(self):
        resp = self.client.get('/api/analytics/leaderboard/?limit=zero')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leaderboard_season_filter(self):
        resp = self.client.get(
            '/api/analytics/leaderboard/?season=2024/2025'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data['results']) > 0)

    def test_leaderboard_limit(self):
        resp = self.client.get('/api/analytics/leaderboard/?limit=1')
        self.assertEqual(len(resp.data['results']), 1)


class TeamPerformanceTest(BaseTestCase):
    """Tests for the team performance / standings endpoint."""

    def test_team_performance_all(self):
        resp = self.client.get('/api/analytics/team-performance/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        standings = resp.data['standings']
        self.assertEqual(len(standings), 2)
        # Arsenal won, so should be first
        self.assertEqual(standings[0]['team_name'], 'Arsenal')
        self.assertEqual(standings[0]['wins'], 1)
        self.assertEqual(standings[0]['points'], 3)

    def test_team_performance_single_team(self):
        resp = self.client.get(
            f'/api/analytics/team-performance/?team={self.team2.id}'
        )
        standings = resp.data['standings']
        self.assertEqual(len(standings), 1)
        self.assertEqual(standings[0]['losses'], 1)

    def test_team_performance_season_filter(self):
        resp = self.client.get(
            '/api/analytics/team-performance/?season=2024/2025'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_team_performance_invalid_team(self):
        resp = self.client.get('/api/analytics/team-performance/?team=9999')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_performance_invalid_season_format(self):
        resp = self.client.get(
            '/api/analytics/team-performance/?season=2024-2025'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class HeadToHeadTest(BaseTestCase):
    """Tests for the head-to-head endpoint."""

    def test_head_to_head(self):
        resp = self.client.get(
            f'/api/analytics/head-to-head/?team1={self.team1.id}&team2={self.team2.id}'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_matches'], 1)
        self.assertEqual(resp.data['team1_wins'], 1)
        self.assertEqual(resp.data['team2_wins'], 0)

    def test_head_to_head_missing_params(self):
        resp = self.client.get('/api/analytics/head-to-head/?team1=1')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_head_to_head_invalid_team(self):
        resp = self.client.get(
            '/api/analytics/head-to-head/?team1=9999&team2=8888'
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_head_to_head_non_numeric_team(self):
        resp = self.client.get(
            f'/api/analytics/head-to-head/?team1=abc&team2={self.team2.id}'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_head_to_head_same_team(self):
        resp = self.client.get(
            f'/api/analytics/head-to-head/?team1={self.team1.id}&team2={self.team1.id}'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class SeasonSummaryTest(BaseTestCase):
    """Tests for the season summary endpoint."""

    def test_season_summary(self):
        resp = self.client.get(
            '/api/analytics/season-summary/?season=2024/2025'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_matches'], 1)
        self.assertEqual(resp.data['total_goals'], 3)  # 2 + 1

    def test_season_summary_missing_param(self):
        resp = self.client.get('/api/analytics/season-summary/')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_season_summary_no_matches(self):
        resp = self.client.get(
            '/api/analytics/season-summary/?season=1999/2000'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_matches'], 0)

    def test_season_summary_invalid_season_format(self):
        resp = self.client.get(
            '/api/analytics/season-summary/?season=2024-2025'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class PlayerProfileTest(BaseTestCase):
    """Tests for the player profile analytics endpoint."""

    def test_player_profile(self):
        resp = self.client.get(
            f'/api/analytics/player-profile/{self.player1.id}/'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        totals = resp.data['career_totals']
        self.assertEqual(totals['goals'], 2)
        self.assertEqual(totals['appearances'], 1)

    def test_player_profile_not_found(self):
        resp = self.client.get('/api/analytics/player-profile/9999/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ═══════════════════════════════════════════════════════════
#  Status Code Tests
# ═══════════════════════════════════════════════════════════

class StatusCodeTest(BaseTestCase):
    """
    Verify the API returns correct HTTP status codes as per
    industry convention (Lecture 2, slide 13).
    """

    def test_200_on_list(self):
        resp = self.client.get('/api/teams/')
        self.assertEqual(resp.status_code, 200)

    def test_201_on_create(self):
        client = self.auth_client()
        resp = client.post('/api/teams/', {
            'name': 'Liverpool', 'short_name': 'LIV',
        })
        self.assertEqual(resp.status_code, 201)

    def test_204_on_delete(self):
        client = self.auth_client()
        resp = client.delete(f'/api/teams/{self.team1.id}/')
        self.assertEqual(resp.status_code, 204)

    def test_400_on_bad_data(self):
        client = self.auth_client()
        resp = client.post('/api/teams/', {})  # missing required fields
        self.assertEqual(resp.status_code, 400)

    def test_401_on_unauthenticated_write(self):
        resp = self.client.post('/api/teams/', {'name': 'X', 'short_name': 'XX'})
        self.assertEqual(resp.status_code, 401)

    def test_404_on_missing_resource(self):
        resp = self.client.get('/api/teams/99999/')
        self.assertEqual(resp.status_code, 404)
