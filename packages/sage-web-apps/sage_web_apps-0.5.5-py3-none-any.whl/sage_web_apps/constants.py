from enum import Enum, auto


SAGE_RESULTS_FOLDER = "results"
SAGE_EXECUTABLE = "sage"
APP_NAME = "SageWebApps"

SAGE_DOWNLOAD_URLS = {
    "v0.14.7": {
        "darwin": {
            "aarch64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-aarch64-apple-darwin.tar.gz",
            "x86_64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-x86_64-apple-darwin.tar.gz"
        },
        "linux": {
            "aarch64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-aarch64-unknown-linux-gnu.tar.gz",
            "x86_64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-x86_64-unknown-linux-gnu.tar.gz"
        },
        "windows": {
            "x86_64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-x86_64-pc-windows-msvc.zip"
        }
    },
    "v0.14.6": {
        "darwin": {
            "aarch64": "https://github.com/lazear/sage/releases/download/v0.14.6/sage-v0.14.6-aarch64-apple-darwin.tar.gz",
            "x86_64": "https://github.com/lazear/sage/releases/download/v0.14.6/sage-v0.14.6-x86_64-apple-darwin.tar.gz"
        },
        "linux": {
            "aarch64": "https://github.com/lazear/sage/releases/download/v0.14.6/sage-v0.14.6-aarch64-unknown-linux-gnu.tar.gz",
            "x86_64": "https://github.com/lazear/sage/releases/download/v0.14.6/sage-v0.14.6-x86_64-unknown-linux-gnu.tar.gz"
        },
        "windows": {
            "x86_64": "https://github.com/lazear/sage/releases/download/v0.14.6/sage-v0.14.6-x86_64-pc-windows-msvc.zip"
        }
    },
}

SAGE_VERSIONS = list(SAGE_DOWNLOAD_URLS.keys())

# Default search name
DEFAULT_SEARCH_NAME = "sage_search"

class SageQueryParam(str, Enum):
    DATABASE_BUCKET_SIZE = 'database_bucket_size'
    DATABASE_FASTA = 'database_fasta'
    DATABASE_ENZYME_MISSED_CLEAVAGES = 'database_enzyme_missed_cleavages'
    DATABASE_ENZYME_MIN_LEN = 'database_enzyme_min_len'
    DATABASE_ENZYME_MAX_LEN = 'database_enzyme_max_len'
    DATABASE_ENZYME_CLEAVE_AT = 'database_enzyme_cleave_at'
    DATABASE_ENZYME_RESTRICT = 'database_enzyme_restrict'
    DATABASE_ENZYME_TERMINAL = 'database_enzyme_terminal'
    DATABASE_ENZYME_SEMI_ENZYMATIC = 'database_enzyme_semi_enzymatic'
    DATABASE_PEPTIDE_MIN_MASS = 'database_peptide_min_mass'
    DATABASE_PEPTIDE_MAX_MASS = 'database_peptide_max_mass'
    DATABASE_ION_KINDS = 'database_ion_kinds'
    DATABASE_MIN_ION_INDEX = 'database_min_ion_index'
    DATABASE_DECOY_TAG = 'database_decoy_tag'
    DATABASE_GENERATE_DECOYS = 'database_generate_decoys'
    DATABASE_STATIC_MODS = 'database_static_mods'
    DATABASE_VARIABLE_MODS = 'database_variable_mods'
    DATABASE_MAX_VARIABLE_MODS = 'database_max_variable_mods'
    PRECURSOR_TOL_MIN_VALUE = 'precursor_tol_min_value'
    PRECURSOR_TOL_MAX_VALUE = 'precursor_tol_max_value'
    PRECURSOR_TOL_UNIT = 'precursor_tol_unit'
    FRAGMENT_TOL_MIN_VALUE = 'fragment_tol_min_value'
    FRAGMENT_TOL_MAX_VALUE = 'fragment_tol_max_value'
    FRAGMENT_TOL_UNIT = 'fragment_tol_unit'
    OUTPUT_DIRECTORY = 'output_directory'
    SEARCH_NAME = 'search_name'
    MZML_PATHS = 'mzml_paths'
    PRECURSOR_MIN_CHARGE = 'precursor_min_charge'
    PRECURSOR_MAX_CHARGE = 'precursor_max_charge'
    ISOTOPE_MIN_ERROR = 'isotope_min_errors'
    ISOTOPE_MAX_ERROR = 'isotope_max_errors'
    DEISOTOPE = 'deisotope'
    CHIMERA = 'chimera'
    WIDE_WINDOW = 'wide_window'
    PREDICT_RT = 'predict_rt'
    MIN_PEAKS = 'min_peaks'
    MAX_PEAKS = 'max_peaks'
    MIN_MATCHED_PEAKS = 'min_matched_peaks'
    MAX_FRAGMENT_CHARGE = 'max_fragment_charge'
    REPORT_PSMS = 'report_psms'
    ENABLE_TMT_QUANT = 'enable_quant_tmt'
    QUANT_TMT = 'quant_tmt'
    QUANT_LFQ = 'quant_lfq'
    QUANT_TMT_SETTINGS_LEVEL = 'quant_tmt_settings_level'
    QUANT_TMT_SETTINGS_SN = 'quant_tmt_settings_sn'
    QUANT_LFQ_SETTINGS_PEAK_SCORING = 'quant_lfq_settings_peak_scoring'
    QUANT_LFQ_SETTINGS_INTEGRATION = 'quant_lfq_settings_integration'
    QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE = 'quant_lfq_settings_spectral_angle'
    QUANT_LFQ_SETTINGS_PPM_TOLERANCE = 'quant_lfq_settings_ppm_tolerance'
    QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE = 'quant_lfq_settings_mobility_pct_tolerance'
    QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES = 'quant_lfq_settings_combine_charge_states'
    BRUKER_MS1_MZ_PPM = 'bruker_ms1_mz_ppm'
    BRUKER_MS1_IMS_PCT = 'bruker_ms1_ims_pct'
    BRUKER_MS2_SMOOTHING_WINDOW = 'bruker_ms2_smoothing_window'
    BRUKER_MS2_CENTROIDING_WINDOW = 'bruker_ms2_centroiding_window'
    BRUKER_MS2_CALIBRATION_TOLERANCE = 'bruker_ms2_calibration_tolerance'
    BRUKER_MS2_CALIBRATE = 'bruker_ms2_calibrate'
    
    BRUKER_MS2_FRAME_SPLITTING_TYPE = 'bruker_ms2_frame_splitting_type'
    BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE = 'bruker_ms2_frame_splitting_minor_type'
    
    BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_WIDTH = 'bruker_ms2_frame_splitting_quadrupole_mobility_width'
    BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_OVERLAP = 'bruker_ms2_frame_splitting_quadrupole_mobility_overlap'
    BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_UNKNOWN = 'bruker_ms2_frame_splitting_quadrupole_mobility_unknown'
    
    BRUKER_MS2_FRAME_SPLITTING_EVEN_NUM = 'bruker_ms2_frame_splitting_even_num'