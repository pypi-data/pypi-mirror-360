import os
import pandas as pd
import streamlit as st
import json
from typing import Dict, List
import streamlit_permalink as stp

from sage_web_apps.streamlit_utils import get_config_params, load_preset

# if not set (running from community cloud = server mode)
is_local = os.getenv("LOCAL", "False") == "True"


is_local = st.toggle("Local Mode", value=is_local, help="Toggle local mode to use local Sage installation.")

def main():
    st.title("Sage Configuration Generator")

    working_dir = os.getcwd()
    params = get_config_params(is_local, working_dir, '.')
    
    # Convert params dict to SageConfig object for demonstration
    st.subheader("Configuration Structure (Dataclass)")
    with st.expander("View Configuration Structure"):
        st.info("""
        The configuration is now managed using dataclasses, which provides:
        - Type validation
        - Better code organization
        - Easier configuration manipulation
        - Self-documenting structure
        """)

if __name__ == "__main__":
    main()
