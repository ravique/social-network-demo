from django_filters import rest_framework as filters

from social_network.models import Like


class LikesFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name="created__date", lookup_expr='gte')
    date_to = filters.DateFilter(field_name="created__date", lookup_expr='lte')

    class Meta:
        model = Like
        fields = ['date_from', 'date_to']
