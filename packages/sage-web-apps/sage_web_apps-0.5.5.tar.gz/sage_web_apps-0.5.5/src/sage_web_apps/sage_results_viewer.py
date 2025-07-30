from dataclasses import dataclass
import json
import os
from typing import Optional
import streamlit as st
import pandas as pd

from sage_web_apps.constants import SAGE_VERSIONS
from sage_web_apps.file_manager import SageFileManager
from sage_web_apps.pydantic_config import SageConfig


sage_search_path = st.text_input(
    "Enter the path to the Sage search results directory",
    value="",
    help="Enter the path to the directory where Sage search results are stored.",
)

if not os.path.exists(sage_search_path):
    st.error(f"Sage searches directory {sage_search_path} does not exist. Please run a Sage search first.")
    st.stop()

st.title("Sage Results Viewer")

@dataclass
class SearchResults:
    folder_path: str

    @property
    def results_path(self) -> Optional[str]:
        # Look for a file that starts with results.sage
        csv_path = 'results.sage.tsv'
        parquet_path = 'results.sage.parquet'
        if os.path.exists(os.path.join(self.folder_path, csv_path)):
            return os.path.join(self.folder_path, csv_path)
        elif os.path.exists(os.path.join(self.folder_path, parquet_path)):
            return os.path.join(self.folder_path, parquet_path)
        else:
            return None
        
    @property
    def results_sage_df(self) -> Optional[pd.DataFrame]:
        if self.results_path is None:
            return None
        if self.results_path.endswith('.tsv'):
            return pd.read_csv(self.results_path, sep='\t')
        elif self.results_path.endswith('.parquet'):
            return pd.read_parquet(self.results_path)
        else:
            return None
    
    @property
    def matched_fragments_path(self) -> Optional[str]:
        # Look for a file that
        csv_path = 'matched_fragments.sage.tsv'
        parquet_path = 'matched_fragments.sage.parquet'
        if os.path.exists(os.path.join(self.folder_path, csv_path)):
            return os.path.join(self.folder_path, csv_path)
        elif os.path.exists(os.path.join(self.folder_path, parquet_path)):
            return os.path.join(self.folder_path, parquet_path)
        else:
            return None
        
    @property
    def matched_fragments_sage_df(self) -> Optional[pd.DataFrame]:
        if self.matched_fragments_path is None:
            return None
        if self.matched_fragments_path.endswith('.tsv'):
            return pd.read_csv(self.matched_fragments_path, sep='\t')
        elif self.matched_fragments_path.endswith('.parquet'):
            return pd.read_parquet(self.matched_fragments_path)
        else:
            return None
        
    @property
    def log_path(self) -> Optional[str]:
        log_path = 'sage.log'
        if os.path.exists(os.path.join(self.folder_path, log_path)):
            return os.path.join(self.folder_path, log_path)
        else:
            return None
        
    @property
    def log_content(self) -> Optional[str]:
        if self.log_path is None:
            return None
        with open(self.log_path, 'r') as f:
            return f.read()
        
    @property
    def config_path(self) -> Optional[str]:
        config_path = 'results.json'
        if os.path.exists(os.path.join(self.folder_path, config_path)):
            return os.path.join(self.folder_path, config_path)
        else:
            return None
        
    @property
    def config_content(self) -> Optional[SageConfig]:
        if self.config_path is None:
            return None
        with open(self.config_path, 'r') as f:
            params = json.loads(f.read())
            return SageConfig.from_dict(params)
        
        
        
# show dataframes in tabs
sr = SearchResults(folder_path=sage_search_path)


stab, ftab, ltab, ctab = st.tabs(["Results", "Matched Fragments", "Log", "Configuration"])
with stab:
    st.subheader("Results")
    st.dataframe(sr.results_sage_df, height=600)
with ftab:
    st.subheader("Matched Fragments")
    st.dataframe(sr.matched_fragments_sage_df, height=600)
with ltab:
    st.subheader("Log")
    with st.container(height=600):
        st.code(sr.log_content)
with ctab:
    st.subheader("Configuration")
    with st.container(height=600):
        st.json(sr.config_content.to_dict())




    
