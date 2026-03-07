"""
URL routing for the api application.

Uses DRF's DefaultRouter for CRUD viewsets — this automatically generates
the standard REST endpoint patterns (list, create, retrieve, update, delete)
from a single registration call. Analytics and auth views are registered
as plain paths since they aren't standard CRUD.

The URL design follows REST best practices from Lecture 3:
  - Resources are nouns (teams, players, matches, statistics)
  - Unique and stable identifiers (/teams/1/ rather than /getTeam?id=1)
  - Hierarchical structure for nested resources (/teams/1/players/)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# The router creates URL patterns for all CRUD operations automatically
router = DefaultRouter()
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'players', views.PlayerViewSet, basename='player')
router.register(r'matches', views.MatchViewSet, basename='match')
router.register(r'statistics', views.PlayerMatchStatisticViewSet, basename='statistic')

urlpatterns = [
    # CRUD endpoints via router
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),

    # Analytics endpoints (read-only, no auth needed)
    path(
        'analytics/leaderboard/',
        views.LeaderboardView.as_view(),
        name='leaderboard',
    ),
    path(
        'analytics/team-performance/',
        views.TeamPerformanceView.as_view(),
        name='team-performance',
    ),
    path(
        'analytics/head-to-head/',
        views.HeadToHeadView.as_view(),
        name='head-to-head',
    ),
    path(
        'analytics/season-summary/',
        views.SeasonSummaryView.as_view(),
        name='season-summary',
    ),
    path(
        'analytics/player-profile/<int:pk>/',
        views.PlayerProfileView.as_view(),
        name='player-profile',
    ),
]
