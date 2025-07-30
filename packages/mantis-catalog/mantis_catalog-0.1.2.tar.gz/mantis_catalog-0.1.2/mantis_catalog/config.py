# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2025 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
#
import enum
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Dict
from typing import Optional

from omegaconf import OmegaConf
from omegaconf import SI


class StorageType(enum.Enum):
    local = 1
    s3 = 2


@dataclass
class BaseStorageConfig:
    """Generic storage config dataclass"""


@dataclass
class LocalStorageConfig(BaseStorageConfig):
    path: Path = SI("${oc.env:CATALOG_STORAGE_LOCAL_PATH}")


@dataclass
class S3StorageConfig(BaseStorageConfig):
    access_key: Optional[str] = SI("${oc.env:CATALOG_STORAGE_S3_ACCESS_KEY,null}")
    secret_key: Optional[str] = SI("${oc.env:CATALOG_STORAGE_S3_SECRET_KEY,null}")
    endpoint_url: Optional[str] = SI("${oc.env:CATALOG_STORAGE_S3_ENDPOINT_URL,null}")
    bucket_name: str = "${oc.env:CATALOG_STORAGE_S3_BUCKET_NAME}"
    region: Optional[str] = SI("${oc.env:CATALOG_STORAGE_S3_REGION,null}")


@dataclass
class StorageConfig:
    """Generic storage config dataclass"""

    _backends: Dict[StorageType, BaseStorageConfig] = field(
        default_factory=lambda: {
            StorageType.local: LocalStorageConfig(),
            StorageType.s3: S3StorageConfig(),
        }
    )
    _type_name: str = "${.type}"
    backend: BaseStorageConfig = SI("${._backends[${._type_name}]}")
    type: StorageType = SI("${oc.env:CATALOG_STORAGE_TYPE,local}")
    path_prefix: str = "${oc.env:CATALOG_STORAGE_PATH_PREFIX,''}"


@dataclass
class CatalogConfig:
    storage: StorageConfig = field(default_factory=StorageConfig)


catalog_config = OmegaConf.structured(CatalogConfig)
