from django import template

register = template.Library()

@register.filter
def class_name(obj):
    """オブジェクトのクラス名を取得するフィルター"""
    return obj.__class__.__name__