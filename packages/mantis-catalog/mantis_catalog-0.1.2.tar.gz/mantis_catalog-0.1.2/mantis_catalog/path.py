# -*- coding: utf-8 -*-
import os
from pathlib import Path

from mantis_catalog.config import catalog_config
from mantis_catalog.config import StorageType
from upath import UPath
from upath.registry import register_implementation


class ResourcePath(UPath):
    def __init__(self, *args, **kwargs):
        storage_backend = catalog_config.storage.backend
        match catalog_config.storage.type:
            case StorageType.local:
                path = UPath(storage_backend.path, protocol="local")
            case StorageType.s3:
                path = UPath(
                    "s3://",
                    endpoint_url=storage_backend.endpoint_url,
                    key=storage_backend.access_key,
                    secret=storage_backend.secret_key,
                    bucket=storage_backend.bucket_name,
                )
            case _:
                raise ValueError("Invalid storage backend type")
        self.__path = path
        super().__init__(*args, **kwargs)
        self._fs_cached = path.fs

    @property
    def abstract_path(self):
        return super().path

    @property
    def path(self):
        # concatenate internal and external paths
        path = os.path.relpath(super().path, self.root)
        path = os.path.join(self.__path.path, path)
        return os.path.normpath(path)

    def __str__(self):
        # get the abstract path
        path = super().path
        if self._protocol:
            return f"{self._protocol}://{path}"
        else:
            return path


def copytree_path(source: Path, dest: Path):
    """Copy a file tree with Path compatibility. If 'dest' does not
    exist, it is created.

    :param source: dir to copy from (objet Path).
    :param dest: dir to copy to (objet Path).

    """

    dest.mkdir(parents=True, exist_ok=True)

    for item in source.iterdir():
        if item.is_dir():
            copytree_path(item, dest / item.name)
        else:
            with item.open('rb') as src_file:
                with (dest / item.name).open('wb') as dst_file:
                    dst_file.write(src_file.read())


register_implementation("resource", ResourcePath)

__all__ = [
    "ResourcePath",
    "UPath",
]
