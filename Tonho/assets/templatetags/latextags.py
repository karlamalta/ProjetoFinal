'''
Created on Oct 7, 2010

@author: yguarata
'''

from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

NEWLINE_TEXTAREA = '\r\n'

@stringfilter
def itemsnewline(value):
    t = ' \item ' + ' \item '.join(value.split(NEWLINE_TEXTAREA))
    return t

@stringfilter
def latexnewline(value):
    t =  ' \\newline '.join(value.split(NEWLINE_TEXTAREA))
    return t

register.filter('itemsnewline', itemsnewline)
register.filter('latexnewline', latexnewline)