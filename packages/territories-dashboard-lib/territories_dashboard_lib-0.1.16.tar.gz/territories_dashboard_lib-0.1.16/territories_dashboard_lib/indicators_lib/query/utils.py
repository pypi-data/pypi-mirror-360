from django.conf import settings
from django.db import connections


def get_breakdown_dimension(indicator):
    breakdown_dimension = (
        indicator.dimensions.filter(is_breakdown=True).first()
        if indicator.dimensions.count() > 1
        else indicator.dimensions.first()
    )
    return breakdown_dimension


def run_custom_query(query, params=None):
    with connections[settings.INDICATORS_DATABASE].cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        return results
