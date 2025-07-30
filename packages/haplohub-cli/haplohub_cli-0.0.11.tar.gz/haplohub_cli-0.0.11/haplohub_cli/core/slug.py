import re

non_alphanum_re = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return non_alphanum_re.sub("-", text.lower()).strip("-")
