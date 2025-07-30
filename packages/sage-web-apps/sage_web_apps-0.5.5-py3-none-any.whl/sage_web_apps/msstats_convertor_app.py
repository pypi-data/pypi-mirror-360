import streamlit as st
import pandas as pd
import io
import base64
import os
from tempfile import NamedTemporaryFile
try:
    from .msstats_convertor import run_sage_lfq
except ImportError:
    from msstats_convertor import run_sage_lfq


def app():
    st.title("Sage LFQ to MSstats Format Converter")
    st.write(
        """
    This application converts Sage Label-Free Quantification (LFQ) data to the MSstats format 
    for differential expression analysis in proteomics studies.
    """
    )

    # File uploaders
    lfq_file = st.file_uploader(
        "Upload LFQ Data File (TSV, CSV, or Parquet)", type=["tsv", "csv", "parquet"]
    )
    annotation_file = st.file_uploader(
        "Upload Annotation File (TSV, CSV, or Excel)", type=["tsv", "csv", "xlsx"]
    )

    # Parameters
    col1, col2 = st.columns(2)

    with col1:
        qvalue = st.number_input(
            "Q-value cutoff",
            min_value=0.0,
            max_value=1.0,
            value=0.01,
            format="%.4f",
            help="Maximum q-value threshold for filtering results",
        )

        min_measurements = st.number_input(
            "Minimum measurements",
            min_value=0,
            value=1,
            help="Minimum number of non-zero measurements required for a peptide-charge pair",
        )

    with col2:
        min_protein_features = st.number_input(
            "Minimum protein features",
            min_value=0,
            value=1,
            help="Minimum number of peptides required for a protein to be included",
        )

        include_filter_cols = st.checkbox(
            "Include filter columns",
            value=True,
            help="Include intermediate filtering columns prefixed with '_' in the output",
        )

    require_unique_peptides = st.checkbox(
        "Unique peptides only",
        value=True,
        help="If checked, only unique peptides will be included in the output"
    )

    # Process button
    if st.button("Convert to MSstats Format") and lfq_file and annotation_file:
        try:
            # Show processing message
            with st.spinner("Processing..."):
                # Read LFQ file
                if lfq_file.name.endswith(".tsv"):
                    lfq_df = pd.read_csv(lfq_file, sep="\t")
                elif lfq_file.name.endswith(".csv"):
                    lfq_df = pd.read_csv(lfq_file)
                elif lfq_file.name.endswith(".parquet"):
                    # Save the uploaded parquet file to a temporary file
                    with NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
                        tmp.write(lfq_file.getvalue())
                        tmp_path = tmp.name
                    lfq_df = pd.read_parquet(tmp_path)
                    os.unlink(tmp_path)  # Delete the temporary file
                else:
                    st.error("LFQ file must be a TSV, CSV, or Parquet file.")
                    return

                # Read annotation file
                if annotation_file.name.endswith(".tsv"):
                    annotation_df = pd.read_csv(annotation_file, sep="\t")
                elif annotation_file.name.endswith(".csv"):
                    annotation_df = pd.read_csv(annotation_file)
                elif annotation_file.name.endswith(".xlsx"):
                    annotation_df = pd.read_excel(annotation_file)
                else:
                    st.error("Annotation file must be a TSV, CSV, or Excel file.")
                    return

                # Convert to MSstats format
                output_df = run_sage_lfq(
                    lfq_df=lfq_df,
                    annotation_df=annotation_df,
                    qvalue=qvalue,
                    min_measurments=min_measurements,
                    min_protein_features=min_protein_features,
                    include_filter_cols=include_filter_cols,
                    require_unique_peptides=require_unique_peptides,
                )

                # Create download button
                csv = output_df.to_csv(sep="\t", index=False)
                filename = "sage_lfq_msstats_format.tsv"
                st.download_button(
                    label="Download Converted Data",
                    data=csv,
                    file_name=filename,
                    mime="text/tab-separated-values",
                )

        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")


if __name__ == "__main__":
    app()

