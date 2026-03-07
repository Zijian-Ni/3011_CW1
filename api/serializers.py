"""
Serializers translate between Django model instances and JSON.

Each model has its own serializer. Some include nested read-only
representations (e.g. team names inside a player response) so that
clients receive self-descriptive messages — aligning with REST
constraint 4.3 from Lecture 3.
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team, Player, Match, PlayerMatchStatistic
from .validators import validate_season_code


# ─── Authentication serializers ────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration.
    Password is write-only so it never appears in responses.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # Use create_user to hash the password properly
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Accepts username + password for token retrieval."""
    username = serializers.CharField()
    password = serializers.CharField()


# ─── Team serializers ──────────────────────────────────────

class TeamSerializer(serializers.ModelSerializer):
    """
    Full Team representation.
    player_count is a read-only computed field that tells the client
    how many players belong to this team.
    """
    player_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'short_name', 'country', 'founded_year',
            'stadium', 'crest_url', 'player_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_player_count(self, obj) -> int:
        return obj.players.count()


class TeamSummarySerializer(serializers.ModelSerializer):
    """Lightweight team representation used in nested contexts."""
    class Meta:
        model = Team
        fields = ['id', 'name', 'short_name']


# ─── Player serializers ───────────────────────────────────

class PlayerSerializer(serializers.ModelSerializer):
    """
    Full Player representation.
    On read, the team is shown as a nested object so the response is
    self-descriptive. On write, the client sends team as an integer ID.
    """
    team_detail = TeamSummarySerializer(source='team', read_only=True)
    position_display = serializers.CharField(
        source='get_position_display', read_only=True,
    )

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'team', 'team_detail', 'position',
            'position_display', 'nationality', 'date_of_birth',
            'jersey_number', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'team': {'write_only': True},
        }


class PlayerSummarySerializer(serializers.ModelSerializer):
    """Minimal player info for nested use (e.g. inside statistics)."""
    team_name = serializers.CharField(source='team.short_name', read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'name', 'team_name', 'position', 'jersey_number']


# ─── Match serializers ─────────────────────────────────────

class MatchSerializer(serializers.ModelSerializer):
    """
    Full Match representation.
    Includes nested team summaries and a computed result_summary field
    so the client doesn't need to calculate the winner itself.
    """
    home_team_detail = TeamSummarySerializer(source='home_team', read_only=True)
    away_team_detail = TeamSummarySerializer(source='away_team', read_only=True)
    result_summary = serializers.CharField(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'home_team', 'home_team_detail',
            'away_team', 'away_team_detail',
            'date', 'venue', 'season',
            'home_score', 'away_score', 'status',
            'result_summary',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'home_team': {'write_only': True},
            'away_team': {'write_only': True},
        }

    def validate(self, data):
        """Ensure a team doesn't play against itself."""
        home = data.get('home_team')
        away = data.get('away_team')
        if home and away and home == away:
            raise serializers.ValidationError(
                'A team cannot play against itself.'
            )
        return data

    def validate_season(self, value):
        """Keep season filters and persisted match data aligned."""
        try:
            return validate_season_code(
                value,
                field_name='season',
                required=True,
            )
        except serializers.ValidationError as exc:
            detail = exc.detail
            if isinstance(detail, dict):
                detail = detail.get('season', detail)
            raise serializers.ValidationError(detail)


class MatchSummarySerializer(serializers.ModelSerializer):
    """Short match info for nested contexts."""
    home_team_name = serializers.CharField(
        source='home_team.short_name', read_only=True,
    )
    away_team_name = serializers.CharField(
        source='away_team.short_name', read_only=True,
    )

    class Meta:
        model = Match
        fields = [
            'id', 'home_team_name', 'away_team_name',
            'home_score', 'away_score', 'date', 'status',
        ]


# ─── PlayerMatchStatistic serializers ──────────────────────

class PlayerMatchStatisticSerializer(serializers.ModelSerializer):
    """
    Full per-match statistic record.
    Nested player and match summaries make the response informative
    without requiring extra API calls (HATEOAS spirit, Lecture 3).
    """
    player_detail = PlayerSummarySerializer(source='player', read_only=True)
    match_detail = MatchSummarySerializer(source='match', read_only=True)

    class Meta:
        model = PlayerMatchStatistic
        fields = [
            'id', 'player', 'player_detail',
            'match', 'match_detail',
            'goals', 'assists', 'minutes_played',
            'yellow_cards', 'red_cards',
            'shots_on_target', 'passes_completed',
            'tackles', 'saves',
            'created_at',
        ]
        read_only_fields = ['created_at']
        extra_kwargs = {
            'player': {'write_only': True},
            'match': {'write_only': True},
        }
