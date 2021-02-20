import re


def _headers():
    return {
        "Cookie": open("cookie",encoding="utf-8",mode="r").read()
    }

def set_cookie(cookie):
    with open("cookie",encoding="utf-8",mode="w") as f:
        f.write(cookie)

def _temp_headers(Cookie):
    return {
        "Cookie": Cookie
    }

def _cookies():
    return [
        {'domain': '11.36.18.196', 'httpOnly': True, 'name': 'JSESSIONID', 'path': '/qbzc/', 'secure': False,
         'value': re.findall(r'JSESSIONID=(.*?);',open("cookie",encoding="utf-8",mode="r").read())[0]}
    ]
