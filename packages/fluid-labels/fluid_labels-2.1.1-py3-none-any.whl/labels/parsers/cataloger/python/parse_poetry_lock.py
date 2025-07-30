import logging

from pydantic import ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.model import PythonRequirementsEntry
from labels.parsers.cataloger.python.package import package_url
from labels.parsers.collection import toml
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int) -> Location:
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        return location.model_copy(update=l_upd)
    return location


def parse_poetry_lock(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    _content = reader.read_closer.read()

    toml_content: IndexedDict[str, ParsedValue] = toml.parse_toml_with_tree_sitter(_content)

    packages = _parse_packages(toml_content, reader)
    relationships = _parse_relationships(toml_content, packages)

    return packages, relationships


def _parse_packages(
    toml_content: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
) -> list[Package]:
    packages = []
    toml_pkgs = toml_content.get("package")
    if not isinstance(toml_pkgs, IndexedList):
        return []
    for package in toml_pkgs:
        if not isinstance(package, IndexedDict):
            continue
        name: str = str(package.get("name", ""))
        version: str = str(package.get("version", ""))

        if not name or not version:
            continue
        p_url = package_url(name, version, package)  # type: ignore

        location = (
            _get_location(reader.location, package.get_key_position("version").start.line)
            if isinstance(package, IndexedDict)
            else reader.location
        )

        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    found_by=None,
                    locations=[location],
                    language=Language.PYTHON,
                    p_url=p_url,
                    metadata=PythonRequirementsEntry(
                        name=name,
                        extras=[],
                        markers=p_url,
                    ),
                    licenses=[],
                    type=PackageType.PythonPkg,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": location.path(),
                    },
                },
            )
            continue

    return packages


def _get_dependencies(
    package: ParsedValue,
    packages: list[Package],
) -> tuple[Package | None, IndexedDict[str, ParsedValue]] | None:
    if not isinstance(package, IndexedDict):
        return None
    _pkg = next((pkg for pkg in packages if pkg.name == package["name"]), None)
    deps = package.get("dependencies")
    if not isinstance(deps, IndexedDict):
        return None
    return _pkg, deps


def _parse_relationships(
    toml_content: IndexedDict[str, ParsedValue],
    packages: list[Package],
) -> list[Relationship]:
    relationships = []
    _pkg: Package | None = None
    toml_pkgs = toml_content.get("package")
    if not isinstance(toml_pkgs, IndexedList):
        return []
    for package in toml_pkgs:
        results = _get_dependencies(package, packages)
        if results:
            _pkg, deps = results
            dependencies = list(deps.keys())

        if _pkg and dependencies:
            for dep in dependencies:
                dep_pkg = next((pkg for pkg in packages if pkg.name == dep), None)
                if dep_pkg:
                    relationships.append(
                        Relationship(
                            from_=dep_pkg.id_,
                            to_=_pkg.id_,
                            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                        ),
                    )

    return relationships
