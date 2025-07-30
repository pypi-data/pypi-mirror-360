"""Executor template for custom executor."""
from typing import List

from ML_management.executor.base_executor import BaseExecutor
from ML_management.executor.patterns import OneModelPattern
from ML_management.executor.upload_model_mode import UploadModelMode
from ML_management.model.model_type_to_methods_map import ModelMethodName


class JobExecutorPattern(BaseExecutor):
    """DEPRECATED.

    Exists only for backward compatibility.
    Instead use BaseExecutor from ML_management.executor.base_executor.
    """

    def __init__(self, desired_model_methods: List[ModelMethodName], upload_model_mode: UploadModelMode) -> None:
        super().__init__(
            executor_models_pattern=OneModelPattern(
                upload_model_mode=upload_model_mode, desired_model_methods=desired_model_methods
            ),
        )
