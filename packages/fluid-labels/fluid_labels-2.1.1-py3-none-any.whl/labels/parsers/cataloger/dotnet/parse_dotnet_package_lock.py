import logging
from collections.abc import Iterator
from copy import deepcopy
from typing import TYPE_CHECKING, cast

from more_itertools import flatten
from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import DependencyType, LocationReadCloser
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
    results: list[Relationship] = []
    for package_name, depens in dependencies.items():
        if not isinstance(depens, IndexedDict):
            continue
        deps = (p for p in packages for dep_name in depens if dep_name == p.name)
        if current_package := next(
            (x for x in packages if x.name == package_name),
            None,
        ):
            results.extend(
                Relationship(
                    from_=x.id_,
                    to_=current_package.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
                for x in deps
            )
    return results


def parse_dotnet_package_lock(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    packages: list[Package] = []
    target_deps: ParsedValue = package_json.get("dependencies", IndexedDict())
    if not isinstance(target_deps, IndexedDict):
        LOGGER.warning("No deps found in package JSON")
        return ([], [])
    dependencies: dict[str, ParsedValue] = {}

    for package_name, package_value in cast(
        "Iterator[IndexedDict[str, ParsedValue]]",
        flatten(x.items() for x in target_deps.values() if isinstance(x, IndexedDict)),
    ):
        if not isinstance(package_value, IndexedDict):
            continue

        is_transitive: str = package_value.get("type", "") == "Transitive"

        version: str | None = package_value.get("resolved")

        if not package_name or not version:
            continue

        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = package_value.position.start.line
            location.dependency_type = (
                DependencyType.TRANSITIVE if is_transitive else DependencyType.DIRECT
            )

        dependencies[package_name] = package_value.get("dependencies", EMPTY_DICT)
        try:
            packages.append(
                Package(
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

    relationships: list[Relationship] = _get_relationships(packages, dependencies)

    return packages, relationships
