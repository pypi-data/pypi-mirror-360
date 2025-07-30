from typing import Dict, Optional, Tuple
import pandas as pd
import argparse
import warnings


def run_sage_lfq(
    lfq_df: pd.DataFrame,
    annotation_df: Optional[pd.DataFrame] = None,
    qvalue: float = 0.01,
    min_measurments: int = 1,
    min_protein_features: int = 1,
    include_filter_cols: bool = True,
    require_unique_peptides: bool = True,
) -> pd.DataFrame:
    """
    Converts Sage LFQ (Label-Free Quantification) data to MSstats format for differential expression analysis.
    This function processes raw LFQ data, applies filtering criteria, and reformats it to be compatible
    with MSstats software for statistical analysis of proteomics data.
    Parameters
    ----------
    lfq_df : str or pandas.DataFrame
        The input dataframe containing LFQ data with peptide measurements across multiple runs.
        Expected columns include 'peptide', 'proteins', 'charge', 'score', 'spectral_angle', 'q_value',
        and one column per experimental run.
    annotation_df : str or pandas.DataFrame
        Annotation dataframe that maps run IDs to conditions, biological replicates, and outlier status.
        Should contain 'Run', 'Condition', 'BioReplicate' columns, and optionally 'Outlier'.
        Can be None, which will result in empty mappings.
    qvalue : float, optional
        Maximum q-value threshold for filtering results. Default is 0.01.
    min_measurments : int, optional
        Minimum number of non-zero measurements required for a peptide-charge pair across all runs. Default is 1.
    min_protein_features : int, optional
        Minimum number of peptides required for a protein to be included. Default is 1.
    include_filter_cols : bool, optional
        If True, includes intermediate filtering columns (prefixed with '_') in the output. Default is True.
    Returns
    -------
    pandas.DataFrame
        A processed dataframe in MSstats format with the following columns:
        - ProteinName: Protein identifier
        - PeptideSequence: Amino acid sequence of the peptide
        - PrecursorCharge: Charge state of the precursor ion
        - FragmentIon: Set to 'p' for all rows
        - ProductCharge: Same as PrecursorCharge
        - IsotopeLabelType: Set to 'Light' for all rows
        - Condition: Experimental condition from annotation
        - BioReplicate: Biological replicate identifier from annotation
        - Run: Experimental run identifier
        - Intensity: Measured peptide intensity
        - Fraction: Set to 1 for all rows
        - Additional filtering columns (if include_filter_cols=True)
    Notes
    -----
    The function applies several filters to improve data quality:
    1. Filters by q-value threshold
    2. Filters proteins with insufficient peptide evidence
    3. Filters peptides with insufficient measurements across runs
    """

    # count the number of peptides for proteins col using a dictionary
    proteins_to_count: Dict[str, int] = lfq_df.groupby("proteins")["peptide"].size().to_dict() # type: ignore

    run_to_condition: Optional[Dict[str, str]] = None
    run_to_biorep: Optional[Dict[str, str]] = None
    run_to_isotope: Optional[Dict[str, str]] = None
    run_to_fraction: Optional[Dict[str, str]] = None

    if annotation_df is not None:

        if "Run" not in annotation_df.columns:
            raise ValueError("Annotation file must contain 'Run' column.")

        if "Condition" in annotation_df.columns:
            run_to_condition = annotation_df.set_index("Run")["Condition"].to_dict() # type: ignore
        else:
            warnings.warn(
                "Annotation file should contain 'Condition' column. Condition will be set to '1' for all runs."
            )

        if "BioReplicate" in annotation_df.columns:
            run_to_biorep = annotation_df.set_index("Run")["BioReplicate"].to_dict() # type: ignore
        else:
            warnings.warn(
                "Annotation file should contain 'BioReplicate' column. BioReplicate will be set to '1' for all runs."
            )

        if "IsotopeLabelType" in annotation_df.columns:
            run_to_isotope = annotation_df.set_index("Run")["IsotopeLabelType"].to_dict() # type: ignore
        else:
            warnings.warn(
                "Annotation file should contain 'IsotopeLabelType' column. IsotopeLabelType will be set to 'L' for all runs."
            )

        if "Fraction" in annotation_df.columns:
            run_to_fraction = annotation_df.set_index("Run")["Fraction"].to_dict() # type: ignore
        else:
            warnings.warn(
                "Annotation file should contain 'Fraction' column. Fraction will be set to '1' for all runs."
            )

    else:
        # If no annotation file, create empty mappings and warn
        warnings.warn(
            "No annotation file provided. Condition, BioReplicate, IsotopeLabelType, and Fraction will be set to '1' for all runs."
        )

    # convert lfq_df to row based df, currently it has cols for each exp
    lfq_cols = lfq_df.columns.tolist()

    # remove charge, peptide, proteins, q_value,  score and spectral_angle
    id_vars = ["peptide", "proteins", "charge", "score", "spectral_angle", "q_value"]

    for col in id_vars:
        if col in lfq_cols:
            lfq_cols.remove(col)

    # Count the number of non-zero and non-NaN values for each peptide-charge pair
    peptide_charge_counts: Dict[Tuple[str, int], int] = {}
    for _, row in lfq_df.iterrows(): 
        key: Tuple[str, int] = (str(row["peptide"]), int(row["charge"]))
        non_zero_count = sum((pd.notna(row[col]) and row[col] != 0) for col in lfq_cols)
        peptide_charge_counts[key] = non_zero_count

    # melt on remaining columns
    result_df = lfq_df.melt(
        id_vars=id_vars, value_vars=lfq_cols, var_name="Run", value_name="Intensity"
    )

    # rename proteins to ProteinName, peptide to PeptideSequence
    result_df.rename(
        columns={
            "proteins": "ProteinName",
            "peptide": "PeptideSequence",
            "charge": "PrecursorCharge",
            "q_value": "_q_value",
            "score": "_score",
            "spectral_angle": "_spectral_angle",
        },
        inplace=True,
    )
    result_df["FragmentIon"] = "p"
    result_df["ProductCharge"] = result_df["PrecursorCharge"]

    if run_to_isotope is None:
        result_df["IsotopeLabelType"] = 'L'
    else:
        result_df["IsotopeLabelType"] = result_df["Run"].map(run_to_isotope)

    iso_type_nan_count = result_df["IsotopeLabelType"].isna().sum()
    if iso_type_nan_count > 0:
        warnings.warn(
            f"{iso_type_nan_count} rows have NA for IsotopeLabelType. Ensure your annotation file contains this column."
        )

    if run_to_condition is None:
        result_df["Condition"] = 1
    else:
        result_df["Condition"] = result_df["Run"].map(run_to_condition)

    condition_nan_count = result_df["Condition"].isna().sum()
    if condition_nan_count > 0:
        warnings.warn(
            f"{condition_nan_count} rows have NA for Condition. Ensure your annotation file contains this column."
        )

    if run_to_biorep is None:
        result_df["BioReplicate"] = 1
    else:
        result_df["BioReplicate"] = result_df["Run"].map(run_to_biorep)

    biorep_nan_count = result_df["BioReplicate"].isna().sum()
    if biorep_nan_count > 0:
        warnings.warn(
            f"{biorep_nan_count} rows have NA for BioReplicate. Ensure your annotation file contains this column."
        )

    if run_to_fraction is None:
        result_df["Fraction"] = 1
    else:
        result_df["Fraction"] = result_df["Run"].map(run_to_fraction)

    fraction_nan_count = result_df["Fraction"].isna().sum()
    if fraction_nan_count > 0:
        warnings.warn(
            f"{fraction_nan_count} rows have NA for Fraction. Ensure your annotation file contains this column."
        )

    starting_df_length = len(result_df)

    # filter results based on q_value
    result_df = result_df[result_df["_q_value"] <= qvalue]

    filtered_df_length = len(result_df)
    print(
        f"Filtered {starting_df_length - filtered_df_length} rows based on q-value <= {qvalue}"
    )

    if require_unique_peptides:
        starting_df_length = len(result_df)

        # remove rows which have a ';' in the protein column
        result_df = result_df[
            ~result_df["ProteinName"].str.contains(";")
        ]

        unqiue_peptide_length = len(result_df)
        print(
            f"Filtered {starting_df_length - unqiue_peptide_length} rows based on unique peptides (no ';' in ProteinName)"
        )


    # remove rows with less than min_protein_features
    starting_df_length = len(result_df)
    result_df["_proteins_count"] = result_df["ProteinName"].map(proteins_to_count)

    result_df = result_df[result_df["_proteins_count"] >= min_protein_features]
    protein_filterred_df_length = len(result_df)
    print(
        f"Filtered {starting_df_length - protein_filterred_df_length} rows based on minimum protein features >= {min_protein_features}"
    )

    # _mesurments
    result_df["_measurements"] = result_df.apply(
        lambda row: peptide_charge_counts.get(
            (row["PeptideSequence"], row["PrecursorCharge"]), 0
        ),
        axis=1,
    )
    starting_df_length = len(result_df)
    result_df = result_df[result_df["_measurements"] >= min_measurments]
    measurements_filtered_df_length = len(result_df)
    print(
        f"Filtered {starting_df_length - measurements_filtered_df_length} rows based on minimum measurements >= {min_measurments}"
    )

    # drop nan rows
    starting_df_length = len(result_df)
    result_df.dropna(
        subset=["Condition", "BioReplicate", "IsotopeLabelType", "Fraction"],
        inplace=True,
    )
    
    print(
        f"Dropped {starting_df_length - len(result_df)} rows with NaN in Condition, BioReplicate, IsotopeLabelType, or Fraction."
    )

    if starting_df_length != len(result_df):
        # warning if nan values were removed
        warnings.warn(
            f"{starting_df_length - len(result_df)} rows had NaN values in Condition, BioReplicate, IsotopeLabelType, or Fraction and were removed."
        )

    print(f"Final number of rows after all filters: {len(result_df)}")


    # sort by (Peptide, 'Charge, Run)
    result_df.sort_values(
        by=["PeptideSequence", "PrecursorCharge", "Run"], inplace=True
    )

    # remove cols that start with "_"
    if not include_filter_cols:
        result_df = result_df.loc[:, ~result_df.columns.str.startswith("_")]

    return result_df


def cli_runner():
    # parse args using arg parser

    args = argparse.ArgumentParser(
        description="Convert Sage LFQ data to MSstats format."
    )
    args.add_argument(
        "--lfq_file",
        type=str,
        required=True,
        help="Path to the LFQ data file (TSV, CSV, or Parquet format).",
    )
    args.add_argument(
        "--annotation_file",
        type=str,
        required=True,
        help="Path to the annotation file (TSV, CSV, or Excel format).",
    )
    args.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Path to save the converted MSstats format file (TSV, CSV, or Parquet format).",
    )
    args.add_argument(
        "--qvalue",
        "--protein_qvalue",  # Alias for backward compatibility
        type=float,
        default=0.01,
        help="Q-value cutoff for filtering (default: 0.01).",
    )
    args.add_argument(
        "--min_measurments",
        type=int,
        default=1,
        help="Minimum number of non-zero measurements required for a peptide-charge pair (default: 1).",
    )
    args.add_argument(
        "--min_protein_features",
        type=int,
        default=1,
        help="Minimum number of peptides required for a protein (default: 1).",
    )

    args.add_argument(
        "--require_unique_peptides",
        action="store_true",
        help="Require unique peptides (no ';' in ProteinName) (default: True).",
    )

    args.add_argument(
        "--include_filter_cols",
        action="store_true",
        help="Include intermediate filtering columns prefixed with '_' in output (default: True).",
    )
    args = args.parse_args()

    # Read LFQ file
    if args.lfq_file.endswith(".tsv"):
        lfq_df = pd.read_csv(args.lfq_file, sep="\t")
    elif args.lfq_file.endswith(".csv"):
        lfq_df = pd.read_csv(args.lfq_file)
    elif args.lfq_file.endswith(".parquet"):
        lfq_df = pd.read_parquet(args.lfq_file)
    else:
        raise ValueError("LFQ file must be a TSV, CSV, or Parquet file.")

    # Read annotation file
    if args.annotation_file.endswith(".tsv"):
        annotation_df = pd.read_csv(args.annotation_file, sep="\t")
    elif args.annotation_file.endswith(".xlsx"):
        annotation_df = pd.read_excel(args.annotation_file)
    elif args.annotation_file.endswith(".csv"):
        annotation_df = pd.read_csv(args.annotation_file)
    else:
        raise ValueError("Annotation file must be a TSV, CSV, or Excel file.")

    # Convert to MSstats format
    output_df = run_sage_lfq(
        lfq_df=lfq_df,
        annotation_df=annotation_df,
        qvalue=args.qvalue,  # Use the new qvalue parameter
        min_measurments=args.min_measurments,
        min_protein_features=args.min_protein_features,
        include_filter_cols=args.include_filter_cols,
        require_unique_peptides=args.require_unique_peptides,
    )

    # Save output file
    if args.output_file.endswith(".tsv"):
        output_df.to_csv(args.output_file, sep="\t", index=False)
    elif args.output_file.endswith(".parquet"):
        output_df.to_parquet(args.output_file, index=False)
    elif args.output_file.endswith(".csv"):
        output_df.to_csv(args.output_file, index=False)
    else:
        raise ValueError("Output file must be a TSV, CSV, or Parquet file.")


if __name__ == "__main__":
    lfq_file = "/workspaces/SageWebApp/sage_results/lfq.tsv"
    annotation_file = "/workspaces/SageWebApp/sage_results/annotations.tsv"

    
    lfq_df = pd.read_csv(lfq_file, sep="\t")
    annotation_df = pd.read_csv(annotation_file, sep="\t")

    print("Running Sage LFQ conversion...")

    df = run_sage_lfq(
        lfq_df=lfq_df,
        annotation_df=annotation_df,
        include_filter_cols=False,
        min_protein_features=2,
        min_measurments=1,
        qvalue=0.01, 
        require_unique_peptides=True
    )

    # write to file
    output_file = "/workspaces/SageWebApp/sage_results/sage_lfq_converted.tsv"
    df.to_csv(output_file, sep="\t", index=False)
