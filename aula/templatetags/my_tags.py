# your_app/templatetags/my_tags.py
from django import template

register = template.Library()

@register.filter
def get_form(forms_dict, question_id):
    return forms_dict.get(question_id)
