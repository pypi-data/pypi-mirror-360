import json
import os
from typing import Dict, List, Literal
import pandas as pd
import streamlit as st
import streamlit_permalink as stp
from sage_web_apps.pydantic_config import SageConfig
from sage_web_apps import constants

import streamlit_notify as stn
import traceback


def update_modification_dataframe(
    key: str, df: pd.DataFrame, append: bool, is_static: bool
) -> None:
    
    original_df = stp.data_editor.get_url_value(key)

    if original_df is None:
        original_df = pd.DataFrame(columns=["Residue", "Mass"])
    elif len(original_df) == 0:
        original_df = pd.DataFrame({"Residue": [''], "Mass": [0.0]})
    else:
        original_df = original_df[0]

    if append:
        df = pd.concat([original_df, df], ignore_index=True)

        # drop any rows with  Residue == "" and Mass == 0.0
        df = df[(df["Residue"] != "") & (df["Mass"] != 0.0)]

        if is_static:
            df = df.drop_duplicates(
                subset=["Residue"], keep="last"
            ).reset_index(drop=True)
            
        else:
            df = df.drop_duplicates(
                subset=["Residue", "Mass"], keep="last"
            ).reset_index(drop=True)

        if len(df) == 0:
            df = pd.DataFrame({"Residue": [''], "Mass": [0.0]})

    else:
        if len(df) == 0:
            if is_static:
                df = pd.DataFrame({"Residue": [''], "Mass": [0.0]})

    stp.data_editor.set_url_value(
        url_key=key,
        value=df,
    )

    st.rerun()

def update_mzml_dataframe(
    key: str, df: pd.DataFrame, append: bool
) -> None:
    
    original_df = stp.data_editor.get_url_value(key)

    if original_df is None:
        original_df = pd.DataFrame({"mzML Path":['']})
    elif len(original_df) == 0:
        original_df = pd.DataFrame({"mzML Path":['']})
    else:
        original_df = original_df[0]


    if append:
        df = pd.concat([original_df, df], ignore_index=True)

        df = df.drop_duplicates(
                subset=["mzML Path"], keep="last"
            ).reset_index(drop=True)

        if len(df) == 0:
            df = pd.DataFrame({"mzML Path":['']})

    else:
        if len(df) == 0:
            df = pd.DataFrame({"mzML Path":['']})

    stp.data_editor.set_url_value(
        url_key=key,
        value=df,
    )

    st.rerun()


def get_config_params(is_local: bool, working_dir, output_dir) -> Dict:

    stn.notify_all()

    load_preset()

    with st.container(height=550):
        (
            file_tab,
            enzyme_tab,
            fragment_tab,
            static_mods_tab,
            variable_mods_tab,
            search_tolerance_tab,
            spectra_processing_tab,
            quantification_tab,
            bruker_tab,
        ) = st.tabs(
            [
                "Input",
                "Enzyme",
                "Fragment",
                "Static Mods",
                "Variable Mods",
                "Search",
                "Spectra",
                "Quant",
                "Bruker",
            ]
        )

    error_container = st.empty()

    params = {}
    
    with file_tab:
        file_tab_params = get_file_params(is_local, working_dir, output_dir, error_container)

    with enzyme_tab:
        enzyme_tab_params = get_enzyme_params(error_container)

    with fragment_tab:
        fragment_tab_params = get_fragment_params(error_container)

    with static_mods_tab:
        static_mods_tab_params = get_static_mods_params(error_container)

    with variable_mods_tab:
        variable_mods_tab_params = get_variable_mods_params(error_container)

    with search_tolerance_tab:
        search_tolerance_tab_params = get_search_tolerance_params(error_container)

    with spectra_processing_tab:
        spectra_processing_tab_params = get_spectra_processing_params(error_container)

    with quantification_tab:
        quantification_tab_params = get_quantification_params(error_container)

    with bruker_tab:
        bruker_tab_params = get_bruker_params(error_container)

    try:
        params = generate_sage_config(
            file_tab_params,
            enzyme_tab_params,
            fragment_tab_params,
            static_mods_tab_params,
            variable_mods_tab_params,
            search_tolerance_tab_params,
            spectra_processing_tab_params,
            quantification_tab_params,
            bruker_tab_params,
        )
    except Exception as e:
        error_container.error(f"Error generating configuration: {str(e)}")
        raise e

    config_json = json.dumps(params, indent=2)
    download_show_config(config_json)

    return params
    

def generate_sage_config(file_tab_params: Dict,
                         enzyme_tab_params: Dict,
                         fragment_tab_params: Dict,
                         static_mods_tab_params: Dict,
                         variable_mods_tab_params: Dict,
                         search_tolerance_tab_params: Dict,
                         spectra_processing_tab_params: Dict,
                         quantification_tab_params: Dict,
                         bruker_tab_params: Dict) -> Dict:
    """
    Generate a Sage configuration dictionary using the dataclass model.
    """


    url_params = {}
    url_params.update(file_tab_params)
    url_params.update(enzyme_tab_params)
    url_params.update(fragment_tab_params)
    url_params.update(static_mods_tab_params)
    url_params.update(variable_mods_tab_params)
    url_params.update(search_tolerance_tab_params)
    url_params.update(spectra_processing_tab_params)
    url_params.update(quantification_tab_params)
    url_params.update(bruker_tab_params)

    return SageConfig.from_url_params(url_params).to_dict()


def get_file_params(is_local: bool, working_dir, output_dir, error_container) -> Dict:

    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    with c1:
        output_directory = stp.text_input(
            label="Output Directory",
            value=output_dir,
            key=constants.SageQueryParam.OUTPUT_DIRECTORY.value,
            help="Directory to save the output files.",
        )

    with c2:
        search_name = stp.text_input(
            label="Search Name",
            value="sage_search",  # Default to a random 8-character string
            key=constants.SageQueryParam.SEARCH_NAME.value,
            help="Name to search for in the results directory.",
        )

    output_path = os.path.join(output_directory, search_name)

    if is_local:
        c1, c2 = st.columns([3, 2], vertical_alignment="bottom")

        with c1:
            folder_path = stp.text_input(
                label="Bulk Upload Folder",
                placeholder="path/to/bulk/upload/folder",
                value=working_dir,
                key="local_folder_path",
                help="Path to the folder containing mzML files",
            )

            # fix folder path for windows
            if os.name == "nt" and folder_path:
                folder_path = folder_path.replace("\\", "/")

        with c2:
            if st.button("Load Folder", use_container_width=True):
                # Load mzML files from the folder
                if folder_path:
                    mzml_files = [
                        os.path.join(folder_path, f)
                        for f in os.listdir(folder_path)
                        if f.endswith(".mzML")
                        or f.endswith(".mzml")
                        or f.endswith(".mzml.gz")
                        or f.endswith(".mzML.gz")
                        or f.endswith(".d")
                    ]
                    if len(mzml_files) == 0:
                        error_container.error(
                            "No mzML files found in the specified folder."
                        )
                    else:
                        tmp_df = pd.DataFrame(columns=["mzML Path"])
                        tmp_df["mzML Path"] = mzml_files
                        update_modification_dataframe(
                            constants.SageQueryParam.MZML_PATHS.value, tmp_df, True, False
                        )
                else:
                    error_container.error("Please specify a folder path.")

    st.caption("mzml paths (paste path(s) to table below)")
    mzml_df = stp.data_editor(
        pd.DataFrame({"mzML Path": ['path/to/mzML.gz']}),
        column_config={
            "mzML Path": st.column_config.TextColumn(
                label="mzML Path", help="Path to the mzML file", required=True
            ),
        },
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True,
        key=constants.SageQueryParam.MZML_PATHS.value,
        height=240 if is_local else 315,
    )

    if len(mzml_df) == 0:
        update_mzml_dataframe(constants.SageQueryParam.MZML_PATHS.value, pd.DataFrame({"mzML Path": ['']}), False)

    # drop na
    if "mzML Path" not in mzml_df.columns:
        update_mzml_dataframe(constants.SageQueryParam.MZML_PATHS.value, pd.DataFrame({"mzML Path": ['']}), False)

    mzml_df = mzml_df.dropna(subset=["mzML Path"]).reset_index(drop=True)
    any_files_stripped = False

    if "mzML Path" in mzml_df.columns:
        mzml_paths = mzml_df["mzML Path"].tolist()
    else:
        mzml_paths = []

    # remove empty paths
    mzml_paths = [path for path in mzml_paths if path.strip()]

    # mix mzml paths with empty strings
    fized_mzml_paths = [path.strip().strip('"') for path in mzml_paths]

    if mzml_paths != fized_mzml_paths:
        #update_mzml_dataframe(constants.SageQueryParam.MZML_PATHS.value, pd.DataFrame({"mzML Path": fized_mzml_paths}), False)
        pass

    return {
        constants.SageQueryParam.OUTPUT_DIRECTORY.value: output_path,
        constants.SageQueryParam.MZML_PATHS.value: fized_mzml_paths,
    }

def update_enzyme_params(cleave_at: str, restrict: str, enzyme_terminal: Literal["C", "N"], missed_cleavages: int, semi_enzymatic: bool) -> None:
    # update query params cleave_at="KR"
    stp.text_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_CLEAVE_AT.value, 
                                    value=cleave_at)
    stn.toast(f"cleave_at={cleave_at}", icon="✅")
    stp.text_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_RESTRICT.value,
                                    value=restrict)
    stn.toast(f"{constants.SageQueryParam.DATABASE_ENZYME_RESTRICT.value}={restrict}", icon="✅")
    stp.radio.set_url_value(
        url_key=constants.SageQueryParam.DATABASE_ENZYME_TERMINAL.value,
        value=enzyme_terminal
    )
    stn.toast(f"enzyme_terminal={enzyme_terminal}", icon="✅")
    stp.number_input.set_url_value(
        url_key=constants.SageQueryParam.DATABASE_ENZYME_MISSED_CLEAVAGES.value,
        value=missed_cleavages
    )
    stn.toast(f"missed_cleavages={missed_cleavages}", icon="✅")
    stp.checkbox.set_url_value(
        url_key=constants.SageQueryParam.DATABASE_ENZYME_SEMI_ENZYMATIC.value,
        value=semi_enzymatic
    )
    stn.toast(f"semi_enzymatic={semi_enzymatic}", icon="✅")

    st.rerun()

def get_enzyme_params(error_container) -> Dict:
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Trypsin (KR!P)", use_container_width=True):
            update_enzyme_params(
                cleave_at="KR",
                restrict="P",
                enzyme_terminal="C",
                missed_cleavages=2,
                semi_enzymatic=False
            )

        # chymotrypsin
        if st.button("Chymotrypsin (FWYL!P)", use_container_width=True):
            update_enzyme_params(
                cleave_at="FWYL",
                restrict="P",
                enzyme_terminal="C",
                missed_cleavages=5,
                semi_enzymatic=False
            )

        if st.button("Lys-C (K!P)", use_container_width=True):
            update_enzyme_params(
                cleave_at="K",
                restrict="P",
                enzyme_terminal="C",
                missed_cleavages=1,
                semi_enzymatic=False
            )

        if st.button("Asp-N (DE)", use_container_width=True):
            update_enzyme_params(
                cleave_at="DE",
                restrict="",
                enzyme_terminal="N",
                missed_cleavages=2,
                semi_enzymatic=False
            )

        # protinase K
        if st.button("Protinase K (AEFILTVWY)", use_container_width=True):
            update_enzyme_params(
                cleave_at="AEFILTVWY",
                restrict="",
                enzyme_terminal="C",
                missed_cleavages=7,
                semi_enzymatic=False
            )

        if st.button("Arg-C (R!P)", use_container_width=True):
            update_enzyme_params(
                cleave_at="R",
                restrict="P",
                enzyme_terminal="C",
                missed_cleavages=1,
                semi_enzymatic=False
            )

        if st.button("Non-enzymatic ()", use_container_width=True):
            update_enzyme_params(
                cleave_at="",
                restrict="",
                enzyme_terminal="C",
                missed_cleavages=0,
                semi_enzymatic=False
            )

        if st.button("No Digestion ($)", use_container_width=True):
            update_enzyme_params(
                cleave_at="$",
                restrict="",
                enzyme_terminal="C",
                missed_cleavages=0,
                semi_enzymatic=False
            )

    with c2:

        missed_cleavages = stp.number_input(
            label="Missed Cleavages",
            min_value=0,
            max_value=None,
            value=2,
            key=constants.SageQueryParam.DATABASE_ENZYME_MISSED_CLEAVAGES.value,
            help="Number of missed cleavages.",
        )

        sc1, sc2 = st.columns(2)
        with sc1:
            min_len = stp.number_input(
                "Minimum Peptide Length",
                min_value=1,
                max_value=None,
                value=5,
                key=constants.SageQueryParam.DATABASE_ENZYME_MIN_LEN.value,
                help="The minimum amino acid (AA) length of peptides to search",
            )

        with sc2:
            max_len = stp.number_input(
                "Maximum Peptide Length",
                min_value=1,
                max_value=None,
                value=50,
                key=constants.SageQueryParam.DATABASE_ENZYME_MAX_LEN.value,
                help="The maximum amino acid (AA) length of peptides to search",
            )

        # assert min_len < max_len
        if min_len > max_len:
            error_container.error(
                "Minimum length must be less than or equal to maximum length."
            )

        cleave_at = stp.text_input(
            label="Cleave At",
            value="KR",
            key=constants.SageQueryParam.DATABASE_ENZYME_CLEAVE_AT.value,
            help="Amino acids to cleave at.",
        )
        restrict = stp.text_input(
            label="Restrict",
            value="P",
            key=constants.SageQueryParam.DATABASE_ENZYME_RESTRICT.value,
            help="Single character string. Do not cleave if this amino acid follows the cleavage site.",
            max_chars=1,
        )

        if restrict == "":
            restrict = None

        sc1, sc2 = st.columns(2)
        with sc1:
            enzyme_terminus = stp.radio(
                "Enzyme Terminus",
                ["N", "C"],
                index=1,
                horizontal=True,
                key=constants.SageQueryParam.DATABASE_ENZYME_TERMINAL.value,
                help="Select the enzyme terminus to use for the search.",
            )

        with sc2:
            semi_enzymatic = stp.checkbox(
                "Semi-enzymatic",
                value=False,
                key=constants.SageQueryParam.DATABASE_ENZYME_SEMI_ENZYMATIC.value,
                help="Select if the search should be semi-enzymatic.",
            )

    return {
        constants.SageQueryParam.DATABASE_ENZYME_MISSED_CLEAVAGES: missed_cleavages,
        constants.SageQueryParam.DATABASE_ENZYME_MIN_LEN: min_len,
        constants.SageQueryParam.DATABASE_ENZYME_MAX_LEN: max_len,
        constants.SageQueryParam.DATABASE_ENZYME_CLEAVE_AT: cleave_at,
        constants.SageQueryParam.DATABASE_ENZYME_RESTRICT: restrict,
        constants.SageQueryParam.DATABASE_ENZYME_TERMINAL: enzyme_terminus,
        constants.SageQueryParam.DATABASE_ENZYME_SEMI_ENZYMATIC: semi_enzymatic,
    }


def get_fragment_params(error_container) -> Dict:
    c1, c2 = st.columns([1, 2])

    with c1:

        st.caption("Resolution")

        if st.button("High Res MS/MS", use_container_width=True):
            # update query params bucket_size=8192
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_BUCKET_SIZE.value,
                value=8192
            )

            stp.checkbox.set_url_value(
                url_key=constants.SageQueryParam.DEISOTOPE.value,
                value=True
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MIN_PEAKS.value,
                value=15
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MAX_PEAKS.value,
                value=150
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MIN_MATCHED_PEAKS.value,
                value=4
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MAX_FRAGMENT_CHARGE.value,
                value=1
            )
            stn.toast(f"bucket_size={8192}", icon="✅")
            stn.toast(f"deisotope=True", icon="✅")
            stn.toast(f"min_peaks=15", icon="✅")
            stn.toast(f"max_peaks=150", icon="✅")
            stn.toast(f"min_matched_peaks=4", icon="✅")
            stn.toast(f"max_fragment_charge=1", icon="✅")
            st.rerun()

        if st.button("Low Res MS/MS", use_container_width=True):
            # update query params bucket_size=32768
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_BUCKET_SIZE.value,
                value=32768
            )

            stp.checkbox.set_url_value(
                url_key=constants.SageQueryParam.DEISOTOPE.value,
                value=False
            )

            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MIN_PEAKS.value,
                value=15
            )

            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MAX_PEAKS.value,
                value=150
            )

            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MIN_MATCHED_PEAKS.value,
                value=4
            )

            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.MAX_FRAGMENT_CHARGE.value,
                value=2
            )

            stn.toast(f"bucket_size={32768}", icon="✅")
            stn.toast(f"deisotope=False", icon="✅")
            stn.toast(f"min_peaks=15", icon="✅")
            stn.toast(f"max_peaks=150", icon="✅")
            stn.toast(f"min_matched_peaks=4", icon="✅")
            stn.toast(f"max_fragment_charge=2", icon="✅")
            st.rerun()

        st.caption("Fragmentation")

        if st.button("CID/HCD", use_container_width=True):
            # update query params bucket_size=8192
            stp.segmented_control.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_ION_KINDS.value,
                value=list("by")
            )
            stn.toast(f"ion_kinds={list('by')}", icon="✅")
            st.rerun()
        if st.button("ETD/ECD", use_container_width=True):
            stp.segmented_control.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_ION_KINDS.value,
                value=list("cz")
            )
            stn.toast(f"ion_kinds={list('cz')}", icon="✅")
            st.rerun()
        if st.button("UVPD", use_container_width=True):
            stp.segmented_control.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_ION_KINDS.value,
                value=list("abcxyz")
            )
            stn.toast(f"ion_kinds={list('abcxyz')}", icon="✅")
            st.rerun()
        if st.button("IRMPD", use_container_width=True):
            stp.segmented_control.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_ION_KINDS.value,
                value=list("by")
            )
            stn.toast(f"ion_kinds={list('by')}", icon="✅")
            st.rerun()

    with c2:
        sc1, sc2 = st.columns(2)
        with sc1:
            bucket_size = stp.selectbox(
                label="Bucket Size",
                options=[8192, 16384, 32768, 65536],
                index=2,
                accept_new_options=True,
                help="Use lower values (8192) for high-res MS/MS, higher values for low-res MS/MS (only affects search speed)",
                key=constants.SageQueryParam.DATABASE_BUCKET_SIZE.value,
            )
        with sc2:
            min_ion_index = stp.number_input(
                label="Minimum Ion Index",
                min_value=0,
                max_value=None,
                value=2,
                key=constants.SageQueryParam.DATABASE_MIN_ION_INDEX.value,
                help="Do not generate b1..bN or y1..yN ions for preliminary searching if min_ion_index = N. Does not affect full scoring of PSMs.",
            )

        ion_kinds = stp.segmented_control(
            label="Fragment Ions",
            options=list("abcxyz"),
            default=list("by"),
            key=constants.SageQueryParam.DATABASE_ION_KINDS.value,
            help="Select the fragment ions to use for the search.",
            selection_mode="multi",
        )

        if len(ion_kinds) == 0:
            error_container.error("At least one ion type must be selected.")

        max_fragment_charge = stp.number_input(
            label="Maximum Fragment Charge",
            min_value=1,
            max_value=None,
            value=None,
            key=constants.SageQueryParam.MAX_FRAGMENT_CHARGE.value,
            help="Maximum charge state of fragment ions to use for the search.",
        )

        peptide_min_mass = stp.number_input(
            "Peptide Minimum Mass",
            min_value=0.0,
            max_value=None,
            value=500.0,
            key=constants.SageQueryParam.DATABASE_PEPTIDE_MIN_MASS.value,
            help="Minimum mass of peptides to search.",
        )
        peptide_max_mass = stp.number_input(
            "Peptide Maximum Mass",
            min_value=0.0,
            max_value=None,
            value=5000.0,
            key=constants.SageQueryParam.DATABASE_PEPTIDE_MAX_MASS.value,
            help="Maximum mass of peptides to search.",
        )

        if peptide_min_mass >= peptide_max_mass:
            error_container.error("Minimum mass must be less than maximum mass.")

    return {
        constants.SageQueryParam.DATABASE_BUCKET_SIZE: bucket_size,
        constants.SageQueryParam.DATABASE_ION_KINDS: ion_kinds,
        constants.SageQueryParam.DATABASE_MIN_ION_INDEX: min_ion_index,
        constants.SageQueryParam.MAX_FRAGMENT_CHARGE: max_fragment_charge,
        constants.SageQueryParam.DATABASE_PEPTIDE_MIN_MASS: peptide_min_mass,
        constants.SageQueryParam.DATABASE_PEPTIDE_MAX_MASS: peptide_max_mass,
    }

def get_static_mods_params(error_container) -> Dict:
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Carbamidomethylation (C)", use_container_width=True):
            cysteine_df = pd.DataFrame({"Residue": ["C"], "Mass": [57.0215]})
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, cysteine_df, True, True)
        if st.button("TMT 2-plex (K^)", use_container_width=True):
            tmt_2plex_df = pd.DataFrame(
                {"Residue": ["K", "^"], "Mass": [225.1558, 225.1558]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, tmt_2plex_df, True, True)
        if st.button("TMT 6-plex (K^)", use_container_width=True):
            tmt_6plex_df = pd.DataFrame(
                {"Residue": ["K", "^"], "Mass": [229.1629, 229.1629]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, tmt_6plex_df, True, True)
        if st.button("TMT 10-plex (K^)", use_container_width=True):
            tmt_10plex_df = pd.DataFrame(
                {"Residue": ["K", "^"], "Mass": [229.1629, 304.2071]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, tmt_10plex_df, True, True)
        if st.button("TMT 16-plex (K^)", use_container_width=True):
            tmt_16plex_df = pd.DataFrame(
                {"Residue": ["K", "^"], "Mass": [304.2071, 304.2071]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, tmt_16plex_df, True, True)
        if st.button("iTRAQ (K^)", use_container_width=True):
            itraq_df = pd.DataFrame(
                {"Residue": ["K", "^"], "Mass": [144.1021, 144.1021]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, itraq_df, True, True)
        if st.button("Dimethyl (K^)", use_container_width=True):
            dimethyl_df = pd.DataFrame(
                {"Residue": ["K", "^"], "Mass": [28.0313, 28.0313]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, dimethyl_df, True, True)
        if st.button(
            "Clear",
            use_container_width=True,
            type="primary",
            key="clear_static_mods",
        ):
            empty_df = pd.DataFrame(columns=["Residue", "Mass"])
            update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, empty_df, False, True)

    with c2:
        with stp.form('Static Mods'):
            static_mods = stp.data_editor(
                pd.DataFrame({"Residue": ["C"], "Mass": [57.0215]}),
                column_config={
                    "Residue": st.column_config.TextColumn("Residue", help="Residue"),
                    "Mass": st.column_config.NumberColumn(
                        "Mass", format="%.5f", help="Mass of modification"
                    ),
                },
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key=constants.SageQueryParam.DATABASE_STATIC_MODS.value,
                height=350,
            )
            stp.form_submit_button(
                "Update Static Mods",
                use_container_width=True,
            )

    if len(static_mods) == 0:
        # if no static mods, create an empty dataframe with the correct columns
        static_mods = pd.DataFrame({"Residue": [''], "Mass": [0.0]})
        update_modification_dataframe(constants.SageQueryParam.DATABASE_STATIC_MODS.value, static_mods, False, True)

    # clear missing rows, either value as NA 
    static_mods = static_mods.dropna(subset=["Residue", "Mass"]).reset_index(drop=True)

    # check that no duplicate residues are selected
    if static_mods["Residue"].duplicated().any():
        error_container.error(
            "Duplicate residues selected in static modifications."
        )

    static_dict: Dict[str, float] = {}
    for _, row in static_mods.iterrows():
        
        residue = row["Residue"]
        mass = row["Mass"]

        if residue == '' or mass == 0.0:
            continue

        static_dict[residue] = mass

    return {
       constants.SageQueryParam.DATABASE_STATIC_MODS: static_dict,
    }

def get_variable_mods_params(error_container) -> Dict:
    var_df = pd.DataFrame({"Residue": ["M"], "Mass": [15.9949]})

    c1, c2 = st.columns([1, 2])

    with c1:
        if st.button("Phosphorylation (STY)", use_container_width=True):
            phospho_df = pd.DataFrame(
                {"Residue": ["S", "T", "Y"], "Mass": [79.9663, 79.9663, 79.9663]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, phospho_df, True, False)
        if st.button("Acetylation (K)", use_container_width=True):
            acetyl_df = pd.DataFrame({"Residue": ["K"], "Mass": [42.0106]})
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, acetyl_df, True, False)
        if st.button("Methylation (KR)", use_container_width=True):
            methyl_df = pd.DataFrame(
                {"Residue": ["K", "R"], "Mass": [14.0157, 14.0157]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, methyl_df, True, False)
        if st.button("Oxidation (M)", use_container_width=True):
            oxidation_df = pd.DataFrame({"Residue": ["M"], "Mass": [15.9949]})
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, oxidation_df, True, False)
        if st.button("Deamidation (NQ)", use_container_width=True):
            deamidation_df = pd.DataFrame(
                {"Residue": ["N", "Q"], "Mass": [0.9840, 0.9840]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, deamidation_df, True, False)
        if st.button("Ubiquitination (K)", use_container_width=True):
            ubiquitination_df = pd.DataFrame({"Residue": ["K"], "Mass": [114.0429]})
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, ubiquitination_df, True, False)
        if st.button("Methyl Ester (DE)", use_container_width=True):
            methyl_ester_df = pd.DataFrame(
                {"Residue": ["D", "E"], "Mass": [14.0157, 14.0157]}
            )
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, methyl_ester_df, True, False)
        if st.button(
            "Clear",
            use_container_width=True,
            type="primary",
            key="clear_variable_mods",
        ):
            empty_df = pd.DataFrame(columns=["Residue", "Mass"])
            update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, empty_df, False, False)

    with c2:
        max_variable_mods = stp.number_input(
            label="Max Variable Modifications",
            min_value=1,
            max_value=None,
            value=3,
            key=constants.SageQueryParam.DATABASE_MAX_VARIABLE_MODS.value,
            help="Maximum number of variable modifications to use for the search.",
        )

        with stp.form('Variable Mods'):
            variable_mods = stp.data_editor(
                var_df,
                column_config={
                    "Residue": st.column_config.TextColumn("Residue", help="Residue"),
                    "Mass": st.column_config.NumberColumn(
                        "Mass", format="%.5f", help="Mass of modification"
                    ),
                },
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key=constants.SageQueryParam.DATABASE_VARIABLE_MODS.value,
                height=280,
            )

            stp.form_submit_button(
                "Update Variable Mods",
                use_container_width=True,
            )

    if len(variable_mods) == 0:
        # if no variable mods, create an empty dataframe with the correct columns
        variable_mods = pd.DataFrame({"Residue": [''], "Mass": [0.0]})
        update_modification_dataframe(constants.SageQueryParam.DATABASE_VARIABLE_MODS.value, variable_mods, False, False)

    variable_mods = variable_mods.dropna(subset=["Residue", "Mass"]).reset_index(drop=True)


    # check no duplicated residue and mass pairs
    if variable_mods.duplicated(subset=["Residue", "Mass"]).any():
        error_container.error(
            "Duplicate residue and mass pairs selected in variable modifications."
        )       

    variable_dict: Dict[str, List[float]] = {}
    for index, row in variable_mods.iterrows():
        residue = row["Residue"]
        mass = row["Mass"]

        if residue == '' or mass == 0.0:
            continue

        if residue in variable_dict:
            variable_dict[residue].append(mass)
        else:
            variable_dict[residue] = [mass]

    return {
        constants.SageQueryParam.DATABASE_VARIABLE_MODS: variable_dict,
        constants.SageQueryParam.DATABASE_MAX_VARIABLE_MODS: max_variable_mods,
    }

def get_search_tolerance_params(error_container) -> Dict:

    c1, c2 = st.columns(2)
    with c1:
        wide_window = stp.checkbox(
                label="Wide Window",
                value=False,
                key=constants.SageQueryParam.WIDE_WINDOW.value,
                help="This parameter instructs Sage to dynamically change the precursor tolerance for each spectra based on the isolation window encoded in the mzML file",
            )
    with c2:
        keep_tolerances_in_sync = stp.checkbox(
            label="Keep Tolerances in Sync",
            value=True,
            key="toelrances_sync",
            help="If true, the fragment tolerance will be set to the same value as the precursor tolerance.",
        )

    def sync_tolerance_type_on_change(key: str, in_sync: bool) -> None:

        value = stp.selectbox.get_url_value(
            url_key=key,
        )

        if value is None:
            return
        
        if not isinstance(value, list):
            raise ValueError(
                f"Expected a list for key {key}, got {type(value)}"
            )
        if len(value) != 1:
            raise ValueError(
                f"Expected a single value for key {key}, got {len(value)} values"
            )

        value = value[0]

        if value not in ["ppm", "da"]:
            raise ValueError(
                f"Invalid value for key {key}: {value}. Expected 'ppm' or 'da'."
            )

        if in_sync:
            stp.selectbox.set_url_value(
                url_key=constants.SageQueryParam.FRAGMENT_TOL_UNIT.value,
                value=value,
            )

            stp.selectbox.set_url_value(
                url_key=constants.SageQueryParam.PRECURSOR_TOL_UNIT.value,
                value=value,
            )

    def sync_tolerance_value_on_change(
        key: str, in_sync: bool
    ) -> None:
        if in_sync:

            value = stp.number_input.get_url_value(
                url_key=key,
            )

            if value is None:
                return
            
            if not isinstance(value, list):
                raise ValueError(
                    f"Expected a list for key {key}, got {type(value)}"
                )
            if len(value) != 1:
                raise ValueError(
                    f"Expected a single value for key {key}, got {len(value)} values"
                )

            value = value[0]

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Invalid value for key {key}: {value}. Expected a number."
                )

            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.FRAGMENT_TOL_MIN_VALUE.value,
                value=-abs(value),
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.FRAGMENT_TOL_MAX_VALUE.value,
                value=abs(value),
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value,
                value=-abs(value),
            )
            stp.number_input.set_url_value(
                url_key=constants.SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value,
                value=abs(value),
            )


    c1, c2 = st.columns(2)
    with c1:

        precursor_tol_type = stp.selectbox(
            label="Precursor Tolerance Units",
            options=["ppm", "da"],
            index=0,
            help="Type of fragment tolerance to use",
            key=constants.SageQueryParam.PRECURSOR_TOL_UNIT.value,
            disabled=wide_window,
            on_change=sync_tolerance_type_on_change,
            kwargs={
                "key": constants.SageQueryParam.PRECURSOR_TOL_UNIT.value,
                "in_sync": keep_tolerances_in_sync,
            },
        )

        precursor_tol_minus = stp.number_input(
            label="Precursor Tolerance Min",
            value=-50.0,
            max_value=0.0,
            step=10.0 if precursor_tol_type == "ppm" else 0.1,
            key=constants.SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value,
            help="Precursor tolerance in Da or ppm",
            disabled=wide_window,
            on_change=sync_tolerance_value_on_change,
            kwargs={
                "key": constants.SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value,
                "in_sync": keep_tolerances_in_sync,
            },
        )
        precursor_tol_plus = stp.number_input(
            label="Precursor Tolerance Max",
            value=50.0,
            min_value=0.0,
            step=10.0 if precursor_tol_type == "ppm" else 0.1,
            key=constants.SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value,
            help="Precursor tolerance in Da or ppm",
            disabled=wide_window,
            on_change=sync_tolerance_value_on_change,
            kwargs={
                "key": constants.SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value,
                "in_sync": keep_tolerances_in_sync,
            },
        )
    with c2:

        fragment_tol_type = stp.selectbox(
            label="Fragment Tolerance Units",
            options=["ppm", "da"],
            index=0,
            help="Units for fragment tolerance",
            key=constants.SageQueryParam.FRAGMENT_TOL_UNIT.value,
            on_change=sync_tolerance_type_on_change,
            kwargs={
                "key": constants.SageQueryParam.FRAGMENT_TOL_UNIT.value,
                "in_sync": keep_tolerances_in_sync,
            },
        )

        fragment_tol_minus = stp.number_input(
            label="Fragment Tolerance Min",
            value=-50.0,
            max_value=0.0,
            step=10.0 if fragment_tol_type == "ppm" else 0.1,
            key=constants.SageQueryParam.FRAGMENT_TOL_MIN_VALUE.value,
            help="Fragment tolerance in Da or ppm",
            on_change=sync_tolerance_value_on_change,
            kwargs={
                "key": constants.SageQueryParam.FRAGMENT_TOL_MIN_VALUE.value,
                "in_sync": keep_tolerances_in_sync,
            },
        )
        fragment_tol_plus = stp.number_input(
            label="Fragment Tolerance Max",
            value=50.0,
            min_value=0.0,
            step=10.0 if fragment_tol_type == "ppm" else 0.1,
            key=constants.SageQueryParam.FRAGMENT_TOL_MAX_VALUE.value,
            help="Fragment tolerance in Da or ppm",
            on_change=sync_tolerance_value_on_change,
            kwargs={
                "key": constants.SageQueryParam.FRAGMENT_TOL_MAX_VALUE.value,
                "in_sync": keep_tolerances_in_sync,
            },
        )

    def fasta_on_change():
        fasta_path = st.session_state.get(
            constants.SageQueryParam.DATABASE_FASTA.value, None
        )

        original_fasta_path = fasta_path
        fasta_path = fasta_path.strip().strip('"')
        if fasta_path != original_fasta_path:
            stp.text_input.set_url_value(
                url_key=constants.SageQueryParam.DATABASE_FASTA.value,
                value=fasta_path
            )
            stn.toast(f"fasta_path={fasta_path}", icon="✅")
            return True
        return False

    fasta_path = stp.text_input(
        label="FASTA Path",
        placeholder="path/to/fasta",
        value="path/to/fasta",
        key=constants.SageQueryParam.DATABASE_FASTA.value,
        help="Path to the FASTA file",
        #on_change=fasta_on_change,
    )

    #if fasta_on_change():
    #    st.rerun()


    c1, c2 = st.columns(2, vertical_alignment="center")
    with c1:
        decoy_tag = stp.text_input(
            label="Decoy Tag",
            value="rev_",
            key=constants.SageQueryParam.DATABASE_DECOY_TAG.value,
            help="The tag used to identify decoy entries in the FASTA database",
        )
    with c2:
        generate_decoys = stp.checkbox(
            label="Generate Decoys",
            value=False,
            key=constants.SageQueryParam.DATABASE_GENERATE_DECOYS.value,
            help="If true, ignore decoys in the FASTA database matching decoy_tag, and generate internally reversed peptides",
        )

    return {
        constants.SageQueryParam.WIDE_WINDOW: wide_window,
        constants.SageQueryParam.PRECURSOR_TOL_UNIT: precursor_tol_type,
        constants.SageQueryParam.PRECURSOR_TOL_MIN_VALUE: precursor_tol_minus,
        constants.SageQueryParam.PRECURSOR_TOL_MAX_VALUE: precursor_tol_plus,
        constants.SageQueryParam.FRAGMENT_TOL_UNIT: fragment_tol_type,
        constants.SageQueryParam.FRAGMENT_TOL_MIN_VALUE: fragment_tol_minus,
        constants.SageQueryParam.FRAGMENT_TOL_MAX_VALUE: fragment_tol_plus,
        constants.SageQueryParam.DATABASE_FASTA: fasta_path,
        constants.SageQueryParam.DATABASE_DECOY_TAG: decoy_tag,
        constants.SageQueryParam.DATABASE_GENERATE_DECOYS: generate_decoys,
    }

def get_spectra_processing_params(error_container) -> Dict:
    c1, c2, c3 = st.columns(3)
    with c1:
        deisotope = stp.checkbox(
            label="Deisotope",
            value=False,
            key=constants.SageQueryParam.DEISOTOPE.value,
            help="Deisotope the MS2 spectra",
        )
    with c2:
        chimera = stp.checkbox(
            label="Chimera",
            value=False,
            key=constants.SageQueryParam.CHIMERA.value,
            help="Search for chimeric/co-fragmenting PSMs",
        )

    with c3:
        predict_rt = stp.checkbox(
            label="Predict RT",
            value=True,
            key=constants.SageQueryParam.PREDICT_RT.value,
            help="Predict retention time for the peptides. (You probably don't want to turn this off without good reason!)",
        )

    c1, c2 = st.columns(2)
    with c1:
        precursor_charge_min = stp.number_input(
            label="Minimum Precursor Charge",
            min_value=1,
            max_value=None,
            value=2,
            key=constants.SageQueryParam.PRECURSOR_MIN_CHARGE.value,
            help="Minimum charge state of precursor ions to use for the search",
        )
    with c2:
        precursor_charge_max = stp.number_input(
            label="Maximum Precursor Charge",
            min_value=1,
            max_value=None,
            value=4,
            key=constants.SageQueryParam.PRECURSOR_MAX_CHARGE.value,
            help="Maximum charge state of precursor ions to use for the search",
        )

    if precursor_charge_min > precursor_charge_max:
        error_container.error(
            "Minimum charge must be less than  or equal to maximum charge."
        )

    c1, c2 = st.columns(2)
    with c1:
        isotope_error_min = stp.number_input(
            label="Minimum Isotope Error",
            min_value=None,
            max_value=0,
            value=-1,
            key=constants.SageQueryParam.ISOTOPE_MIN_ERROR.value,
            help="Minimum number of isotopes to use for the search",
        )
    with c2:
        isotope_error_max = stp.number_input(
            label="Maximum Isotope Error",
            min_value=0,
            max_value=None,
            value=3,
            key=constants.SageQueryParam.ISOTOPE_MAX_ERROR.value,
            help="Maximum number of isotopes to use for the search",
        )

    c1, c2 = st.columns(2)
    with c1:
        min_peaks = stp.number_input(
            label="Minimum Peaks",
            min_value=0,
            max_value=None,
            value=15,
            key=constants.SageQueryParam.MIN_PEAKS.value,
            help="Only process MS2 spectra with at least N peaks",
        )
    with c2:
        max_peaks = stp.number_input(
            label="Maximum Peaks",
            min_value=0,
            max_value=None,
            value=150,
            key=constants.SageQueryParam.MAX_PEAKS.value,
            help="Take the top N most intense MS2 peaks to search",
        )

    if min_peaks > max_peaks:
        error_container.error(
            "Minimum peaks must be less than or equal to maximum peaks."
        )

    c1, c2 = st.columns(2)
    with c1:
        min_matched_peaks = stp.number_input(
            label="Minimum Matched Peaks",
            min_value=1,
            max_value=None,
            value=6,
            key=constants.SageQueryParam.MIN_MATCHED_PEAKS.value,
            help="Minimum number of matched peaks to report PSMs",
        )
    with c2:
        report_psms = stp.number_input(
            label="Report PSMs",
            min_value=1,
            max_value=None,
            value=1,
            key=constants.SageQueryParam.REPORT_PSMS.value,
            help="The number of PSMs to report for each spectrum. Higher values might disrupt re-scoring, it is best to search with multiple values",
        )

    return {
        constants.SageQueryParam.DEISOTOPE: deisotope,
        constants.SageQueryParam.CHIMERA: chimera,
        constants.SageQueryParam.PREDICT_RT: predict_rt,
        constants.SageQueryParam.PRECURSOR_MIN_CHARGE: precursor_charge_min,
        constants.SageQueryParam.PRECURSOR_MAX_CHARGE: precursor_charge_max,
        constants.SageQueryParam.ISOTOPE_MIN_ERROR: isotope_error_min,
        constants.SageQueryParam.ISOTOPE_MAX_ERROR: isotope_error_max,
        constants.SageQueryParam.MIN_PEAKS: min_peaks,
        constants.SageQueryParam.MAX_PEAKS: max_peaks,
        constants.SageQueryParam.MIN_MATCHED_PEAKS: min_matched_peaks,
        constants.SageQueryParam.REPORT_PSMS: report_psms,
    }

def get_quantification_params(error_container) -> Dict:

    with st.container(border=True):
        c1, c2 = st.columns(2, vertical_alignment="bottom")
        with c1:
            enable_tmt =stp.toggle(
                label="Enable TMT Quant",
                value=False,
                key=constants.SageQueryParam.ENABLE_TMT_QUANT.value,
                help="Enable TMT quantification parameters",
            )
            tmt_type = stp.selectbox(
                label="TMT Type",
                options=["Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18"],
                index=3,
                key=constants.SageQueryParam.QUANT_TMT.value,
                help="Select the TMT type to use for the search",
            )
        with c2:
            tmt_sn = stp.checkbox(
            label="Use Signal/Noise instead of intensity",
            value=False,
            key=constants.SageQueryParam.QUANT_TMT_SETTINGS_SN.value,
            help="Use Signal/Noise instead of intensity for TMT quantification. Requires noise values in mzML",
            )
            tmt_level = stp.number_input(
                label="TMT Level",
                value=3,
                min_value=0,
                key=constants.SageQueryParam.QUANT_TMT_SETTINGS_LEVEL.value,
                help="The MS-level to perform TMT quantification on",
            )
    
    with st.container(border=True):

        c1, c2 = st.columns(2, vertical_alignment="top")
        with c1:

            enable_lfq = stp.toggle(
                    label="Enable LFQ Quant",
                    value=False,
                    key=constants.SageQueryParam.QUANT_LFQ.value,
                    help="Enable LFQ quantification parameters",
                )
            combine_charge_states = stp.toggle(
                label="Combine Charge States",
                value=True,
                key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES.value,
                help="Combine charge states for LFQ quantification",
            )
        with c2:

            lfq_integration = stp.selectbox(
                label="LFQ Integration",
                options=["Sum", "Apex"],
                index=0,
                key= constants.SageQueryParam.QUANT_LFQ_SETTINGS_INTEGRATION.value,
                help="The method used for integrating peak intensities",
            )

        c1, c2 = st.columns(2, vertical_alignment="bottom")
        with c1:
            lfq_peak_scoring = stp.selectbox(
                label="LFQ Peak Scoring",
                options=["Hybrid", "Simple"],
                index=0,
                key= constants.SageQueryParam.QUANT_LFQ_SETTINGS_PEAK_SCORING.value,
                help="The method used for scoring peaks in LFQ",
            )

        with c2:
            lfq_spectral_angle = stp.number_input(
                label="LFQ Spectral Angle",
                min_value=0.0,
                max_value=None,
                value=0.7,
                key= constants.SageQueryParam.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE.value,
                help="Threshold for the normalized spectral angle similarity measure (observed vs theoretical isotopic envelope)",
            )

        c1, c2 = st.columns(2, vertical_alignment="bottom")
        with c1:
            lfq_ppm_tolerance = stp.number_input(
                label="LFQ PPM Tolerance",
                min_value=0.0,
                max_value=None,
                value=5.0,
                key= constants.SageQueryParam.QUANT_LFQ_SETTINGS_PPM_TOLERANCE.value,
                help="Tolerance for matching MS1 ions in parts per million",
            )

        with c2:

            lfq_mobility_pct_tolerance = stp.number_input(
                label="LFQ Mobility % Tolerance",
                min_value=0.0,
                max_value=None,
                value=3.0,
                key= constants.SageQueryParam.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE.value,
                help="Tolerance for matching MS1 ions in percent (default: 3.0). Only used for Bruker input.",
            )

    if enable_tmt is False:
        tmt_type = None


    return {
        constants.SageQueryParam.QUANT_TMT: tmt_type,
        constants.SageQueryParam.QUANT_TMT_SETTINGS_SN: tmt_sn,
        constants.SageQueryParam.QUANT_TMT_SETTINGS_LEVEL: tmt_level,
        constants.SageQueryParam.QUANT_LFQ: enable_lfq,
        constants.SageQueryParam.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES: combine_charge_states,
        constants.SageQueryParam.QUANT_LFQ_SETTINGS_INTEGRATION: lfq_integration,
        constants.SageQueryParam.QUANT_LFQ_SETTINGS_PEAK_SCORING: lfq_peak_scoring,
        constants.SageQueryParam.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE: lfq_spectral_angle,
        constants.SageQueryParam.QUANT_LFQ_SETTINGS_PPM_TOLERANCE: lfq_ppm_tolerance,
        constants.SageQueryParam.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE: lfq_mobility_pct_tolerance,
    }



@st.dialog("Load Preset Query Params")
def load_preset_from_params():
    params_file = st.file_uploader(
        label="Load Preset Query Params",
        type=["json"],
        key="load_preset_params",
        help="Load preset query params from a JSON file",
    )
    if st.button(
        "Load Preset",
        type="secondary",
        key="load_preset_button",
        use_container_width=True,
        help="Load preset query params from the uploaded JSON file",
        disabled=params_file is None
    ):
        try:
            preset_params = json.loads(params_file.read().decode("utf-8"))
            sage_params = SageConfig.from_dict(preset_params)
            url_params = sage_params.to_url_params()
            sage_params.update_url_params()
            stn.toast(
                "Preset query params loaded successfully!",
                icon="✅",)
            st.rerun()
            
        except Exception as e:
            st.error(f"Error loading preset params: {e}")
            traceback.print_exc()


def load_preset():
    # reset query params btn
    c1, c2, c3, c4 = st.columns(4)

    # Open Search: set wide window = false, precursor tol to da, and -100 - 500
    # WWA/PRM/DIA: wide_window = true, chimeric=false, report_psms=5

    if c1.button(
        label="Open Search",
        type="secondary",
        key="open_search",
        use_container_width=True,
        help="Open Search settings(wide_window = false, precursor_tol=da, precursor_tol_minus=-100, precursor_tol_plus=500)",
    ):

        stp.checkbox.set_url_value(
            url_key=constants.SageQueryParam.WIDE_WINDOW.value,
            value=False
        )
        stn.toast(f"wide_window={False}", icon="✅")
        stp.selectbox.set_url_value(
            url_key=constants.SageQueryParam.PRECURSOR_TOL_UNIT.value,
            value="da"
        )
        stn.toast(f"precursor_tol_unit=da", icon="✅")
        stp.number_input.set_url_value(
            url_key=constants.SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value,
            value=-100
        )
        stn.toast(f"precursor_tol_min_value=-100", icon="✅")
        stp.number_input.set_url_value(
            url_key=constants.SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value,
            value=500
        )
        stn.toast(f"precursor_tol_max_value=500", icon="✅")
        st.rerun()

    # WWA/PRM/DIA: set wide window = true, chimeric=false, report_psms=5
    if c2.button(
        label="WWA/PRM/DIA",
        type="secondary",
        key="wwa_prm_dia",
        use_container_width=True,
        help="WWA/PRM/DIA settings(wide_window = true, chimeric=false, report_psms=5)",
    ):
        stp.checkbox.set_url_value(
            url_key=constants.SageQueryParam.WIDE_WINDOW.value,
            value=True
        )
        stn.toast(f"wide_window={True}", icon="✅")
        stp.checkbox.set_url_value(
            url_key=constants.SageQueryParam.CHIMERA.value,
            value=False
        )
        stn.toast(f"chimeric={False}", icon="✅")
        stp.number_input.set_url_value(
            url_key=constants.SageQueryParam.REPORT_PSMS.value,
            value=5
        )
        stn.toast(f"report_psms={5}", icon="✅")
        st.rerun()

    if c3.button(
        label="Reset",
        type="secondary",
        key="reset_query_params",
        use_container_width=True,
        help="Reset all query params to default values",
    ):
        st.query_params.clear()
        stn.toast("Query params reset to default values", icon="✅")
        st.rerun()

    if c4.button(
        label="Load Config",
        type="secondary",
        key="load_preset",
        use_container_width=True,
        help="Load preset query params from the URL",
    ):
        # Load the preset from the query params
        load_preset_from_params()


def download_show_config(config_json):
    c1, c2 = st.columns(2)
    with c1:
        @st.dialog("Download Configuration")
        def popover_download():
            file_name = st.text_input(
                "File Name",
                value="sage_config.json",
                help="Enter the name of the configuration file to download.",
            )
            st.download_button(
                label=f"Download ({file_name})",
                data=config_json,
                file_name=file_name,
                type="primary",
                mime="application/json",
                use_container_width=True,
            )
        st.button("Download", on_click=popover_download, use_container_width=True)

    with c2:
        @st.dialog("Generated Configuration")
        def popover_code():
            st.code(config_json, language="json", height=500)

        st.button("Show Configuration", on_click=popover_code, use_container_width=True)

def get_bruker_params(error_container) -> Dict:
    """Get Bruker configuration parameters."""
        
    with st.container(border=False):        
        c1, c2 = st.columns(2)
        with c1:
            ms1_mz_ppm = stp.number_input(
                label="PPM Tolerance (MS1)",
                min_value=0.0,
                value=15.0,
                step=1.0,
                key=constants.SageQueryParam.BRUKER_MS1_MZ_PPM.value,
                help="Mass tolerance in PPM for MS1 data processing (used for LFQ)",
            )
        with c2:
            ms1_ims_pct = stp.number_input(
                label="IMS % Tolerance (MS1)",
                min_value=0.0,
                value=3.0,
                step=0.1,
                key=constants.SageQueryParam.BRUKER_MS1_IMS_PCT.value,
                help="Ion mobility tolerance in percent for MS1 data (used for LFQ)",
            )
    
    with st.container(border=False):        
        c1, c2 = st.columns(2)
        with c1:
            smoothing_window = stp.number_input(
                label="Smoothing Window (MS2)",
                min_value=1,
                value=1,
                step=1,
                key=constants.SageQueryParam.BRUKER_MS2_SMOOTHING_WINDOW.value,
                help="Window size for spectrum smoothing",
            )
        with c2:           
            calibration_tolerance = stp.number_input(
                label="Calibration Tolerance (MS2)",
                min_value=0.0,
                value=0.1,
                step=0.01,
                key=constants.SageQueryParam.BRUKER_MS2_CALIBRATION_TOLERANCE.value,
                help="Tolerance for mass calibration",
            )
        
        c1, c2 = st.columns(2, vertical_alignment="bottom")
        with c1:
            centroiding_window = stp.number_input(
                label="Centroiding Window (MS2)",
                min_value=1,
                value=1,
                step=1,
                key=constants.SageQueryParam.BRUKER_MS2_CENTROIDING_WINDOW.value,
                help="Window size for peak centroiding",
            )
        with c2:
            calibrate = stp.checkbox(
                label="Enable Calibration (MS2)",
                value=False,
                key=constants.SageQueryParam.BRUKER_MS2_CALIBRATE.value,
                help="Enable mass calibration for MS2 spectra",
            )
    
    with st.container(border=True):

        c1, c2 = st.columns(2, vertical_alignment="bottom")
        with c1:
            split_type = stp.selectbox(
                label="Frame Splitting",
                options=["Quadrupole", "Window"],
                index=0,
                key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_TYPE.value,
                help="Select the type of frame splitting for quadrupole data",
            )

        with c2:
            split_mode = stp.selectbox(
                label="Frame Splitting Mode",
                options=["UniformMobility", "Even", "None"],
                index=0,
                key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value,
                help="Select the mode for frame splitting",
            )

        if split_mode == "UniformMobility":
            c1, c2 = st.columns(2, vertical_alignment="bottom")
            with c1:
                ion_mobility_size = stp.number_input(
                    label="Ion Mobility Size",
                    min_value=0.0,
                    value=0.1,
                    step=0.1,
                    key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_WIDTH.value,
                    help="Size of the ion mobility window for uniform mobility splitting",
                )

            with c2:
                mobility_overlap = stp.number_input(
                    label="Mobility Overlap",
                    min_value=0.0,
                    value=0.005,
                    step=0.005,
                    key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_OVERLAP.value,
                    help="Overlap percentage for ion mobility windows",
                )

        elif split_mode == "Even":
            num_frames = stp.number_input(
                label="Number of Frames",
                min_value=1,
                value=10,
                step=1,
                key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_EVEN_NUM.value,
                help="Number of frames to split the data into",
            )
            


    d = {
        constants.SageQueryParam.BRUKER_MS1_MZ_PPM.value: ms1_mz_ppm,
        constants.SageQueryParam.BRUKER_MS1_IMS_PCT.value: ms1_ims_pct,
        constants.SageQueryParam.BRUKER_MS2_SMOOTHING_WINDOW.value: smoothing_window,
        constants.SageQueryParam.BRUKER_MS2_CENTROIDING_WINDOW.value: centroiding_window,
        constants.SageQueryParam.BRUKER_MS2_CALIBRATION_TOLERANCE.value: calibration_tolerance,
        constants.SageQueryParam.BRUKER_MS2_CALIBRATE.value: calibrate,
        constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_TYPE.value: split_type,
        constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value: split_mode,
    }

    if split_mode == "UniformMobility":
        d[constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_WIDTH.value] = ion_mobility_size
        d[constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_OVERLAP.value] = mobility_overlap
    elif split_mode == "Even":
        d[constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_EVEN_NUM.value] = num_frames
    
    return d

