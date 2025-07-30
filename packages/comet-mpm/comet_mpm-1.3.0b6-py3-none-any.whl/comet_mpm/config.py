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

import inspect
import os
from typing import Any, Optional


def find_page_name() -> Optional[str]:
    """
    This function searches the call stack to find the name of the calling
    Python Panel function. It depends on the name of the panel script.
    """
    stack = inspect.stack()
    for row in stack:
        frame, filename, line_number, function_name, lines, index = row
        basename = os.path.basename(filename)
        # NOTE: this is based on specific naming of the Python Panel files:
        if basename.startswith("edit_mpm_panel_") or basename.startswith("mpm_panel_"):
            return basename

    return None


def get_config(key: str) -> Any:
    """
    Get the key in the config. If it a Python Panel,
    it can try to get the key from the streamlit session
    state. Otherwise, it could try other means.
    """
    try:
        import streamlit as st
    except ImportError:
        # FIXME: get from environment
        return None

    page_name = find_page_name()
    if page_name is not None:
        state = st.session_state.get("comet_config_override", {})
        config = state.get(page_name, {})
        value = config.get(key, None)
        return value
    return None
