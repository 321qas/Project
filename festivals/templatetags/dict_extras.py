# 커스텀 템플릿 필터, templates/region_interest_chart.html에 region: "{{ region_labels|get_item:obj.region }}" 부분 사용하기 위해 필요

from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


