import argparse
import os
import sys
import subprocess
import signal


def run_streamlit_app(module_path):
    """Helper function to run a Streamlit app from a module path."""
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct absolute path if relative
    if not os.path.isabs(module_path):
        module_path = os.path.join(current_dir, module_path)

    # Run streamlit command
    cmd = [sys.executable, "-m", "streamlit", "run", module_path]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)


def run_input_app():
    try:
        # arg parse to get local
        parser = argparse.ArgumentParser(description="Run the Sage input app.")
        parser.add_argument(
            "--server",
            action="store_true",
            help="Run the app in server mode (default: False)",
        )

        args = parser.parse_args()
        if args.server:
            os.environ["LOCAL"] = "False"
        else:
            # set env local to true if not set (running cli command)
            os.environ["LOCAL"] = "True"

        """Run the sage_input_app.py streamlit application."""
        app_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sage_input_app.py"
        )
        run_streamlit_app(app_path)
    except KeyboardInterrupt:
        print("\n\nShutting down Sage input app gracefully...")
        sys.exit(0)


def run_sage_app():
    try:
        parser = argparse.ArgumentParser(description="Run the Sage app.")
        parser.add_argument(
            "--server",
            action="store_true",
            help="Run the app in server mode (default: False)",
        )

        args = parser.parse_args()
        if args.server:
            os.environ["LOCAL"] = "False"
        else:
            # set env local to true if not set (running cli command)
            os.environ["LOCAL"] = "True"

        """Run the sage_app.py streamlit application."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_app.py")
        run_streamlit_app(app_path)
    except KeyboardInterrupt:
        print("\n\nShutting down Sage app gracefully...")
        sys.exit(0)

def run_sage_gui():
    try:
        parser = argparse.ArgumentParser(description="Run the Sage GUI.")

        """Run the sage_app.py streamlit application."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_gui.py")
        run_streamlit_app(app_path)
    except KeyboardInterrupt:
        print("\n\nShutting down Sage GUI gracefully...")
        sys.exit(0)


def run_msstats_app():
    try:
        parser = argparse.ArgumentParser(description="Run the MSstats converter app.")
        parser.add_argument(
            "--server",
            action="store_true",
            help="Run the app in server mode (default: False)",
        )

        args = parser.parse_args()
        if args.server:
            os.environ["LOCAL"] = "False"
        else:
            # set env local to true if not set (running cli command)
            os.environ["LOCAL"] = "True"

        """Run the msstats_convertor_app.py streamlit application."""
        app_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "msstats_convertor_app.py"
        )
        run_streamlit_app(app_path)
    except KeyboardInterrupt:
        print("\n\nShutting down MSstats app gracefully...")
        sys.exit(0)


def run_sage_vis():
    try:
        parser = argparse.ArgumentParser(description="Run the Sage Results Viewer app.")
        parser.add_argument(
            "--server",
            action="store_true",
            help="Run the app in server mode (default: False)",
        )

        args = parser.parse_args()
        if args.server:
            os.environ["LOCAL"] = "False"
        else:
            # set env local to true if not set (running cli command)
            os.environ["LOCAL"] = "True"

        """Run the sage_results_viewer.py streamlit application."""
        app_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sage_results_viewer.py"
        )
        run_streamlit_app(app_path)
    except KeyboardInterrupt:
        print("\n\nShutting down Sage Results Viewer gracefully...")
        sys.exit(0)

if __name__ == "__main__":
    # If script is run directly, show help
    print("This module provides functions to run Sage Streamlit apps.")
    print(
        "Use 'sage-app', 'sage-input-app', or 'sage-msstats-app' CLI commands to run the apps."
    )
