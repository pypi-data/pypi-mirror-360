import re

from labels.utils.licenses.licenses_index import (
    COMMON_LICENSES,
    INVERSE_LICENSES,
    sanitization_pattern,
)


def sanitize_license_string(license_str: str) -> str:
    sanitized = re.sub(r"\s+", " ", license_str.strip())
    sanitized = re.sub(r"[,\s]+", " ", sanitized)
    sanitized = re.sub(sanitization_pattern, "", sanitized)
    return re.sub(r"\s+", " ", sanitized).strip()


def find_license_by_pattern(sanitized_license: str) -> str | None:
    for identifier, (pattern, _) in COMMON_LICENSES.items():
        if re.search(pattern, sanitized_license, re.IGNORECASE):
            return identifier
    return None


def validate_licenses(licenses: list[str]) -> list[str]:
    found_licenses = set()
    for declared_license in licenses:
        license_parts = [
            part.strip()
            for part in declared_license.replace(" OR ", ",").replace(" AND ", ",").split(",")
        ]

        for license_part in license_parts:
            sanitized_license = sanitize_license_string(license_part)
            identifier = find_license_by_pattern(sanitized_license)
            if identifier:
                found_licenses.add(identifier)
            else:
                full_name = INVERSE_LICENSES.get(sanitized_license)
                if full_name:
                    found_licenses.add(full_name)

    return sorted(found_licenses)
