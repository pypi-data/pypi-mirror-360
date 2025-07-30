import os
import inspect

def find_page_name():
    stack = inspect.stack()
    for row in stack:
        frame, filename, line_number, function_name, lines, index = row
        basename = os.path.basename(filename)
        if basename.startswith("edit_mpm_panel_"):
            return basename

def get_config(key):
    try:
        import streamlit as st
    except ImportError:
        return None

    page_name = find_page_name()
    if page_name:
        state = st.session_state.get("comet_config_override", {})
        config = state.get(page_name, {})
        value = config.get(key, None)
        return value

