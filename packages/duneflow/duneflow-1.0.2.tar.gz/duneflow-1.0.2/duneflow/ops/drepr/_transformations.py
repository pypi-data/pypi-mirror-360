from __future__ import annotations


def decimal_number(value):
    try:
        value = value.strip()
        return float(value)
    except:
        return value


def integer_number(value):
    try:
        value = value.strip()
        return int(value)
    except:
        return value


def number(value):
    try:
        value = value.strip()
        if value.isdigit():
            return int(value)
        return float(value)
    except:
        return value


def drepr_uri(value):
    from hashlib import sha256
    from urllib.parse import urljoin, urlparse

    result = urlparse(value)
    if result.netloc != "" and result.scheme != "":
        return value

    # urljoin works for Domain-relative URLs
    return urljoin("{{ BASE_URI }}", sha256(value.encode()).hexdigest())


def global_coordinate(value):
    from lat_lon_parser import parse

    try:
        part = {" ", ".", "°", "′", "″", "'", '"'}
        norm_value = (
            value.lower().replace("b", "n").replace("đ", "e").replace("t", "w").upper()
        )
        split_index = -1
        for i, c in enumerate(norm_value):
            if c.isdigit() or c in part:
                continue
            split_index = i + 1
            break

        if split_index == -1:
            return value

        part1, part2 = norm_value[:split_index], norm_value[split_index:]
        if "E" in part2 or "W" in part2:
            lat, long = part1, part2
        else:
            lat, long = part2, part1

        lat = parse(lat)
        long = parse(long)
        return f"Point({long} {lat})"
    except:
        return value
