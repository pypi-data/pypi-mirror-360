# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021-2025 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import os
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .api_key.comet_api_key import parse_api_key
from .config import get_config
from .connection_helpers import get_root_url, sanitize_url


def get_comet_base_url(api_key: str) -> str:
    """
    Extracts Comet base URL from API key and sanitizes it (appends / at the end)

    Args:
        api_key: The Comet API key string

    Returns:
        str: Sanitized Comet base URL
    """
    api_key_parsed = parse_api_key(api_key)
    if api_key_parsed is not None and api_key_parsed.base_url is not None:
        return sanitize_url(api_key_parsed.base_url)
    else:
        return get_root_url(
            get_config("comet.url_override") or os.environ.get("COMET_URL_OVERRIDE")
        )


class Client:
    """
    A REST client for interacting with the Comet MPM API.

    This client provides methods for making HTTP requests to the Comet MPM API endpoints,
    including model management, feature search, and monitoring notifications.

    Args:
        api_key: The Comet API key for authentication
        retry_total: Total number of retries for failed requests (default: 3)
        status_codes: HTTP status codes to retry on (default: [429, 500, 502, 503, 504])
        backoff_factor: Wait time between retries (exponential backoff) (default: 1)
        raise_on_status: Whether to raise an exception on non-200 status codes (default: False)
    """

    def __init__(
        self,
        api_key: str,
        retry_total: int = 3,
        status_codes: Optional[List[int]] = None,
        backoff_factor: int = 1,
        raise_on_status: bool = False,
    ) -> None:
        """
        Initialize the Comet MPM REST client.

        Args:
            api_key: The Comet API key for authentication
            retry_total: Total number of retries for failed requests (default: 3)
            status_codes: HTTP status codes to retry on (default: [429, 500, 502, 503, 504])
            backoff_factor: Wait time between retries (exponential backoff) (default: 1)
            raise_on_status: Whether to raise an exception on non-200 status codes (default: False)
        """
        if status_codes is None:
            status_codes = [429, 500, 502, 503, 504]

        retry_strategy = Retry(
            total=retry_total,
            status_forcelist=status_codes,
            backoff_factor=backoff_factor,
            raise_on_status=raise_on_status,
        )

        self.adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)

        self.api_key = api_key
        self.base_url = get_comet_base_url(api_key)

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a GET request to the Comet MPM API.

        Args:
            endpoint: The API endpoint to request
            params: Optional query parameters for the request

        Returns:
            Dict: JSON response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        headers = {"Authorization": self.api_key, "Accept": "application/json"}
        response = self.session.get(url, headers=headers, params=params)
        return_data = response.json()
        return return_data

    def post(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a POST request to the Comet MPM API.

        Args:
            endpoint: The API endpoint to request
            params: Request body parameters

        Returns:
            Dict: JSON response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        headers = {"Authorization": self.api_key, "Accept": "application/json"}
        response = self.session.post(url, headers=headers, json=params)
        return_data = response.json()
        return return_data

    def get_model_details(self, model_id: str) -> Dict:
        """
        Get detailed information about a model.

        Args:
            model_id: ID of the model to retrieve details for

        Returns:
            Dict: Model details including ID, name, creation time, and latest prediction
        """
        endpoint = "api/mpm/v2/model/details"
        return self.get(endpoint, {"modelId": model_id})

    def search_features(self, include_metrics: bool = False) -> Dict:
        """
        Search for features in the model.

        Args:
            include_metrics: Whether to include metrics in the search results

        Returns:
            Dict: Search results including features and their metrics
        """
        endpoint = "api/mpm/v2/features/search"
        return self.get(endpoint, {"includeMetrics": include_metrics})

    def get_monitor_notifications(
        self, model_id: str, page: int = 1, page_size: int = 10
    ) -> Dict:
        """
        Get monitoring notifications for a model.

        Args:
            model_id: ID of the model to get notifications for
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 10)

        Returns:
            Dict: List of monitoring notifications
        """
        endpoint = "api/mpm/v2/monitor-notification"
        return self.get(
            endpoint,
            {"modelId": model_id, "page": page, "pageSize": page_size},
        )

    def search_models(
        self,
        workspace_id: str,
        predicates: Optional[List[Dict]] = None,
        page: int = 1,
        page_size: int = 1000,
    ) -> Dict:
        """
        Search for models in a workspace.

        Args:
            workspace_id: ID of the workspace to search in
            predicates: Optional search filters
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 1000)

        Returns:
            Dict: List of matching models
        """
        endpoint = "api/mpm/v2/model/search"
        params = {
            "workspaceId": workspace_id,
            "page": page,
            "pageSize": page_size,
            "predicates": [] if predicates is None else predicates,
        }
        return self.post(endpoint, params)

    def get_user_details(self) -> Dict:
        """
        Get details about the authenticated user.

        Returns:
            Dict: User account details
        """
        endpoint = "api/rest/v2/account-details"
        return self.get(endpoint)

    # v3 endpoints:

    # ROOT PATH api/mpm/v3

    def get_workspaces(self) -> List[str]:
        """
        Get list of available workspaces.

        Returns:
            List[str]: List of workspace names
        """
        endpoint = "api/mpm/v3/workspaces"
        response = self.get(endpoint)
        return [workspace["workspaceName"] for workspace in response["workspaces"]]

    def get_models(self, workspace_name: str) -> Dict:
        """
        Get list of models in a workspace.

        Args:
            workspace_name: Name of the workspace

        Returns:
            Dict: Workspace details including list of models with their IDs, names, creation times, and latest predictions
        """
        # FIXME: can you get a list of models?
        endpoint = f"api/mpm/v3/workspaces/{workspace_name}"
        response = self.get(endpoint)
        return response

    def get_sql_metrics(
        self,
        model_id: str,
        sql: str,
        start_date: str,
        end_date: str,
        interval_type: str,
        filters: Dict[str, str],
        model_version: Optional[str],
    ) -> Dict:
        """
        Get custom metrics using SQL query.

        Args:
            model_id: ID of the model
            sql: SQL query string, like
                SELECT F1("label_value", "prediction_value", "true") FROM MODEL
            is_time_series: Whether the metric is time-series data
            group_by: List of features to group by

        Returns:
            Dict: Metric results from the SQL query
        """
        endpoint = f"api/mpm/v3/model/{model_id}/metric/custom"
        params = {
            "cometSql": sql,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "dashboardFilters": filters,
            "versionFilter": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_feature_density(
        self,
        feature: str,
        model_id: str,
        start_date: str,
        end_date: str,
        interval_type: str,
        filters: Dict[str, str],
        model_version: Optional[str],
        source_type: str = "INPUT",
    ) -> Dict:
        """
        Get density distribution of a numerical feature.

        Args:
            feature: Name of the numerical feature
            source_type: "INPUT" or "OUTPUT"

        Returns:
            Dict: Density distribution of the feature
        """
        endpoint = f"api/mpm/v3/model/{model_id}/feature/metric/feature_density"
        params = {
            "featureName": feature,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "featureSourceType": source_type,
            "dashboardFilters": filters,
            "versionFilter": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_features_drift(
        self,
        features: List[str],
        model_id: str,
        start_date: str,
        end_date: str,
        interval_type: str,
        filters: Dict[str, str],
        model_version: Optional[str],
        source_type: str = "INPUT",
        algorithm: str = "EMD",
    ) -> Dict:
        """
        Calculate drift metrics for model features.

        Args:
            model_id: ID of the model
            features: List of features to calculate drift for

        Returns:
            Dict: Drift metrics for the specified features

        """
        endpoint = f"api/mpm/v3/model/{model_id}/metric/drift"
        params = {
            "inputFeatures": features,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "algorithmType": algorithm,
            "dashboardFilters": filters,
            "versionFilter": model_version,
        }
        response = self.post(endpoint, params)
        return response
