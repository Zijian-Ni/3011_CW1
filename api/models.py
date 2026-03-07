"""
Database models for the SportsPulse API.

Four interconnected models represent football data:
  Team  →  Player  (one-to-many)
  Team  →  Match   (home / away foreign keys)
  Match + Player → PlayerMatchStatistic (join table with extra data)

Each model maps to a database table via Django's ORM, as covered in
Lecture 6 (slides 6-8). Fields use the built-in Django field types
with appropriate constraints and defaults.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Team(models.Model):
    """
    Represents a football team.

    Fields deliberately kept focused on what the API actually needs —
    name, abbreviation, country, founding year, stadium, and an optional
    crest image URL.
    """
    name = models.CharField(max_length=128, unique=True)
    short_name = models.CharField(
        max_length=5,
        unique=True,
        help_text='Abbreviation, e.g. ARS for Arsenal',
    )
    country = models.CharField(max_length=64, default='England')
    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2030)],
    )
    stadium = models.CharField(max_length=128, blank=True, default='')
    crest_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    # String representation — Lecture 7, slide 5
    def __str__(self):
        return f'{self.name} ({self.short_name})'


class Player(models.Model):
    """
    A player belonging to one team.

    The team field is a ForeignKey (Lecture 7, slides 9-10), so deleting
    a team cascades to its players. Position choices use Django's
    'choices' parameter (Lecture 6, slide 7).
    """
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('FW', 'Forward'),
    ]

    name = models.CharField(max_length=128)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players',
    )
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    nationality = models.CharField(max_length=64, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    jersey_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['team', 'jersey_number']
        # A jersey number should be unique within a team
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'jersey_number'],
                name='unique_jersey_per_team',
            )
        ]

    def __str__(self):
        return f'{self.name} (#{self.jersey_number}, {self.team.short_name})'


class Match(models.Model):
    """
    A single football match between a home and away team.

    Two ForeignKey fields point at Team, with related_name differentiation
    so we can do team.home_matches and team.away_matches separately.
    Status tracks whether a match is scheduled, in progress, or completed.
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('COMPLETED', 'Completed'),
        ('POSTPONED', 'Postponed'),
    ]

    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_matches',
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches',
    )
    date = models.DateTimeField()
    venue = models.CharField(max_length=128, blank=True, default='')
    season = models.CharField(
        max_length=9,
        help_text='Format: 2024/2025',
    )
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SCHEDULED',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'matches'

    def __str__(self):
        return (
            f'{self.home_team.short_name} {self.home_score} - '
            f'{self.away_score} {self.away_team.short_name} '
            f'({self.date.strftime("%Y-%m-%d")})'
        )

    @property
    def result_summary(self):
        """Return a short string like 'HOME_WIN', 'AWAY_WIN', or 'DRAW'."""
        if self.status != 'COMPLETED':
            return 'PENDING'
        if self.home_score > self.away_score:
            return 'HOME_WIN'
        elif self.away_score > self.home_score:
            return 'AWAY_WIN'
        return 'DRAW'


class PlayerMatchStatistic(models.Model):
    """
    Per-match statistics for an individual player.

    This acts as a join table between Player and Match but carries
    additional data fields (goals, assists, cards, etc.), making it
    a model in its own right rather than a simple many-to-many table.
    """
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='match_stats',
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='player_stats',
    )
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(120)],
    )
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    shots_on_target = models.PositiveIntegerField(default=0)
    passes_completed = models.PositiveIntegerField(default=0)
    tackles = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match__date']
        # One stat record per player per match
        constraints = [
            models.UniqueConstraint(
                fields=['player', 'match'],
                name='unique_player_match_stat',
            )
        ]

    def __str__(self):
        return (
            f'{self.player.name} — {self.match} '
            f'(G:{self.goals} A:{self.assists})'
        )
