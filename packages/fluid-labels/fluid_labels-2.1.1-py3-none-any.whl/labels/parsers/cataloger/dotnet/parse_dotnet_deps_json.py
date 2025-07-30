import logging
from copy import deepcopy
from typing import TYPE_CHECKING, cast

from more_itertools import flatten
from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.collection.json import parse_json_with_tree_sitter
from labels.utils.strings import format_exception

if TYPE_CHECKING:
    from collections.abc import Iterator

LOGGER = logging.getLogger(__name__)

EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def _get_relationships(
    packages: list[Package],
    dependencies: dict[str, ParsedValue],
) -> list[Relationship]:
    result: list[Relationship] = []
    for package_name, depens in dependencies.items():
        if not isinstance(depens, IndexedDict):
            continue
        deps_gen = (
            p
            for p in packages
            for dep_name in depens
            if dep_name == p.name and isinstance(depens, IndexedDict)
        )
        current_package = next((p for p in packages if p.name == package_name), None)
        if current_package is not None:
            result.extend(
                Relationship(
                    from_=p.id_,
                    to_=current_package.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
                for p in deps_gen
            )
    return result


def parse_dotnet_deps_json(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    packages: list[Package] = []
    targets: ParsedValue = package_json.get("targets", IndexedDict())
    dependencies: dict[str, ParsedValue] = {}
    if not isinstance(targets, IndexedDict):
        LOGGER.warning("No targets found in package JSON")
        return ([], [])
    for package_key, package_value in cast(
        "Iterator[IndexedDict[str, ParsedValue]]",
        flatten(x.items() for x in targets.values() if isinstance(x, IndexedDict)),
    ):
        if not isinstance(package_key, str) or "/" not in package_key:
            continue
        package_name, version = package_key.split("/", 1)
        if not isinstance(package_value, IndexedDict):
            continue
        location = deepcopy(reader.location)
        pos = package_value.position
        if hasattr(location, "coordinates") and location.coordinates:
            location.coordinates.line = pos.start.line
        dependencies[package_name] = package_value.get("dependencies", EMPTY_DICT)
        try:
            pkg = Package(
                name=package_name,
                version=version,
                locations=[location],
                licenses=[],
                type=PackageType.DotnetPkg,
                language=Language.DOTNET,
                metadata=None,
                p_url=PackageURL(
                    type="nuget",
                    namespace="",
                    name=package_name,
                    version=version,
                    qualifiers={},
                    subpath="",
                ).to_string(),
            )
            packages.append(pkg)
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

    relationships: list[Relationship] = _get_relationships(packages, dependencies)
    return packages, relationships
