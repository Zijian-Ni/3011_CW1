"""
Reusable validators for query parameters and shared API inputs.
"""

import re

from rest_framework.exceptions import ValidationError


SEASON_CODE_RE = re.compile(r'^(?P<start>\d{4})/(?P<end>\d{4})$')


def validate_season_code(value, *, field_name='season', required=False):
    """
    Validate the coursework season format (e.g. 2024/2025).
    """
    if value in (None, ''):
        if required:
            raise ValidationError({field_name: 'This parameter is required.'})
        return None

    match = SEASON_CODE_RE.fullmatch(str(value))
    if not match:
        raise ValidationError({
            field_name: 'Use the format YYYY/YYYY, for example 2024/2025.',
        })

    start_year = int(match.group('start'))
    end_year = int(match.group('end'))
    if end_year != start_year + 1:
        raise ValidationError({
            field_name: 'The second year must be exactly one greater.',
        })

    return str(value)


def parse_positive_int(value, *, field_name, required=False):
    """
    Parse an optional positive integer query parameter.
    """
    if value in (None, ''):
        if required:
            raise ValidationError({field_name: 'This parameter is required.'})
        return None

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({
            field_name: 'Must be a positive integer.',
        }) from exc

    if parsed < 1:
        raise ValidationError({field_name: 'Must be a positive integer.'})

    return parsed


def parse_limited_positive_int(value, *, field_name, default, maximum):
    """
    Parse a positive integer and cap it at a configured maximum.
    """
    if value in (None, ''):
        return default

    parsed = parse_positive_int(value, field_name=field_name)
    return min(parsed, maximum)


def normalise_choice(value, *, field_name, allowed):
    """
    Normalise enum-like query params and reject unsupported values.
    """
    if value in (None, ''):
        return None

    normalised = str(value).upper()
    if normalised not in allowed:
        allowed_values = ', '.join(sorted(allowed))
        raise ValidationError({
            field_name: f'Must be one of: {allowed_values}.',
        })

    return normalised
