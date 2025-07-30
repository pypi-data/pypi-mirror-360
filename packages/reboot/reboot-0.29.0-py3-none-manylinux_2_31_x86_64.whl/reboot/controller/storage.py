import os
from dataclasses import dataclass
from enum import Enum
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.deployments import UpdateStrategy
from kubernetes_utils.resources.persistent_volume_claims import AccessMode
from reboot.controller.settings import ENVVAR_REBOOT_STORAGE_TYPE
from rebootdev.aio.types import ApplicationId, ConsensusId

LOCAL_STORAGE_CLASS_NAME = "local"
EBS_STORAGE_CLASS_NAME = "ebs-gp3"
EFS_STORAGE_CLASS_NAME = "efs-shared"


class StorageType(Enum):
    LOCAL = 'LOCAL'
    AWS_EBS = 'AWS_EBS'
    AWS_EFS = 'AWS_EFS'


@dataclass
class MountInfo:
    pvc_name: str
    deployment_update_strategy: UpdateStrategy


async def _ensure_single_consensus_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    name: str,
    size: str,  # E.g. "10Gi".
    storage_class_name: str,
) -> MountInfo:
    await k8s_client.persistent_volume_claims.create_or_update(
        namespace=namespace,
        name=name,
        storage_class_name=storage_class_name,
        storage_request=size,
        access_modes=[AccessMode.READ_WRITE_ONCE],
    )
    return MountInfo(
        pvc_name=name,
        # Currently, Reboot applications can't be replaced in a graceful rolling
        # restart. They must be brought down first, before a replacement can be
        # brought back up. This will cause some downtime, particularly since the
        # old application doesn't terminate instantly.
        #
        # ISSUE(https://github.com/reboot-dev/mono/issues/4110): There are two
        # reasons we don't support rolling restarts:
        # * Because of the access mode we must delete the old pod before
        #   creating the new one.
        # * Even if we could multi-attach, the application would crash if it
        #   doesn't have the rocksdb lock.
        deployment_update_strategy=UpdateStrategy.RECREATE,
    )


async def _ensure_local_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    consensus_id: ConsensusId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    return await _ensure_single_consensus_persistent_volume_claim(
        k8s_client=k8s_client,
        namespace=namespace,
        name=consensus_id,
        size=size,
        storage_class_name=LOCAL_STORAGE_CLASS_NAME,
    )


async def _ensure_ebs_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    consensus_id: ConsensusId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    return await _ensure_single_consensus_persistent_volume_claim(
        k8s_client=k8s_client,
        namespace=namespace,
        name=consensus_id,
        size=size,
        storage_class_name=EBS_STORAGE_CLASS_NAME,
    )


async def _ensure_efs_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    await k8s_client.persistent_volume_claims.create_or_update(
        namespace=namespace,
        # Each application has one PersistentVolumeClaim that can be mounted by
        # many pods. Since Reboot consensuses create a subdirectory for
        # themselves they can all share the same folder.
        name=application_id,
        storage_class_name=EFS_STORAGE_CLASS_NAME,
        storage_request="1Ki",  # Storage request size is ignored by EFS.
        access_modes=[AccessMode.READ_WRITE_MANY],
    )
    return MountInfo(
        pvc_name=application_id,
        # Currently, Reboot applications can't be replaced in a graceful rolling
        # restart. They must be brought down first, before a replacement can be
        # brought back up. This will cause some downtime, particularly since the
        # old application doesn't terminate instantly.
        #
        # There reason we don't support rolling restarts is that the application
        # will crash if it doesn't have the rocksdb lock.
        #
        # TODO: when the above limitation has been addressed, switch to a
        #       rolling update for lower downtime:
        #         https://github.com/reboot-dev/mono/issues/4110
        deployment_update_strategy=UpdateStrategy.RECREATE,
    )


async def ensure_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    consensus_id: ConsensusId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    storage_type_str = os.environ.get(ENVVAR_REBOOT_STORAGE_TYPE)
    if storage_type_str is None:
        raise ValueError(
            f"Missing required environment variable '{ENVVAR_REBOOT_STORAGE_TYPE}'"
        )

    try:
        storage_type = StorageType[storage_type_str]
    except KeyError:
        raise ValueError(
            f"Invalid value '{storage_type_str}' for environment variable "
            f"'{ENVVAR_REBOOT_STORAGE_TYPE}'; supported values are: "
            f"{', '.join([storage_type.value for storage_type in StorageType])}"
        )

    match storage_type:
        case StorageType.LOCAL:
            return await _ensure_local_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                consensus_id=consensus_id,
                size=size,
            )
        case StorageType.AWS_EBS:
            return await _ensure_ebs_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                consensus_id=consensus_id,
                size=size,
            )
        case StorageType.AWS_EFS:
            return await _ensure_efs_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                application_id=application_id,
                size=size,
            )
        case _:
            raise AssertionError(f"Unhandled storage type '{storage_type}'")
