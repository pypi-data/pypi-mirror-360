import re

TMP = """From: %s
To: %s
Subject: %s

%s"""

def strip_html(s):
    p = re.compile(r'<.*?>')
    return p.sub("", s)