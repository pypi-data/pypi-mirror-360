from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from mountaineer.controller import ControllerBase
from mountaineer.logging import LOGGER
from mountaineer.paths import ManagedViewPath


@dataclass
class ClientBundleMetadata:
    package_root_link: ManagedViewPath

    # We keep a tmpdir open for the duration of the build process, so our rust
    # logic can leverage file-based caches for faster builds
    # Note that this tmpdir is shared across all client builders, so it's important
    # that you enforce uniqueness of filenames if you leverage this cache
    tmp_dir: Path

    live_reload_port: int | None = None


class APIBuilderBase(ABC):
    """
    Base class for client builders. When mounted to an AppController, these build plugins
    will be called for every file defined in the view/app directory. It's up to the plugin
    whether to handle the incoming file.

    """

    def __init__(self):
        self.metadata: ClientBundleMetadata | None = None

        self.dirty_files: set[Path] = set()
        self.controllers: list[tuple[ControllerBase, ManagedViewPath]] = []

    def set_metadata(self, metadata: ClientBundleMetadata):
        self.metadata = metadata

    def register_controller(
        self, controller: ControllerBase, view_path: ManagedViewPath
    ):
        self.controllers.append((controller, view_path))

    def mark_file_dirty(self, file_path: Path):
        self.dirty_files.add(file_path)

    async def build_wrapper(self):
        """
        All internal users should use this instead of .build()
        """
        await self.build()
        self.dirty_files.clear()

    @abstractmethod
    async def build(self):
        """
        Builds the dirty files.

        """
        pass

    def managed_views_from_paths(self, paths: list[Path]) -> list[ManagedViewPath]:
        """
        Given a list of paths, assume these fall somewhere within the view directories
        specified by the controllers. Returns the ManagedViewPath objects for
        all paths where a match is found.

        Only includes paths from controllers that have build enabled (excluding plugins).

        """
        # Index all of the unique view roots to track the DAG hierarchies
        # Only include controllers that have build enabled (exclude plugins)
        build_enabled_controllers = [
            (controller, view_path)
            for controller, view_path in self.controllers
            if controller._build_enabled
        ]
        unique_roots = {
            view_path.get_root_link() for _, view_path in build_enabled_controllers
        }

        # Convert all of the dirty files into managed paths
        converted_paths: list[ManagedViewPath] = []
        for path in paths:
            # Each file must be relative to one of our known view roots, otherwise
            # we ignore it
            found_root = False
            for root in unique_roots:
                if path.is_relative_to(root):
                    relative_path = path.relative_to(root)
                    converted_paths.append(root / relative_path)
                    found_root = True
                    break

            if not found_root:
                LOGGER.debug(
                    f"File {path} is not relative to any build-enabled view root ({unique_roots})"
                )

        return converted_paths
