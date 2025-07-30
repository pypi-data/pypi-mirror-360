import logging

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import Location
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.python.model import PythonPackage
from labels.parsers.cataloger.python.parse_wheel_egg_metadata import ParsedData
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def new_package_for_package(
    data: ParsedData,
    sources: Location,
) -> Package | None:
    name = data.python_package.name
    version = data.python_package.version

    if not name or not version:
        return None

    try:
        return Package(
            name=name,
            version=version,
            p_url=package_url(
                name,
                version,
                data.python_package,
            ),
            locations=[sources],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            metadata=data.python_package,
            licenses=[],
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": sources.path(),
                },
            },
        )
        return None


def package_url(name: str, version: str, package: PythonPackage | None) -> str:
    return PackageURL(
        type="pypi",
        namespace="",
        name=name,
        version=version,
        qualifiers=_purl_qualifiers_for_package(package),
        subpath="",
    ).to_string()


def _purl_qualifiers_for_package(
    package: PythonPackage | None,
) -> dict[str, str]:
    if not package:
        return {}
    if (
        hasattr(package, "direct_url_origin")
        and package.direct_url_origin
        and package.direct_url_origin.vcs
    ):
        url = package.direct_url_origin
        return {"vcs_url": f"{url.vcs}+{url.url}@{url.commit_id}"}
    return {}
