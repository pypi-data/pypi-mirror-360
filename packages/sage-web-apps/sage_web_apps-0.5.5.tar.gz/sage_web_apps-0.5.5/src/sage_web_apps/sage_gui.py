import json
import streamlit as st
from sage_web_apps.constants import SAGE_VERSIONS
from sage_web_apps.file_manager import SageFileManager, SearchStatus
import os
import datetime
import psutil

from sage_web_apps.streamlit_utils import download_show_config, get_config_params, load_preset
from sage_web_apps.utils import verify_params
import streamlit_notify as stn

st.title("Sage GUI")

stn.notify_all()

# load version from environment variable or default to latest version
VERSION = os.getenv("SAGE_VERSION", SAGE_VERSIONS[0])
MAX_WORKERS = os.getenv("MAX_WORKERS", 1)

@st.cache_resource
def get_sage_config_manager(VERSION, sage_executable, max_workers):
    return SageFileManager(VERSION, executable_path=sage_executable, max_workers=max_workers)

def get_cpu_usage():
    """Get current CPU usage percentage"""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Get current memory usage percentage and details"""
    memory = psutil.virtual_memory()
    return memory.percent, memory.used, memory.total

sage_file_manager = get_sage_config_manager(VERSION, None, MAX_WORKERS)
output_dir = sage_file_manager.results_directory_path


st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 600px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    

    @st.fragment(run_every="5s")
    def display():


        # Resource monitoring section
        st.header("System Resources")
        with st.container(border=True):
            # CPU Usage
            cpu_percent = get_cpu_usage()
            st.write("**CPU Usage**")
            st.progress(cpu_percent / 100, text=f"{cpu_percent:.1f}%")
            
            # Memory Usage
            memory_percent, memory_used, memory_total = get_memory_usage()
            st.write("**Memory Usage**")
            st.progress(memory_percent / 100, text=f"{memory_percent:.1f}%")
            
            # Memory details
            memory_used_gb = memory_used / (1024**3)
            memory_total_gb = memory_total / (1024**3)
            st.caption(f"{memory_used_gb:.1f} GB / {memory_total_gb:.1f} GB")

        # Job monitoring section
        st.header("Job Monitor")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Refresh", use_container_width=True):
                    st.rerun()
            
            with col2:
                if st.button("Clear Completed", use_container_width=True):
                    cleared_count = sage_file_manager.clear_completed_jobs()
                    if cleared_count > 0:
                        st.success(f"Cleared {cleared_count} completed jobs")
                    else:
                        st.info("No completed jobs to clear")
                    st.rerun()
            
            with col3:
                if st.button("Cancel All", use_container_width=True):
                    jobs = sage_file_manager.get_all_jobs()
                    cancelled_count = 0
                    for job_id in jobs:
                        if sage_file_manager.cancel_job(job_id):
                            cancelled_count += 1
                    if cancelled_count > 0:
                        st.warning(f"Cancelled {cancelled_count} jobs")
                    else:
                        st.info("No jobs to cancel")
                    st.rerun()
            
            # Display jobs
            jobs = sage_file_manager.get_all_jobs()
            
            if not jobs:
                st.info("No jobs submitted yet")
            else:
                for job_id, job in jobs.items():
                    status_color = {
                        SearchStatus.QUEUED: "🟡",
                        SearchStatus.RUNNING: "🔵", 
                        SearchStatus.COMPLETED: "🟢",
                        SearchStatus.FAILED: "🔴"
                    }.get(job.status, "⚪")
                    
                    with st.expander(f"{status_color} Job {job_id[:8]}... - {job.status.value.title()}", expanded=job.status == SearchStatus.RUNNING):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Status:** {job.status.value.title()}")
                            st.write(f"**Created:** {datetime.datetime.fromtimestamp(job.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            if job.started_at:
                                st.write(f"**Started:** {datetime.datetime.fromtimestamp(job.started_at).strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            if job.completed_at:
                                st.write(f"**Completed:** {datetime.datetime.fromtimestamp(job.completed_at).strftime('%Y-%m-%d %H:%M:%S')}")
                                duration = job.completed_at - (job.started_at or job.created_at)
                                st.write(f"**Duration:** {duration:.1f} seconds")
                            
                            if job.error_message:
                                st.error(f"**Error:** {job.error_message}")
                            
                            st.write(f"**Output Path:** {job.output_path}")
                            st.write(f"**Output Type:** {job.output_type}")
                            st.write(f"**Fragment Annotations:** {'Yes' if job.include_fragment_annotations else 'No'}")
                        
                        with col2:
                            if job.status in [SearchStatus.QUEUED, SearchStatus.RUNNING]:
                                if st.button(f"Cancel", key=f"cancel_{job_id}", use_container_width=True):
                                    if sage_file_manager.cancel_job(job_id):
                                        st.success("Job cancelled")
                                        st.rerun()
                                    else:
                                        st.error("Failed to cancel job")
                            
                            if job.status == SearchStatus.COMPLETED and os.path.exists(job.output_path):
                                if st.button(f"View Results", key=f"view_{job_id}", use_container_width=True):
                                    st.write("**Results Directory:**")
                                    try:
                                        files = os.listdir(job.output_path)
                                        for file in sorted(files):
                                            st.write(f"• {file}")
                                    except Exception as e:
                                        st.error(f"Error reading results: {e}")

    display()

params = get_config_params(True, os.getcwd(), output_dir)

if params is None:
    st.error("Failed to load configuration parameters.")
    #st.stop()

are_params_valid = False
try:
    verify_params(params)
    are_params_valid = True
except ValueError as e:
    st.error(f"Parameter verification failed: {str(e)}")

with st.container(border = True):

    c1, c2 = st.columns(2, vertical_alignment="bottom")
    with c1:
        output_type = st.selectbox(
            "Output Type",
            options=["tsv", "parquet"],
            index=1,  # Default to 'tsv'
            help="Select the output file format.",
        )

    with c2:
        include_fragment_annotations = st.checkbox(
            "Include Fragment Annotations",
            value=True,
            help="Whether to include fragment annotations in the output.",
        )

    if st.checkbox("Add Date/Time to Output Directory", 
                    value=True, 
                    help="Whether to append the current date and time to the output directory name."):
        # update the output directory with current date and time
        date_str = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '-').replace('.', '-')
        params['output_directory'] = f"{params['output_directory']}_{date_str}"

    sage_file_manager.setup_sage_search()

    if not sage_file_manager.sage_executable_path:
        st.error("Sage executable path is not set. Please provide a valid path to the Sage executable.")

    if not sage_file_manager.search_valid:
        st.error("Sage search setup is not valid. Please check the Sage executable path and configuration parameters.")

    if st.button("Run Sage", disabled=are_params_valid==False or sage_file_manager.search_valid==False, use_container_width=True):
        # def run_search(self, json_path: str, output_path: str, include_fragment_annotations: bool = True, output_type: str = "csv"):

        st.caption("Output path")
        st.code(params["output_directory"], language="plaintext")
        
        job_id = sage_file_manager.submit_search(
            params=params,
            output_path=params["output_directory"],
            include_fragment_annotations=include_fragment_annotations,
            output_type=output_type,
        )

        stn.toast(f"Sage job submitted successfully! Job ID: {job_id[:8]}...")
        st.rerun()


