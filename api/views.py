"""
Views for the SportsPulse API.

CRUD endpoints use DRF viewsets. Analytics endpoints delegate their
aggregation work to a small service layer so the HTTP layer stays thin.
"""

from django.contrib.auth import authenticate
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Match, Player, PlayerMatchStatistic, Team
from .serializers import (
    LoginSerializer,
    MatchSerializer,
    PlayerMatchStatisticSerializer,
    PlayerSerializer,
    RegisterSerializer,
    TeamSerializer,
)
from .services import (
    build_head_to_head_payload,
    build_leaderboard_payload,
    build_player_profile_payload,
    build_season_summary_payload,
    build_team_performance_payload,
)
from .validators import normalise_choice, parse_positive_int, validate_season_code


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Create a new user account and return a token immediately.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    @extend_schema(
        request=RegisterSerializer,
        responses={201: dict},
        tags=['Auth'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'message': 'Account created successfully.',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                    },
                    'token': token.key,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticate with username/password and return a token.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    @extend_schema(
        request=LoginSerializer,
        responses={200: dict},
        tags=['Auth'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'message': 'Login successful.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'token': token.key,
            },
            status=status.HTTP_200_OK,
        )


class TeamViewSet(viewsets.ModelViewSet):
    """
    CRUD for football teams.
    """

    serializer_class = TeamSerializer

    def get_queryset(self):
        queryset = Team.objects.all()

        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter('country', str, description='Filter by country'),
            OpenApiParameter('search', str, description='Search by team name'),
        ],
        tags=['Teams'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['Teams'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['Teams'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Teams'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=['Teams'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=['Teams'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(tags=['Teams'])
    @action(detail=True, methods=['get'], url_path='players')
    def players(self, request, pk=None):
        """
        GET /api/teams/{id}/players/
        """

        team = self.get_object()
        serializer = PlayerSerializer(team.players.all(), many=True)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    """
    CRUD for players with optional filtering.
    """

    serializer_class = PlayerSerializer

    def get_queryset(self):
        queryset = Player.objects.select_related('team').all()

        team_id = parse_positive_int(
            self.request.query_params.get('team'),
            field_name='team',
        )
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        position = normalise_choice(
            self.request.query_params.get('position'),
            field_name='position',
            allowed={code for code, _ in Player.POSITION_CHOICES},
        )
        if position:
            queryset = queryset.filter(position=position)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter('team', int, description='Filter by team ID'),
            OpenApiParameter(
                'position',
                str,
                description='Filter by position code (GK/DF/MF/FW)',
            ),
            OpenApiParameter('search', str, description='Search by player name'),
        ],
        tags=['Players'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['Players'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['Players'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Players'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=['Players'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=['Players'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MatchViewSet(viewsets.ModelViewSet):
    """
    CRUD for matches with optional filtering.
    """

    serializer_class = MatchSerializer

    def get_queryset(self):
        queryset = Match.objects.select_related('home_team', 'away_team').all()

        team_id = parse_positive_int(
            self.request.query_params.get('team'),
            field_name='team',
        )
        if team_id:
            queryset = queryset.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id)
            )

        season = validate_season_code(
            self.request.query_params.get('season'),
            field_name='season',
        )
        if season:
            queryset = queryset.filter(season=season)

        match_status = normalise_choice(
            self.request.query_params.get('status'),
            field_name='status',
            allowed={code for code, _ in Match.STATUS_CHOICES},
        )
        if match_status:
            queryset = queryset.filter(status=match_status)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'team',
                int,
                description='Filter by team ID (home or away)',
            ),
            OpenApiParameter(
                'season',
                str,
                description='Filter by season, e.g. 2024/2025',
            ),
            OpenApiParameter(
                'status',
                str,
                description='Filter by status (SCHEDULED/LIVE/COMPLETED/POSTPONED)',
            ),
        ],
        tags=['Matches'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['Matches'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['Matches'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Matches'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=['Matches'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=['Matches'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PlayerMatchStatisticViewSet(viewsets.ModelViewSet):
    """
    CRUD for per-match player statistics.
    """

    serializer_class = PlayerMatchStatisticSerializer

    def get_queryset(self):
        queryset = PlayerMatchStatistic.objects.select_related(
            'player',
            'player__team',
            'match',
            'match__home_team',
            'match__away_team',
        ).all()

        player_id = parse_positive_int(
            self.request.query_params.get('player'),
            field_name='player',
        )
        if player_id:
            queryset = queryset.filter(player_id=player_id)

        match_id = parse_positive_int(
            self.request.query_params.get('match'),
            field_name='match',
        )
        if match_id:
            queryset = queryset.filter(match_id=match_id)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter('player', int, description='Filter by player ID'),
            OpenApiParameter('match', int, description='Filter by match ID'),
        ],
        tags=['Statistics'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['Statistics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['Statistics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Statistics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=['Statistics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=['Statistics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class LeaderboardView(APIView):
    """
    GET /api/analytics/leaderboard/
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'metric',
                str,
                description='Ranking metric: goals or assists',
            ),
            OpenApiParameter('season', str, description='Filter by season'),
            OpenApiParameter(
                'limit',
                int,
                description='Number of results (default 10, max 50)',
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=['Analytics'],
    )
    def get(self, request):
        payload = build_leaderboard_payload(
            metric=request.query_params.get('metric', 'goals'),
            season=request.query_params.get('season'),
            limit=request.query_params.get('limit'),
        )
        return Response(payload)


class TeamPerformanceView(APIView):
    """
    GET /api/analytics/team-performance/
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter('season', str, description='Filter by season'),
            OpenApiParameter('team', int, description='Single team ID'),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=['Analytics'],
    )
    def get(self, request):
        payload = build_team_performance_payload(
            season=request.query_params.get('season'),
            team_id=request.query_params.get('team'),
        )
        return Response(payload)


class HeadToHeadView(APIView):
    """
    GET /api/analytics/head-to-head/?team1=1&team2=2
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'team1',
                int,
                required=True,
                description='First team ID',
            ),
            OpenApiParameter(
                'team2',
                int,
                required=True,
                description='Second team ID',
            ),
            OpenApiParameter('season', str, description='Optional season filter'),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=['Analytics'],
    )
    def get(self, request):
        payload = build_head_to_head_payload(
            team1_id=request.query_params.get('team1'),
            team2_id=request.query_params.get('team2'),
            season=request.query_params.get('season'),
        )
        return Response(payload)


class SeasonSummaryView(APIView):
    """
    GET /api/analytics/season-summary/?season=2024/2025
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'season',
                str,
                required=True,
                description='Season, e.g. 2024/2025',
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=['Analytics'],
    )
    def get(self, request):
        payload = build_season_summary_payload(
            season=request.query_params.get('season'),
        )
        return Response(payload)


class PlayerProfileView(APIView):
    """
    GET /api/analytics/player-profile/{id}/
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Analytics'], responses={200: OpenApiTypes.OBJECT})
    def get(self, request, pk):
        payload = build_player_profile_payload(player_id=pk)
        return Response(payload)
