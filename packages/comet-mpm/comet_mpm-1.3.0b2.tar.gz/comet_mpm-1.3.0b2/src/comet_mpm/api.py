from typing import Dict, List, Optional
import os

from .client import Client
from .config import get_config

class Model:
    """
    Represents a Comet MPM model with methods for accessing model metrics and features.

    Args:
        client: The Comet MPM client instance
        workspace_name: Name of the workspace containing the model
        model_details: Dictionary containing model details from the API
    """

    def __init__(
        self,
        client: Client,
        workspace_name: str,
        model_details: Dict,
    ) -> None:
        """
        Initialize a Model instance.

        Args:
            client: The Comet MPM client instance
            workspace_name: Name of the workspace containing the model
            model_details: Dictionary containing model details from the API
        """
        self._client = client
        self.workspace_name = workspace_name
        # Unpack model details:
        self.id = model_details["modelId"]
        self.name = model_details["modelName"]
        self.created_at = model_details["createdAt"]
        self.latest_prediction = model_details["latestPrediction"]
        # FIXME: add all

    def get_metrics_by_sql(
        self, sql: str, is_time_series: bool, group_by: List[str]
    ) -> Dict:
        """
        Get custom metrics using SQL query.

        Args:
            sql: SQL query string
            is_time_series: Whether the metric is time-series data
            group_by: List of features to group by

        Returns:
            Dict: Metric results from the SQL query
        """
        response = self._client.get_metric_by_sql(
            self.id, sql, is_time_series, group_by
        )
        return response

    def get_metric_density(self, feature: str) -> Dict:
        """
        Get density distribution of a numerical feature.

        Args:
            feature: Name of the numerical feature

        Returns:
            Dict: Density distribution of the feature
        """
        response = self._client.get_metric_density(self.id, feature)
        return response

    def get_metric_drift(
        self,
        features: List[str],
        metric: str,
        is_time_series: bool,
        is_model_drift: bool,
    ) -> Dict:
        """
        Calculate drift metrics for model features.

        Args:
            features: List of features to calculate drift for
            metric: Name of the metric to calculate (EMD, PSI, KL)
            is_time_series: Whether to calculate time-series drift
            is_model_drift: Whether to calculate model-level drift

        Returns:
            Dict: Drift metrics for the specified features
        """
        response = self._client.get_metric_drift(
            self.id, features, metric, is_time_series, is_model_drift
        )
        return response


class API:
    """
    Main entry point for interacting with the Comet MPM API.

    Provides high-level methods for working with models and workspaces.
    Caches model information to reduce API calls.

    Args:
        api_key: The Comet API key for authentication
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Comet MPM API client.

        Args:
            api_key: The Comet API key for authentication
        """
        api_key = api_key if api_key is not None else get_config("comet.api_key") or os.environ.get("COMET_API_KEY")
        if api_key is None:
            raise Exception("COMET_API_KEY is not defined, and api_key is not given")

        self._client = Client(api_key)
        self._model_cache = {}

    def get_workspaces(self) -> List[str]:
        """
        Get a list of the workspace names that you belong to.
        """
        return self._client.get_workspaces()

    def get_model_names(self, workspace_name: str) -> List[str]:
        """
        Get list of model names in a workspace.

        This method also updates the internal model cache.

        Args:
            workspace_name: Name of the workspace to retrieve models from

        Returns:
            List[str]: List of model names in the workspace
        """
        models = self._client.get_models(workspace_name)
        names = []
        self._model_cache.clear()
        for model in models["models"]:
            model_name = model["modelName"]
            # Save in cache:
            self._model_cache[(workspace_name, model_name)] = model
            names.append(model_name)
        return names

    def get_model(self, workspace_name: Optional[str] = None, model_name: Optional[str] = None) -> Model:
        """
        Get a Model instance for the specified model.

        Args:
            workspace_name: Name of the workspace containing the model
            model_name: Name of the model to retrieve

        Returns:
            Model: Model instance with methods for accessing model metrics
        """
        if workspace_name is None:
            workspace_name = get_config("comet.workspace")
        if model_name is None:
            model_name = get_config("COMET_PANEL_OPTIONS")["modelName"]
        if not self._model_cache:
            # Fill the cache:
            self.get_model_names(workspace_name)

        model_data = self._model_cache[(workspace_name, model_name)]
        model_details = self._client.get_model(model_data["model_id"])

        return Model(
            client=self._client,
            workspace_name=workspace_name,
            model_details=model_details,
        )
