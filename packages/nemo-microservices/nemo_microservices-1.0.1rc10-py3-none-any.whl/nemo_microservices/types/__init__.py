# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .model import Model as Model
from .score import Score as Score
from .shared import (
    Rails as Rails,
    Function as Function,
    ImageURL as ImageURL,
    LogProbs as LogProbs,
    JobStatus as JobStatus,
    ModelSpec as ModelSpec,
    Ownership as Ownership,
    UsageInfo as UsageInfo,
    ConfigData as ConfigData,
    InputRails as InputRails,
    PromptData as PromptData,
    RailsParam as RailsParam,
    TaskPrompt as TaskPrompt,
    TopLogprob as TopLogprob,
    VersionTag as VersionTag,
    ActionRails as ActionRails,
    DialogRails as DialogRails,
    Instruction as Instruction,
    OutputRails as OutputRails,
    DeltaMessage as DeltaMessage,
    FunctionCall as FunctionCall,
    ErrorResponse as ErrorResponse,
    ModelArtifact as ModelArtifact,
    ArtifactStatus as ArtifactStatus,
    ChoiceLogprobs as ChoiceLogprobs,
    DeleteResponse as DeleteResponse,
    FinetuningType as FinetuningType,
    GuardrailModel as GuardrailModel,
    ModelPrecision as ModelPrecision,
    PaginationData as PaginationData,
    RetrievalRails as RetrievalRails,
    APIEndpointData as APIEndpointData,
    ConfigDataParam as ConfigDataParam,
    GuardrailConfig as GuardrailConfig,
    InferenceParams as InferenceParams,
    MessageTemplate as MessageTemplate,
    RailsConfigData as RailsConfigData,
    ReasoningParams as ReasoningParams,
    ValidationError as ValidationError,
    AutoAlignOptions as AutoAlignOptions,
    GenericSortField as GenericSortField,
    SingleCallConfig as SingleCallConfig,
    APIEndpointFormat as APIEndpointFormat,
    BackendEngineType as BackendEngineType,
    ClavataRailConfig as ClavataRailConfig,
    FiddlerGuardrails as FiddlerGuardrails,
    ClavataRailOptions as ClavataRailOptions,
    InjectionDetection as InjectionDetection,
    LoraFinetuningData as LoraFinetuningData,
    PatronusRailConfig as PatronusRailConfig,
    PrivateAIDetection as PrivateAIDetection,
    UserMessagesConfig as UserMessagesConfig,
    AutoAlignRailConfig as AutoAlignRailConfig,
    ChoiceDeltaToolCall as ChoiceDeltaToolCall,
    HTTPValidationError as HTTPValidationError,
    GuardrailConfigParam as GuardrailConfigParam,
    RailsConfigDataParam as RailsConfigDataParam,
    ReasoningModelConfig as ReasoningModelConfig,
    ChatCompletionMessage as ChatCompletionMessage,
    PTuningFinetuningData as PTuningFinetuningData,
    FactCheckingRailConfig as FactCheckingRailConfig,
    PatronusEvaluateConfig as PatronusEvaluateConfig,
    SensitiveDataDetection as SensitiveDataDetection,
    ChoiceDeltaFunctionCall as ChoiceDeltaFunctionCall,
    PatronusRailConfigParam as PatronusRailConfigParam,
    CompletionResponseChoice as CompletionResponseChoice,
    JailbreakDetectionConfig as JailbreakDetectionConfig,
    PatronusEvaluateAPIParams as PatronusEvaluateAPIParams,
    PrivateAIDetectionOptions as PrivateAIDetectionOptions,
    ChatCompletionTokenLogprob as ChatCompletionTokenLogprob,
    OutputRailsStreamingConfig as OutputRailsStreamingConfig,
    ChoiceDeltaToolCallFunction as ChoiceDeltaToolCallFunction,
    PatronusEvaluateConfigParam as PatronusEvaluateConfigParam,
    ChatCompletionResponseChoice as ChatCompletionResponseChoice,
    ChatCompletionMessageToolCall as ChatCompletionMessageToolCall,
    SensitiveDataDetectionOptions as SensitiveDataDetectionOptions,
    ChatCompletionToolMessageParam as ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam as ChatCompletionUserMessageParam,
    CompletionResponseStreamChoice as CompletionResponseStreamChoice,
    ChatCompletionSystemMessageParam as ChatCompletionSystemMessageParam,
    ParameterEfficientFinetuningData as ParameterEfficientFinetuningData,
    PatronusEvaluationSuccessStrategy as PatronusEvaluationSuccessStrategy,
    ChatCompletionContentPartTextParam as ChatCompletionContentPartTextParam,
    ChatCompletionFunctionMessageParam as ChatCompletionFunctionMessageParam,
    ChatCompletionMessageToolCallParam as ChatCompletionMessageToolCallParam,
    ChatCompletionResponseStreamChoice as ChatCompletionResponseStreamChoice,
    ChatCompletionAssistantMessageParam as ChatCompletionAssistantMessageParam,
    ChatCompletionContentPartImageParam as ChatCompletionContentPartImageParam,
)
from .dataset import Dataset as Dataset
from .project import Project as Project
from .model_de import ModelDe as ModelDe
from .model_ev import ModelEv as ModelEv
from .embedding import Embedding as Embedding
from .namespace import Namespace as Namespace
from .dataset_ev import DatasetEv as DatasetEv
from .rag_target import RagTarget as RagTarget
from .toleration import Toleration as Toleration
from .model_param import ModelParam as ModelParam
from .models_page import ModelsPage as ModelsPage
from .rail_status import RailStatus as RailStatus
from .score_param import ScoreParam as ScoreParam
from .score_stats import ScoreStats as ScoreStats
from .status_enum import StatusEnum as StatusEnum
from .target_type import TargetType as TargetType
from .task_config import TaskConfig as TaskConfig
from .task_result import TaskResult as TaskResult
from .task_status import TaskStatus as TaskStatus
from .group_config import GroupConfig as GroupConfig
from .group_result import GroupResult as GroupResult
from .model_filter import ModelFilter as ModelFilter
from .datasets_page import DatasetsPage as DatasetsPage
from .llm_call_info import LlmCallInfo as LlmCallInfo
from .metric_config import MetricConfig as MetricConfig
from .metric_result import MetricResult as MetricResult
from .model_spec_de import ModelSpecDe as ModelSpecDe
from .node_affinity import NodeAffinity as NodeAffinity
from .node_selector import NodeSelector as NodeSelector
from .projects_page import ProjectsPage as ProjectsPage
from .target_status import TargetStatus as TargetStatus
from .training_type import TrainingType as TrainingType
from .activated_rail import ActivatedRail as ActivatedRail
from .dataset_filter import DatasetFilter as DatasetFilter
from .generation_log import GenerationLog as GenerationLog
from .model_de_param import ModelDeParam as ModelDeParam
from .model_ev_param import ModelEvParam as ModelEvParam
from .project_filter import ProjectFilter as ProjectFilter
from .prompt_data_de import PromptDataDe as PromptDataDe
from .executed_action import ExecutedAction as ExecutedAction
from .guardrails_data import GuardrailsData as GuardrailsData
from .live_evaluation import LiveEvaluation as LiveEvaluation
from .namespaces_page import NamespacesPage as NamespacesPage
from .dataset_ev_param import DatasetEvParam as DatasetEvParam
from .date_time_filter import DateTimeFilter as DateTimeFilter
from .generation_stats import GenerationStats as GenerationStats
from .model_sort_field import ModelSortField as ModelSortField
from .rag_target_param import RagTargetParam as RagTargetParam
from .retriever_target import RetrieverTarget as RetrieverTarget
from .toleration_param import TolerationParam as TolerationParam
from .base_model_filter import BaseModelFilter as BaseModelFilter
from .created_at_filter import CreatedAtFilter as CreatedAtFilter
from .deployment_config import DeploymentConfig as DeploymentConfig
from .evaluation_config import EvaluationConfig as EvaluationConfig
from .evaluation_params import EvaluationParams as EvaluationParams
from .evaluation_result import EvaluationResult as EvaluationResult
from .evaluation_target import EvaluationTarget as EvaluationTarget
from .model_artifact_de import ModelArtifactDe as ModelArtifactDe
from .model_list_params import ModelListParams as ModelListParams
from .model_peft_filter import ModelPeftFilter as ModelPeftFilter
from .rag_pipeline_data import RagPipelineData as RagPipelineData
from .score_stats_param import ScoreStatsParam as ScoreStatsParam
from .task_config_param import TaskConfigParam as TaskConfigParam
from .training_pod_spec import TrainingPodSpec as TrainingPodSpec
from .artifact_status_de import ArtifactStatusDe as ArtifactStatusDe
from .dataset_sort_field import DatasetSortField as DatasetSortField
from .finetuning_type_de import FinetuningTypeDe as FinetuningTypeDe
from .group_config_param import GroupConfigParam as GroupConfigParam
from .model_filter_param import ModelFilterParam as ModelFilterParam
from .model_precision_de import ModelPrecisionDe as ModelPrecisionDe
from .node_selector_term import NodeSelectorTerm as NodeSelectorTerm
from .project_sort_field import ProjectSortField as ProjectSortField
from .cached_outputs_data import CachedOutputsData as CachedOutputsData
from .completion_response import CompletionResponse as CompletionResponse
from .dataset_list_params import DatasetListParams as DatasetListParams
from .guardrail_config_de import GuardrailConfigDe as GuardrailConfigDe
from .label_selector_term import LabelSelectorTerm as LabelSelectorTerm
from .metric_config_param import MetricConfigParam as MetricConfigParam
from .model_create_params import ModelCreateParams as ModelCreateParams
from .model_spec_de_param import ModelSpecDeParam as ModelSpecDeParam
from .model_update_params import ModelUpdateParams as ModelUpdateParams
from .node_affinity_param import NodeAffinityParam as NodeAffinityParam
from .node_selector_param import NodeSelectorParam as NodeSelectorParam
from .project_list_params import ProjectListParams as ProjectListParams
from .customization_config import CustomizationConfig as CustomizationConfig
from .customization_target import CustomizationTarget as CustomizationTarget
from .dataset_filter_param import DatasetFilterParam as DatasetFilterParam
from .project_filter_param import ProjectFilterParam as ProjectFilterParam
from .prompt_data_de_param import PromptDataDeParam as PromptDataDeParam
from .dataset_create_params import DatasetCreateParams as DatasetCreateParams
from .dataset_update_params import DatasetUpdateParams as DatasetUpdateParams
from .guardrails_data_param import GuardrailsDataParam as GuardrailsDataParam
from .namespace_list_params import NamespaceListParams as NamespaceListParams
from .nim_deployment_config import NIMDeploymentConfig as NIMDeploymentConfig
from .project_create_params import ProjectCreateParams as ProjectCreateParams
from .project_update_params import ProjectUpdateParams as ProjectUpdateParams
from .backend_engine_type_de import BackendEngineTypeDe as BackendEngineTypeDe
from .date_time_filter_param import DateTimeFilterParam as DateTimeFilterParam
from .evaluation_live_params import EvaluationLiveParams as EvaluationLiveParams
from .guardrail_check_params import GuardrailCheckParams as GuardrailCheckParams
from .retriever_target_param import RetrieverTargetParam as RetrieverTargetParam
from .base_model_filter_param import BaseModelFilterParam as BaseModelFilterParam
from .created_at_filter_param import CreatedAtFilterParam as CreatedAtFilterParam
from .deployment_config_param import DeploymentConfigParam as DeploymentConfigParam
from .embedding_create_params import EmbeddingCreateParams as EmbeddingCreateParams
from .evaluation_config_param import EvaluationConfigParam as EvaluationConfigParam
from .evaluation_params_param import EvaluationParamsParam as EvaluationParamsParam
from .evaluation_target_param import EvaluationTargetParam as EvaluationTargetParam
from .model_artifact_de_param import ModelArtifactDeParam as ModelArtifactDeParam
from .model_peft_filter_param import ModelPeftFilterParam as ModelPeftFilterParam
from .namespace_create_params import NamespaceCreateParams as NamespaceCreateParams
from .namespace_update_params import NamespaceUpdateParams as NamespaceUpdateParams
from .rag_pipeline_data_param import RagPipelineDataParam as RagPipelineDataParam
from .retriever_pipeline_data import RetrieverPipelineData as RetrieverPipelineData
from .training_pod_spec_param import TrainingPodSpecParam as TrainingPodSpecParam
from .completion_create_params import CompletionCreateParams as CompletionCreateParams
from .evaluation_config_filter import EvaluationConfigFilter as EvaluationConfigFilter
from .evaluation_target_filter import EvaluationTargetFilter as EvaluationTargetFilter
from .external_endpoint_config import ExternalEndpointConfig as ExternalEndpointConfig
from .generation_options_param import GenerationOptionsParam as GenerationOptionsParam
from .guardrail_check_response import GuardrailCheckResponse as GuardrailCheckResponse
from .node_selector_term_param import NodeSelectorTermParam as NodeSelectorTermParam
from .cached_outputs_data_param import CachedOutputsDataParam as CachedOutputsDataParam
from .create_embedding_response import CreateEmbeddingResponse as CreateEmbeddingResponse
from .evaluation_status_details import EvaluationStatusDetails as EvaluationStatusDetails
from .guardrail_config_de_param import GuardrailConfigDeParam as GuardrailConfigDeParam
from .label_selector_term_param import LabelSelectorTermParam as LabelSelectorTermParam
from .preferred_scheduling_term import PreferredSchedulingTerm as PreferredSchedulingTerm
from .completion_stream_response import CompletionStreamResponse as CompletionStreamResponse
from .customization_config_param import CustomizationConfigParam as CustomizationConfigParam
from .customization_target_param import CustomizationTargetParam as CustomizationTargetParam
from .label_selector_requirement import LabelSelectorRequirement as LabelSelectorRequirement
from .nim_deployment_config_param import NIMDeploymentConfigParam as NIMDeploymentConfigParam
from .generation_log_options_param import GenerationLogOptionsParam as GenerationLogOptionsParam
from .customization_training_option import CustomizationTrainingOption as CustomizationTrainingOption
from .retriever_pipeline_data_param import RetrieverPipelineDataParam as RetrieverPipelineDataParam
from .evaluation_config_filter_param import EvaluationConfigFilterParam as EvaluationConfigFilterParam
from .evaluation_target_filter_param import EvaluationTargetFilterParam as EvaluationTargetFilterParam
from .external_endpoint_config_param import ExternalEndpointConfigParam as ExternalEndpointConfigParam
from .generation_rails_options_param import GenerationRailsOptionsParam as GenerationRailsOptionsParam
from .evaluation_status_details_param import EvaluationStatusDetailsParam as EvaluationStatusDetailsParam
from .preferred_scheduling_term_param import PreferredSchedulingTermParam as PreferredSchedulingTermParam
from .label_selector_requirement_param import LabelSelectorRequirementParam as LabelSelectorRequirementParam
from .customization_training_option_param import CustomizationTrainingOptionParam as CustomizationTrainingOptionParam
from .parameter_efficient_finetuning_data_de import (
    ParameterEfficientFinetuningDataDe as ParameterEfficientFinetuningDataDe,
)
from .parameter_efficient_finetuning_data_de_param import (
    ParameterEfficientFinetuningDataDeParam as ParameterEfficientFinetuningDataDeParam,
)
