"""
Management command to populate the database with sample football data.

Usage:
    python manage.py seed_data

This creates 6 Premier League teams, ~30 players, 15 matches, and
per-match statistics. Having realistic data makes the API demonstrable
during the oral exam without manual data entry.

I found the idea of a seed script from Django docs and various
tutorials — it automates what would otherwise be tedious admin work.
"""

import random
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import Team, Player, Match, PlayerMatchStatistic


class Command(BaseCommand):
    help = 'Seed the database with sample football data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Clear existing data (idempotent re-run)
        PlayerMatchStatistic.objects.all().delete()
        Match.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()

        # ── Create teams ──────────────────────────────────
        teams_data = [
            {
                'name': 'Arsenal',
                'short_name': 'ARS',
                'country': 'England',
                'founded_year': 1886,
                'stadium': 'Emirates Stadium',
            },
            {
                'name': 'Chelsea',
                'short_name': 'CHE',
                'country': 'England',
                'founded_year': 1905,
                'stadium': 'Stamford Bridge',
            },
            {
                'name': 'Liverpool',
                'short_name': 'LIV',
                'country': 'England',
                'founded_year': 1892,
                'stadium': 'Anfield',
            },
            {
                'name': 'Manchester City',
                'short_name': 'MCI',
                'country': 'England',
                'founded_year': 1880,
                'stadium': 'Etihad Stadium',
            },
            {
                'name': 'Manchester United',
                'short_name': 'MUN',
                'country': 'England',
                'founded_year': 1878,
                'stadium': 'Old Trafford',
            },
            {
                'name': 'Tottenham Hotspur',
                'short_name': 'TOT',
                'country': 'England',
                'founded_year': 1882,
                'stadium': 'Tottenham Hotspur Stadium',
            },
        ]

        teams = []
        for td in teams_data:
            team = Team.objects.create(**td)
            teams.append(team)
            self.stdout.write(f'  Created team: {team.name}')

        # ── Create players ────────────────────────────────
        players_data = {
            'Arsenal': [
                ('David Raya', 'GK', 'Spain', 13),
                ('William Saliba', 'DF', 'France', 2),
                ('Ben White', 'DF', 'England', 4),
                ('Declan Rice', 'MF', 'England', 41),
                ('Martin Odegaard', 'MF', 'Norway', 8),
                ('Bukayo Saka', 'FW', 'England', 7),
            ],
            'Chelsea': [
                ('Robert Sanchez', 'GK', 'Spain', 1),
                ('Levi Colwill', 'DF', 'England', 6),
                ('Reece James', 'DF', 'England', 24),
                ('Enzo Fernandez', 'MF', 'Argentina', 8),
                ('Cole Palmer', 'MF', 'England', 20),
                ('Nicolas Jackson', 'FW', 'Senegal', 15),
            ],
            'Liverpool': [
                ('Alisson Becker', 'GK', 'Brazil', 1),
                ('Virgil van Dijk', 'DF', 'Netherlands', 4),
                ('Trent Alexander-Arnold', 'DF', 'England', 66),
                ('Alexis Mac Allister', 'MF', 'Argentina', 10),
                ('Ryan Gravenberch', 'MF', 'Netherlands', 38),
                ('Mohamed Salah', 'FW', 'Egypt', 11),
            ],
            'Manchester City': [
                ('Ederson Moraes', 'GK', 'Brazil', 31),
                ('Ruben Dias', 'DF', 'Portugal', 3),
                ('Kyle Walker', 'DF', 'England', 2),
                ('Kevin De Bruyne', 'MF', 'Belgium', 17),
                ('Phil Foden', 'MF', 'England', 47),
                ('Erling Haaland', 'FW', 'Norway', 9),
            ],
            'Manchester United': [
                ('Andre Onana', 'GK', 'Cameroon', 24),
                ('Harry Maguire', 'DF', 'England', 5),
                ('Lisandro Martinez', 'DF', 'Argentina', 6),
                ('Bruno Fernandes', 'MF', 'Portugal', 8),
                ('Kobbie Mainoo', 'MF', 'England', 37),
                ('Marcus Rashford', 'FW', 'England', 10),
            ],
            'Tottenham Hotspur': [
                ('Guglielmo Vicario', 'GK', 'Italy', 13),
                ('Cristian Romero', 'DF', 'Argentina', 17),
                ('Micky van de Ven', 'DF', 'Netherlands', 37),
                ('James Maddison', 'MF', 'England', 10),
                ('Dejan Kulusevski', 'MF', 'Sweden', 21),
                ('Son Heung-min', 'FW', 'South Korea', 7),
            ],
        }

        all_players = {}
        for team in teams:
            team_players = players_data[team.name]
            all_players[team.name] = []
            for name, pos, nat, num in team_players:
                player = Player.objects.create(
                    name=name, team=team, position=pos,
                    nationality=nat, jersey_number=num,
                )
                all_players[team.name].append(player)
            self.stdout.write(
                f'  Created {len(team_players)} players for {team.name}'
            )

        # ── Create matches ────────────────────────────────
        season = '2024/2025'
        match_date = datetime(2024, 8, 17, 15, 0, tzinfo=timezone.utc)
        matches = []

        # Round-robin: each team plays every other team once at home
        for i, home in enumerate(teams):
            for j, away in enumerate(teams):
                if i == j:
                    continue
                home_score = random.randint(0, 4)
                away_score = random.randint(0, 3)
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    date=match_date,
                    venue=home.stadium,
                    season=season,
                    home_score=home_score,
                    away_score=away_score,
                    status='COMPLETED',
                )
                matches.append(match)
                match_date += timedelta(days=random.randint(3, 7))

        self.stdout.write(f'  Created {len(matches)} matches')

        # ── Create player statistics ──────────────────────
        stat_count = 0
        for match in matches:
            home_players = all_players[match.home_team.name]
            away_players = all_players[match.away_team.name]

            # Distribute home goals among home players
            home_goal_scorers = random.choices(
                [p for p in home_players if p.position != 'GK'],
                k=match.home_score,
            ) if match.home_score > 0 else []

            away_goal_scorers = random.choices(
                [p for p in away_players if p.position != 'GK'],
                k=match.away_score,
            ) if match.away_score > 0 else []

            for player in home_players:
                goals = home_goal_scorers.count(player)
                PlayerMatchStatistic.objects.create(
                    player=player,
                    match=match,
                    goals=goals,
                    assists=random.randint(0, 1) if player.position != 'GK' else 0,
                    minutes_played=random.randint(60, 90),
                    yellow_cards=1 if random.random() < 0.15 else 0,
                    red_cards=1 if random.random() < 0.02 else 0,
                    shots_on_target=random.randint(0, 4) if player.position in ('FW', 'MF') else 0,
                    passes_completed=random.randint(20, 70),
                    tackles=random.randint(0, 5),
                    saves=random.randint(1, 8) if player.position == 'GK' else 0,
                )
                stat_count += 1

            for player in away_players:
                goals = away_goal_scorers.count(player)
                PlayerMatchStatistic.objects.create(
                    player=player,
                    match=match,
                    goals=goals,
                    assists=random.randint(0, 1) if player.position != 'GK' else 0,
                    minutes_played=random.randint(60, 90),
                    yellow_cards=1 if random.random() < 0.15 else 0,
                    red_cards=1 if random.random() < 0.02 else 0,
                    shots_on_target=random.randint(0, 4) if player.position in ('FW', 'MF') else 0,
                    passes_completed=random.randint(20, 70),
                    tackles=random.randint(0, 5),
                    saves=random.randint(1, 8) if player.position == 'GK' else 0,
                )
                stat_count += 1

        self.stdout.write(f'  Created {stat_count} player statistics')

        # ── Create a demo user with token ─────────────────
        if not User.objects.filter(username='demo').exists():
            demo_user = User.objects.create_user(
                username='demo',
                email='demo@sportspulse.com',
                password='demopass123',
            )
            token, _ = Token.objects.get_or_create(user=demo_user)
            self.stdout.write(f'  Demo user created — token: {token.key}')

        self.stdout.write(self.style.SUCCESS(
            '\nDatabase seeded successfully!'
        ))
