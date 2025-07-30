import re

COMMENT_REGEX = re.compile(r'(s1cns:skip=) *([A-Za-z_\d]+)(:[^\n]+)?')
