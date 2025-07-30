# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021-2024 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
import logging

from .api_key.comet_api_key import parse_api_key
from .connection_helpers import get_root_url, sanitize_url
from .logging_messages import BASE_URL_MISMATCH_CONFIG_API_KEY
from .settings import MPMSettings

LOGGER = logging.getLogger(__name__)

DEFAULT_COMET_BASE_URL = "https://www.comet.com/"


def extract_comet_url(settings: MPMSettings) -> str:
    """Extracts Comet base url from settings or API key and sanitizes it (appends / at the end)"""
    api_key = parse_api_key(settings.api_key)
    if api_key is None:
        return DEFAULT_COMET_BASE_URL

    if settings.url is not None:
        settings_base_url = sanitize_url(get_root_url(str(settings.url)))
        if (
            api_key.base_url is not None
            and sanitize_url(api_key.base_url) != settings_base_url
        ):
            LOGGER.warning(
                BASE_URL_MISMATCH_CONFIG_API_KEY,
                settings_base_url,
                sanitize_url(api_key.base_url),
            )
        # do not change base url but add trailing slash if not there
        return sanitize_url(str(settings.url))

    if api_key.base_url is not None:
        return sanitize_url(api_key.base_url)

    return DEFAULT_COMET_BASE_URL
