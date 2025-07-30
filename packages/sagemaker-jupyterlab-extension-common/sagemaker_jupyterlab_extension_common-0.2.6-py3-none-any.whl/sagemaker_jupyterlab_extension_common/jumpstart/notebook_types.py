from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class JumpStartBucketStage(Enum):
    PROD = ("prod",)
    BETA = ("beta",)
    ALPHA = ("alpha",)
    GAMMA = ("gamma",)
    SBX = ("sbx",)


class JumpStartModelNotebookAlterationType(Enum):
    modelIdVersion = "modelIdVersion"
    modelIdOnly = "modelIdOnly"
    dropModelSelection = "dropModelSelection"
    dropForDeploy = "dropForDeploy"
    dropForTraining = "dropForTraining"
    clusterId = "clusterId"
    clusterName = "clusterName"
    hyperPodStudio = "hyperPodStudio"
    hyperPodUnifiedStudio = "hyperPodUnifiedStudio"
    estimatorInitHubName = "jumpStartEstimatorInitOptionalHubName"
    modelInitHubName = "jumpStartModelInitOptionalHubName"
    getRecipePath = "getRecipePath"
    getExtractedRecipePath = "getExtractedRecipePath"
    novaTrainingJobNotebookHeaderMarkdown = "novaTrainingJobNotebookHeaderMarkdown"
    novaHyperpodNotebookHeaderMarkdown = "novaHyperpodNotebookHeaderMarkdown"
    fetchCodeCommitCredentials = "fetchCodeCommitCredentials"
    cloneRepository = "cloneRepository"


class JumpStartNotebookNames(Enum):
    infer = "inference"
    train = "training"


class JumpStartModelNotebookSubstitutionTarget(Enum):
    endpointName = "endpointName"
    inferenceComponentTarget = "inferenceComponentTarget"


class JumpStartResourceType(Enum):
    inferNotebook = "inferNotebook"
    modelSdkNotebook = "modelSdkNotebook"
    proprietaryNotebook = "proprietaryNotebook"
    default = "notebook"
    hyperpodNotebook = "hyperpodNotebook"
    novaNotebook = "novaNotebook"


class JumpStartModelNotebookGlobalActionType(Enum):
    dropAllMarkdown = "dropAllMarkdown"
    dropAllCode = "dropAllCode"


class JumpStartModelNotebookSubstitutionTarget(Enum):
    endpointName = "!!!name!!!"
    inferenceComponentBoto3 = "EndpointName=endpoint_name"
    inferenceComponentSdk = "(endpoint_name)"
    inferenceComponent = "!!!component_name!!!"


class JumpStartModelNotebookSuffix(Enum):
    modelSdkNotebook = "sdk"
    inferNotebook = "infer"
    proprietaryNotebook = "pp"


@dataclass
class JumpStartModelNotebookSubstitution:
    find: JumpStartModelNotebookSubstitutionTarget
    replace: str
    onlyOnce: bool


@dataclass
class JumpStartModelNotebookMetadataUpdateType:
    key: str
    value: Any


@dataclass
class UpdateHubNotebookUpdateOptions:
    substitutions: List[JumpStartModelNotebookSubstitution]
    alterations: List[JumpStartModelNotebookAlterationType]
    globalActions: List[JumpStartModelNotebookGlobalActionType]
    metadataUpdates: Optional[List[JumpStartModelNotebookMetadataUpdateType]] = field(
        default_factory=list
    )
