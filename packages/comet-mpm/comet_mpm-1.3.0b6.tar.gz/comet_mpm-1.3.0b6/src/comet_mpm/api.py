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

from .client import Client
from .config import get_config


class Model:
    def __init__(
        self, client: Client, model_id: str, panel_options: Optional[Dict] = None
    ):
        self._client = client
        self.model_id = model_id
        self.panel_options = panel_options

    def get_features_drift(
        self,
        features: List[str],
        source_type: str = "INPUT",
        algorithm: str = "EMD",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        model_version: Optional[str] = None,
    ) -> Dict:
        """
        Calculate drift metrics for model features.

        Args:
            model_id: ID of the model
            features: List of features to calculate drift for

        Returns:
            Dict: Drift metrics for the specified features

        """
        if self.panel_options is not None:
            if start_date is None:
                start_date = self.panel_options["startDate"]
            if end_date is None:
                end_date = self.panel_options["endDate"]
            if interval_type is None:
                interval_type = self.panel_options["intervalType"]
            if filters is None:
                filters = {
                    f"filter_{i + 1}": filter
                    for i, filter in enumerate(self.panel_options["filters"])
                }
            if model_version is None:
                model_version = self.panel_options["modelVersion"]

        data = self._client.get_features_drift(
            features=features,
            source_type=source_type,
            algorithm=algorithm,
            model_id=self.model_id,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            filters=filters,
            model_version=model_version,
        )
        return data

    def get_feature_density(
        self,
        feature: str,
        source_type: str = "INPUT",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        model_version: Optional[str] = None,
    ) -> Dict:
        """
        Get density distribution of a numerical feature.

        Args:
            feature: Name of the numerical feature
            source_type: "INPUT" or "OUTPUT"

        Returns:
            Dict: Density distribution of the feature
        """
        if self.panel_options is not None:
            if start_date is None:
                start_date = self.panel_options["startDate"]
            if end_date is None:
                end_date = self.panel_options["endDate"]
            if interval_type is None:
                interval_type = self.panel_options["intervalType"]
            if filters is None:
                filters = {
                    f"filter_{i + 1}": filter
                    for i, filter in enumerate(self.panel_options["filters"])
                }
            if model_version is None:
                model_version = self.panel_options["modelVersion"]

        data = self._client.get_feature_density(
            feature=feature,
            source_type=source_type,
            model_id=self.model_id,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            filters=filters,
            model_version=model_version,
        )
        return data

    def get_sql_metrics(
        self,
        sql: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        model_version: Optional[str] = None,
    ) -> Dict:
        if self.panel_options is not None:
            if start_date is None:
                start_date = self.panel_options["startDate"]
            if end_date is None:
                end_date = self.panel_options["endDate"]
            if interval_type is None:
                interval_type = self.panel_options["intervalType"]
            if filters is None:
                filters = {
                    f"filter_{i + 1}": filter
                    for i, filter in enumerate(self.panel_options["filters"])
                }
            if model_version is None:
                model_version = self.panel_options["modelVersion"]

        data = self._client.get_sql_metrics(
            model_id=self.model_id,
            sql=sql,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            filters=filters,
            model_version=model_version,
        )
        return data


class API:
    """
    Main entry point for interacting with the Comet MPM API.

    Provides high-level methods for working with models and workspaces.

    Args:
        api_key: The Comet API key for authentication
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Comet MPM API client.

        Args:
            api_key: The Comet API key for authentication
        """
        api_key = (
            api_key
            if api_key is not None
            else get_config("comet.api_key") or os.environ.get("COMET_API_KEY")
        )
        if api_key is None:
            raise Exception("COMET_API_KEY is not defined, and api_key is not given")

        self._client = Client(api_key)

    def get_panel_model(self):
        panel_options = get_config("COMET_PANEL_OPTIONS")
        return Model(
            client=self._client,
            model_id=panel_options["modelId"],
            panel_options=panel_options,
        )

    def get_workspaces(self) -> List[str]:
        """
        Get a list of the workspace names that you belong to.
        """
        return self._client.get_workspaces()
