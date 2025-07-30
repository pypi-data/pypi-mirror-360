"""
Sage configuration using Pydantic for better validation and serialization.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, Tuple, Union
import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator
import peptacular as pt
from sage_web_apps import constants
import streamlit_permalink as stp

SageQueryParam = constants.SageQueryParam

DEFAULT_MISSED_CLEAVAGES: Optional[int] = 2
DEFAULT_MIN_LEN: Optional[int] = 5
DEFAULT_MAX_LEN: Optional[int] = 50
DEFAULT_CLEAVE_AT: Optional[str] = "KR"
DEFAULT_RESTRICT: Optional[str] = "P"
DEFAULT_C_TERMINAL: Optional[bool] = True
DEFAULT_SEMI_ENZYMATIC: Optional[bool] = False

class EnzymeConfig(BaseModel, frozen=True):
    """Configuration for enzyme digestion."""
    # Define constants for default values as regular class variables, not Field objects
    missed_cleavages: Optional[int] = Field(default=DEFAULT_MISSED_CLEAVAGES, ge=0, validate_default=True)
    min_len: Optional[int] = Field(default=DEFAULT_MIN_LEN, gt=0, validate_default=True)
    max_len: Optional[int] = Field(default=DEFAULT_MAX_LEN, gt=0, validate_default=True)
    cleave_at: Optional[str] = Field(default=DEFAULT_CLEAVE_AT, min_length=0, validate_default=True)
    restrict: Optional[str] = Field(default=DEFAULT_RESTRICT, min_length=1, max_length=1, validate_default=True)
    c_terminal: Optional[bool] = Field(default=DEFAULT_C_TERMINAL, validate_default=True)
    semi_enzymatic: Optional[bool] = Field(default=DEFAULT_SEMI_ENZYMATIC, validate_default=True)

    @property
    def enzyme_terminus(self) -> str:
        if self.c_terminal is True or self.c_terminal is None:
            return 'C'
        return 'N'
        

    # Disabled since None migth be a valid value raterh than specifying default
    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:  
        """Replace None values with their defaults"""
        if data.get('missed_cleavages') is None:
            data['missed_cleavages'] = DEFAULT_MISSED_CLEAVAGES
        if data.get('min_len') is None:
            data['min_len'] = DEFAULT_MIN_LEN
        if data.get('max_len') is None:
            data['max_len'] = DEFAULT_MAX_LEN
        if data.get('cleave_at') is None:
            data['cleave_at'] = DEFAULT_CLEAVE_AT
        if data.get('restrict') is None:
            data['restrict'] = DEFAULT_RESTRICT
        if data.get('c_terminal') is None:
            data['c_terminal'] = DEFAULT_C_TERMINAL
        if data.get('semi_enzymatic') is None:
            data['semi_enzymatic'] = DEFAULT_SEMI_ENZYMATIC
        return data

    @field_validator('restrict')
    @classmethod
    def validate_restrict(cls, v):
        if v is None:
            return v
        if v not in pt.AMINO_ACIDS:
            raise ValueError(f"Invalid restrict character: {v}. Must be a single amino acid.")
        return v

    @field_validator('cleave_at')
    @classmethod
    def validate_cleave_at(cls, v):
        if v is None:
            raise ValueError("Cleave at cannot be empty")
        
        if  v == "": # Non-enzymatic
            return v

        if v == "$": # No digestion
            return v
        
        # check if all characters are valid amino acids or special characters
        if not all(c in pt.AMINO_ACIDS for c in v):
            raise ValueError(f"Invalid cleave_at characters: {v}. Must be valid amino acids.")

        return v

    @model_validator(mode='after')
    def validate_lengths(self):
        if self.max_len < self.min_len:
            raise ValueError("Maximum length must be greater than or equal to minimum length")
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        return self.model_dump()
    
    def to_url_params(self) -> Dict[str, Any]:
        return {
            SageQueryParam.DATABASE_ENZYME_MISSED_CLEAVAGES.value: self.missed_cleavages,
            SageQueryParam.DATABASE_ENZYME_MIN_LEN.value: self.min_len,
            SageQueryParam.DATABASE_ENZYME_MAX_LEN.value: self.max_len,
            SageQueryParam.DATABASE_ENZYME_CLEAVE_AT.value: self.cleave_at,
            SageQueryParam.DATABASE_ENZYME_RESTRICT.value: self.restrict,
            SageQueryParam.DATABASE_ENZYME_TERMINAL.value: 'C' if self.c_terminal else 'N',
            SageQueryParam.DATABASE_ENZYME_SEMI_ENZYMATIC.value: self.semi_enzymatic
        }
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'EnzymeConfig':
        """Create an EnzymeConfig instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary

        terminal = data.get(SageQueryParam.DATABASE_ENZYME_TERMINAL.value, 'C')
        if terminal not in ['C', 'N']:
            raise ValueError(f"Invalid value for terminal: {terminal}. Must be 'C' or 'N'.")

        return cls(
            missed_cleavages=data.get(SageQueryParam.DATABASE_ENZYME_MISSED_CLEAVAGES.value, DEFAULT_MISSED_CLEAVAGES),
            min_len=data.get(SageQueryParam.DATABASE_ENZYME_MIN_LEN.value, DEFAULT_MIN_LEN),
            max_len=data.get(SageQueryParam.DATABASE_ENZYME_MAX_LEN.value, DEFAULT_MAX_LEN),
            cleave_at=data.get(SageQueryParam.DATABASE_ENZYME_CLEAVE_AT.value, DEFAULT_CLEAVE_AT),
            restrict=data.get(SageQueryParam.DATABASE_ENZYME_RESTRICT.value, DEFAULT_RESTRICT),
            c_terminal= terminal == 'C',
            semi_enzymatic=data.get(SageQueryParam.DATABASE_ENZYME_SEMI_ENZYMATIC.value, DEFAULT_SEMI_ENZYMATIC)
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnzymeConfig':
        """Create an EnzymeConfig instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary

        if data is None:
            return cls()

        return cls(
            missed_cleavages=data.get('missed_cleavages', DEFAULT_MISSED_CLEAVAGES),
            min_len=data.get('min_len', DEFAULT_MIN_LEN),
            max_len=data.get('max_len', DEFAULT_MAX_LEN),
            cleave_at=data.get('cleave_at', DEFAULT_CLEAVE_AT),
            restrict=data.get('restrict', DEFAULT_RESTRICT),
            c_terminal=data.get('c_terminal', DEFAULT_C_TERMINAL),
            semi_enzymatic=data.get('semi_enzymatic', DEFAULT_SEMI_ENZYMATIC)
        )

    
    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_MISSED_CLEAVAGES.value, value=self.missed_cleavages)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_MIN_LEN.value, value=self.min_len)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_MAX_LEN.value, value=self.max_len)
        stp.text_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_CLEAVE_AT.value, value=self.cleave_at if self.cleave_at else "")
        stp.text_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_RESTRICT.value, value=self.restrict if self.restrict else "")
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_TERMINAL.value, value=self.enzyme_terminus)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.DATABASE_ENZYME_SEMI_ENZYMATIC.value, value=self.semi_enzymatic)


DEFAULT_LEVEL: int = 3
DEFAULT_SN: bool = False

class TMTSettings(BaseModel, frozen=True):
    """Settings for TMT quantification."""
    # Define constants for default values
    level: Optional[int] = Field(default=DEFAULT_LEVEL, ge=0, validate_default=True)
    sn: Optional[bool] = Field(default=DEFAULT_SN, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('level') is None:
            data['level'] = DEFAULT_LEVEL
        if data.get('sn') is None:
            data['sn'] = DEFAULT_SN
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        return {
            'level': self.level,
            'sn': self.sn
        }

    def to_url_params(self) -> Dict[str, Any]:
        return {
            SageQueryParam.QUANT_TMT_SETTINGS_LEVEL.value: self.level,
            SageQueryParam.QUANT_TMT_SETTINGS_SN.value: self.sn
        }
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'TMTSettings':
        """Create a TMTSettings instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            level=data.get(SageQueryParam.QUANT_TMT_SETTINGS_LEVEL.value, DEFAULT_LEVEL),
            sn=data.get(SageQueryParam.QUANT_TMT_SETTINGS_SN.value, DEFAULT_SN)
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TMTSettings':
        """Create a TMTSettings instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary

        if data is None:
            return cls()

        return cls(
            level=data.get('level', DEFAULT_LEVEL),
            sn=data.get('sn', DEFAULT_SN)
        )

    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.QUANT_TMT_SETTINGS_LEVEL.value, value=self.level)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.QUANT_TMT_SETTINGS_SN.value, value=self.sn)

# Define constants for default values
DEFAULT_PEAK_SCORING: str = "Hybrid"
DEFAULT_INTEGRATION: Literal["Sum", "Apex"] = "Sum"
DEFAULT_SPECTRAL_ANGLE: float = 0.7
DEFAULT_PPM_TOLERANCE: float = 5.0
DEFAULT_MOBILITY_PCT_TOLERANCE: float = 3.0
DEFAULT_COMBINE_CHARGE_STATES: bool = True

class LFQSettings(BaseModel, frozen=True):
    """Settings for Label-Free Quantification."""    
    peak_scoring: Optional[str] = Field(default=DEFAULT_PEAK_SCORING, validate_default=True)
    integration: Optional[Literal["Sum", "Apex"]] = Field(default=DEFAULT_INTEGRATION, validate_default=True)
    spectral_angle: Optional[float] = Field(default=DEFAULT_SPECTRAL_ANGLE, ge=0, le=1)
    ppm_tolerance: Optional[float] = Field(default=DEFAULT_PPM_TOLERANCE, ge=0)
    mobility_pct_tolerance: Optional[float] = Field(default=DEFAULT_MOBILITY_PCT_TOLERANCE, ge=0)
    combine_charge_states: Optional[bool] = Field(default=DEFAULT_COMBINE_CHARGE_STATES, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('peak_scoring') is None:
            data['peak_scoring'] = DEFAULT_PEAK_SCORING
        if data.get('integration') is None:
            data['integration'] = DEFAULT_INTEGRATION
        if data.get('spectral_angle') is None:
            data['spectral_angle'] = DEFAULT_SPECTRAL_ANGLE
        if data.get('ppm_tolerance') is None:
            data['ppm_tolerance'] = DEFAULT_PPM_TOLERANCE
        if data.get('mobility_pct_tolerance') is None:
            data['mobility_pct_tolerance'] = DEFAULT_MOBILITY_PCT_TOLERANCE
        if data.get('combine_charge_states') is None:
            data['combine_charge_states'] = DEFAULT_COMBINE_CHARGE_STATES
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        return {
            'peak_scoring': self.peak_scoring,
            'integration': self.integration,
            'spectral_angle': self.spectral_angle,
            'ppm_tolerance': self.ppm_tolerance,
            'mobility_pct_tolerance': self.mobility_pct_tolerance,
            'combine_charge_states': self.combine_charge_states
        }
    
    def to_url_params(self) -> Dict[str, Any]:
        return {
            SageQueryParam.QUANT_LFQ_SETTINGS_PEAK_SCORING.value: self.peak_scoring,
            SageQueryParam.QUANT_LFQ_SETTINGS_INTEGRATION.value: self.integration,
            SageQueryParam.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE.value: self.spectral_angle,
            SageQueryParam.QUANT_LFQ_SETTINGS_PPM_TOLERANCE.value: self.ppm_tolerance,
            SageQueryParam.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE.value: self.mobility_pct_tolerance,
            SageQueryParam.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES.value: self.combine_charge_states
        }
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'LFQSettings':
        """Create a LFQSettings instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            peak_scoring=data.get(SageQueryParam.QUANT_LFQ_SETTINGS_PEAK_SCORING.value, DEFAULT_PEAK_SCORING),
            integration=data.get(SageQueryParam.QUANT_LFQ_SETTINGS_INTEGRATION.value, DEFAULT_INTEGRATION),
            spectral_angle=data.get(SageQueryParam.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE.value, DEFAULT_SPECTRAL_ANGLE),
            ppm_tolerance=data.get(SageQueryParam.QUANT_LFQ_SETTINGS_PPM_TOLERANCE.value, DEFAULT_PPM_TOLERANCE),
            mobility_pct_tolerance=data.get(SageQueryParam.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE.value, DEFAULT_MOBILITY_PCT_TOLERANCE),
            combine_charge_states=data.get(SageQueryParam.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES.value, DEFAULT_COMBINE_CHARGE_STATES)
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LFQSettings':
        """Create a LFQSettings instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary

        if data is None:
            return cls()

        return cls(
            peak_scoring=data.get('peak_scoring', DEFAULT_PEAK_SCORING),
            integration=data.get('integration', DEFAULT_INTEGRATION),
            spectral_angle=data.get('spectral_angle', DEFAULT_SPECTRAL_ANGLE),
            ppm_tolerance=data.get('ppm_tolerance', DEFAULT_PPM_TOLERANCE),
            mobility_pct_tolerance=data.get('mobility_pct_tolerance', DEFAULT_MOBILITY_PCT_TOLERANCE),
            combine_charge_states=data.get('combine_charge_states', DEFAULT_COMBINE_CHARGE_STATES)
        )
    
    def update_url_params(self) -> None:
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_PEAK_SCORING.value, value=self.peak_scoring)
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_INTEGRATION.value, value=self.integration)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE.value, value=self.spectral_angle)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_PPM_TOLERANCE.value, value=self.ppm_tolerance)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE.value, value=self.mobility_pct_tolerance)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES.value, value=self.combine_charge_states)

DEFAULT_TMT: Optional[Literal["Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18"]] = None
DEFAULT_LFQ: bool = False

class QuantConfig(BaseModel, frozen=True):
    """Configuration for quantification."""
    # Define constants for default values
    
    tmt: Optional[Literal["Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18"]] = Field(default=None, validate_default=True)
    lfq: Optional[bool] = Field(default=DEFAULT_LFQ, validate_default=True)
    tmt_settings: Optional[TMTSettings] = Field(default_factory=TMTSettings, validate_default=True)
    lfq_settings: Optional[LFQSettings] = Field(default_factory=LFQSettings, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('tmt') is None:
            data['tmt'] = DEFAULT_TMT
        if data.get('lfq') is None:
            data['lfq'] = DEFAULT_LFQ
        if data.get('tmt_settings') is None:
            data['tmt_settings'] = TMTSettings()
        if data.get('lfq_settings') is None:
            data['lfq_settings'] = LFQSettings()
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        return {
            'tmt': self.tmt,
            'lfq': self.lfq,
            'tmt_settings': self.tmt_settings.to_dict() if self.tmt_settings else None,
            'lfq_settings': self.lfq_settings.to_dict() if self.lfq_settings else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuantConfig':
        """Create a QuantConfig instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary

        if data is None:
            return cls()

        return cls(
            tmt=data.get('tmt', DEFAULT_TMT),
            lfq=data.get('lfq', DEFAULT_LFQ),
            tmt_settings=TMTSettings.from_dict(data.get('tmt_settings', {})),
            lfq_settings=LFQSettings.from_dict(data.get('lfq_settings', {}))
        )
    
    def to_url_params(self) -> Dict[str, Any]:
        d = {
            SageQueryParam.QUANT_TMT.value: self.tmt,
            SageQueryParam.QUANT_LFQ.value: self.lfq,
        }

        if self.tmt_settings:
            d.update(self.tmt_settings.to_url_params())

        if self.lfq_settings:
            d.update(self.lfq_settings.to_url_params())

        return d

    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'QuantConfig':
        """Create a QuantConfig instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            tmt=data.get(SageQueryParam.QUANT_TMT.value, DEFAULT_TMT),
            lfq=data.get(SageQueryParam.QUANT_LFQ.value, DEFAULT_LFQ),
            tmt_settings=TMTSettings.from_dict(data.get('tmt_settings', {})),
            lfq_settings=LFQSettings.from_dict(data.get('lfq_settings', {}))
        )

    def update_url_params(self) -> None:
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.QUANT_TMT.value, value=self.tmt)
        stp.toggle.set_url_value(url_key=constants.SageQueryParam.QUANT_LFQ.value, value=self.lfq)
        self.tmt_settings.update_url_params()
        self.lfq_settings.update_url_params()


class ToleranceConfig(BaseModel, frozen=True):
    """Configuration for mass tolerance."""
    value: List[float] = Field(min_length=2, max_length=2, validate_default=True)
    unit: Literal["ppm", "da"] = Field(..., validate_default=True)

    @field_validator('value')
    @classmethod
    def validate_tolerance_values(cls, v):
        if len(v) != 2:
            raise ValueError("Tolerance value must be a list of exactly two floats")
        if v[0] >= 0 or v[1] <= 0:
            raise ValueError("Tolerance values must be in the format [negative, positive]")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        # should output {'ppm': [-10.0, 10.0]}
        return {self.unit: self.value}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToleranceConfig':
        """Create a ToleranceConfig instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary
        unit = next(iter(data))  # Get the first key (unit)
        return cls(
            value=data[unit],
            unit=unit
        )
       

    
class PrecursorToleranceConfig(ToleranceConfig, frozen=True):

    def to_url_params(self) -> Dict[str, Any]:
        """Convert to URL parameters."""
        return {
            SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value: self.value[0],
            SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value: self.value[1],
            SageQueryParam.PRECURSOR_TOL_UNIT.value: self.unit
        }


    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'ToleranceConfig':
        """Create a ToleranceConfig instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            value=[data[SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value], data[SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value]],
            unit=data[SageQueryParam.PRECURSOR_TOL_UNIT.value]
        )

    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.PRECURSOR_TOL_MIN_VALUE.value, value=self.value[0])
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.PRECURSOR_TOL_MAX_VALUE.value, value=self.value[1])
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.PRECURSOR_TOL_UNIT.value, value=self.unit)
    
class FragmentToleranceConfig(ToleranceConfig, frozen=True):
    def to_url_params(self) -> Dict[str, Any]:
        """Convert to URL parameters."""
        return {
            SageQueryParam.FRAGMENT_TOL_MIN_VALUE.value: self.value[0],
            SageQueryParam.FRAGMENT_TOL_MAX_VALUE.value: self.value[1],
            SageQueryParam.FRAGMENT_TOL_UNIT.value: self.unit
        }

    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'ToleranceConfig':
        """Create a ToleranceConfig instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            value=[data[SageQueryParam.FRAGMENT_TOL_MIN_VALUE.value], data[SageQueryParam.FRAGMENT_TOL_MAX_VALUE.value]],
            unit=data[SageQueryParam.FRAGMENT_TOL_UNIT.value]
        )
    
    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.FRAGMENT_TOL_MIN_VALUE.value, value=self.value[0])
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.FRAGMENT_TOL_MAX_VALUE.value, value=self.value[1])
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.FRAGMENT_TOL_UNIT.value, value=self.unit)

def validate_mod_key(mod: str) -> str:
    """Validate modification key format."""
    if len(mod) == 2:
        if mod[0] not in "^$[]":
            raise ValueError(f"Invalid modification key: {mod}. Must be a single amino acid or a valid modification format.")
        if mod[1] not in pt.AMINO_ACIDS:
            raise ValueError(f"Invalid modification key: {mod}. Must be a single amino acid.")
    elif len(mod) == 1 and mod not in pt.AMINO_ACIDS and mod not in "^$[]":
        raise ValueError(f"Invalid modification key: {mod}. Must be a single amino acid.")
    elif len(mod) > 2:
        raise ValueError(f"Invalid modification key: {mod}. Must be a single amino acid or a valid modification format.")
    return mod

# Define constants for default values
DEFAULT_BUCKET_SIZE: int = 32768
DEFAULT_PEPTIDE_MIN_MASS: float = 500.0
DEFAULT_PEPTIDE_MAX_MASS: float = 5000.0
DEFAULT_ION_KINDS: List[Literal["a", "b", "c", "x", "y", "z"]] = ["b", "y"]
DEFAULT_MIN_ION_INDEX: int = 2
DEFAULT_DECOY_TAG: str = "rev_"
DEFAULT_GENERATE_DECOYS: bool = True
DEFAULT_MAX_VARIABLE_MODS: int = 2

class DatabaseConfig(BaseModel, frozen=True):
    """Configuration for database search."""    
    bucket_size: Optional[int] = Field(default=DEFAULT_BUCKET_SIZE, gt=0, validate_default=True)
    fasta: str = Field(min_length=1, validate_default=True)
    enzyme: Optional[EnzymeConfig] = Field(default_factory=EnzymeConfig, validate_default=True)
    peptide_min_mass: Optional[float] = Field(default=DEFAULT_PEPTIDE_MIN_MASS, gt=0, validate_default=True)
    peptide_max_mass: Optional[float] = Field(default=DEFAULT_PEPTIDE_MAX_MASS, gt=0, validate_default=True)
    ion_kinds: Optional[List[Literal["a", "b", "c", "x", "y", "z"]]] = Field(default=DEFAULT_ION_KINDS, min_length=1, validate_default=True)
    min_ion_index: Optional[int] = Field(default=DEFAULT_MIN_ION_INDEX, ge=1, validate_default=True)
    decoy_tag: Optional[str] = Field(default=DEFAULT_DECOY_TAG, validate_default=True)
    generate_decoys: Optional[bool] = Field(default=DEFAULT_GENERATE_DECOYS, validate_default=True)
    static_mods: Optional[Dict[str, float]] = Field(default_factory=dict, validate_default=True)
    variable_mods: Optional[Dict[str, List[float]]] = Field(default_factory=dict, validate_default=True)
    max_variable_mods: Optional[int] = Field(default=DEFAULT_MAX_VARIABLE_MODS, ge=0, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('bucket_size') is None:
            data['bucket_size'] = DEFAULT_BUCKET_SIZE
        if data.get('fasta') is None:
            raise ValueError("Fasta file path must be provided")
        if data.get('enzyme') is None:
            data['enzyme'] = EnzymeConfig()
        if data.get('peptide_min_mass') is None:
            data['peptide_min_mass'] = DEFAULT_PEPTIDE_MIN_MASS
        if data.get('peptide_max_mass') is None:
            data['peptide_max_mass'] = DEFAULT_PEPTIDE_MAX_MASS
        if data.get('ion_kinds') is None:
            data['ion_kinds'] = DEFAULT_ION_KINDS
        if data.get('min_ion_index') is None:
            data['min_ion_index'] = DEFAULT_MIN_ION_INDEX
        if data.get('decoy_tag') is None:
            data['decoy_tag'] = DEFAULT_DECOY_TAG
        if data.get('generate_decoys') is None:
            data['generate_decoys'] = DEFAULT_GENERATE_DECOYS
        if data.get('static_mods') is None:
            data['static_mods'] = {}
        if data.get('variable_mods') is None:
            data['variable_mods'] = {}
        if data.get('max_variable_mods') is None:
            data['max_variable_mods'] = DEFAULT_MAX_VARIABLE_MODS
        return data

    @field_validator('static_mods')
    @classmethod
    def validate_static_mods(cls, v):
        if v is None:
            return {}
        validated_mods = {}
        for mod, mass in v.items():
            validate_mod_key(mod)
            if not isinstance(mass, (int, float)):
                raise ValueError(f"Modification mass must be a number: {mass}")
            validated_mods[mod] = float(mass)
        return validated_mods

    @field_validator('variable_mods')
    @classmethod
    def validate_variable_mods(cls, v):
        if v is None:
            return {}
        validated_mods = {}
        for mod, masses in v.items():
            validate_mod_key(mod)
            validated_masses = []
            for mass in masses:
                if not isinstance(mass, (int, float)):
                    raise ValueError(f"Modification mass must be a number: {mass}")
                validated_masses.append(float(mass))
            validated_mods[mod] = validated_masses
        return validated_mods

    
    @field_validator('ion_kinds')
    @classmethod
    def validate_restrict(cls, v):
        if v is None:
            return []
        valid_ions = ["a", "b", "c", "x", "y", "z"]
        for ion in v:
            if ion not in valid_ions:
                raise ValueError(f"Invalid ion kind: {ion}. Must be one of {valid_ions}.")

        # enseur no duplicates
        if len(v) != len(set(v)):
            raise ValueError("Ion kinds must be unique")
        
        return v

    @model_validator(mode='after')
    def validate_peptide_masses(self):
        if self.peptide_min_mass >= self.peptide_max_mass:
            raise ValueError("Peptide min mass must be less than max mass")
        return self
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        return self.model_dump()
    
    def to_url_params(self) -> Dict[str, Any]:
        d = {
            SageQueryParam.DATABASE_BUCKET_SIZE.value: self.bucket_size,
            SageQueryParam.DATABASE_FASTA.value: self.fasta,
            SageQueryParam.DATABASE_PEPTIDE_MIN_MASS.value: self.peptide_min_mass,
            SageQueryParam.DATABASE_PEPTIDE_MAX_MASS.value: self.peptide_max_mass,
            SageQueryParam.DATABASE_ION_KINDS.value: self.ion_kinds,
            SageQueryParam.DATABASE_MIN_ION_INDEX.value: self.min_ion_index,
            SageQueryParam.DATABASE_DECOY_TAG.value: self.decoy_tag,
            SageQueryParam.DATABASE_GENERATE_DECOYS.value: self.generate_decoys,
            SageQueryParam.DATABASE_STATIC_MODS.value: self.static_mods,
            SageQueryParam.DATABASE_VARIABLE_MODS.value: self.variable_mods,
            SageQueryParam.DATABASE_MAX_VARIABLE_MODS.value: self.max_variable_mods
        }

        d = {**d, **self.enzyme.to_url_params()}

        return d
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        """Create a DatabaseConfig instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            bucket_size=data.get(SageQueryParam.DATABASE_BUCKET_SIZE.value, DEFAULT_BUCKET_SIZE),
            fasta=data.get(SageQueryParam.DATABASE_FASTA.value, ""),
            enzyme=EnzymeConfig.from_url_params(data),
            peptide_min_mass=data.get(SageQueryParam.DATABASE_PEPTIDE_MIN_MASS.value, DEFAULT_PEPTIDE_MIN_MASS),
            peptide_max_mass=data.get(SageQueryParam.DATABASE_PEPTIDE_MAX_MASS.value, DEFAULT_PEPTIDE_MAX_MASS),
            ion_kinds=data.get(SageQueryParam.DATABASE_ION_KINDS.value, DEFAULT_ION_KINDS),
            min_ion_index=data.get(SageQueryParam.DATABASE_MIN_ION_INDEX.value, DEFAULT_MIN_ION_INDEX),
            decoy_tag=data.get(SageQueryParam.DATABASE_DECOY_TAG.value, DEFAULT_DECOY_TAG),
            generate_decoys=data.get(SageQueryParam.DATABASE_GENERATE_DECOYS.value, DEFAULT_GENERATE_DECOYS),
            static_mods=data.get(SageQueryParam.DATABASE_STATIC_MODS.value, {}),
            variable_mods=data.get(SageQueryParam.DATABASE_VARIABLE_MODS.value, {}),
            max_variable_mods=data.get(SageQueryParam.DATABASE_MAX_VARIABLE_MODS.value, DEFAULT_MAX_VARIABLE_MODS)
        )

    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        """Create a DatabaseConfig instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            bucket_size=data.get('bucket_size', DEFAULT_BUCKET_SIZE),
            fasta=data.get('fasta', ""),
            enzyme=EnzymeConfig.from_dict(data.get('enzyme', {})),
            peptide_min_mass=data.get('peptide_min_mass', DEFAULT_PEPTIDE_MIN_MASS),
            peptide_max_mass=data.get('peptide_max_mass', DEFAULT_PEPTIDE_MAX_MASS),
            ion_kinds=data.get('ion_kinds', DEFAULT_ION_KINDS),
            min_ion_index=data.get('min_ion_index', DEFAULT_MIN_ION_INDEX),
            decoy_tag=data.get('decoy_tag', DEFAULT_DECOY_TAG),
            generate_decoys=data.get('generate_decoys', DEFAULT_GENERATE_DECOYS),
            static_mods=data.get('static_mods', {}),
            variable_mods=data.get('variable_mods', {}),
            max_variable_mods=data.get('max_variable_mods', DEFAULT_MAX_VARIABLE_MODS)
        )

    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_BUCKET_SIZE.value, value=self.bucket_size)
        stp.text_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_FASTA.value, value=self.fasta)
        self.enzyme.update_url_params()
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_PEPTIDE_MIN_MASS.value, value=self.peptide_min_mass)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_PEPTIDE_MAX_MASS.value, value=self.peptide_max_mass)
        stp.segmented_control.set_url_value(url_key=constants.SageQueryParam.DATABASE_ION_KINDS.value, value=self.ion_kinds)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_MIN_ION_INDEX.value, value=self.min_ion_index)
        stp.text_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_DECOY_TAG.value, value=self.decoy_tag)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.DATABASE_GENERATE_DECOYS.value, value=self.generate_decoys)
        
        static_df = pd.DataFrame(list(self.static_mods.items()), columns=['Residue', 'Mass'])
        stp.data_editor.set_url_value(
            url_key=constants.SageQueryParam.DATABASE_STATIC_MODS.value,
            value=static_df
        )

        var_df = pd.DataFrame([(k, v) for k, vals in self.variable_mods.items() for v in vals], columns=['Residue', 'Mass'])
        stp.data_editor.set_url_value(
            url_key=constants.SageQueryParam.DATABASE_VARIABLE_MODS.value,
            value=var_df
        )

        stp.number_input.set_url_value(url_key=constants.SageQueryParam.DATABASE_MAX_VARIABLE_MODS.value, value=self.max_variable_mods)


# Define constants for Bruker default values
DEFAULT_MS1_MZ_PPM: float = 15.0
DEFAULT_MS1_IMS_PCT: float = 3.0


class BrukerMS1Config(BaseModel, frozen=True):
    """Configuration for Bruker MS1 data."""
    mz_ppm: Optional[float] = Field(default=DEFAULT_MS1_MZ_PPM, ge=0, validate_default=True)
    ims_pct: Optional[float] = Field(default=DEFAULT_MS1_IMS_PCT, ge=0, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('mz_ppm') is None:
            data['mz_ppm'] = DEFAULT_MS1_MZ_PPM
        if data.get('ims_pct') is None:
            data['ims_pct'] = DEFAULT_MS1_IMS_PCT
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
    
    def to_url_params(self) -> Dict[str, Any]:
        return {
            SageQueryParam.BRUKER_MS1_MZ_PPM.value: self.mz_ppm,
            SageQueryParam.BRUKER_MS1_IMS_PCT.value: self.ims_pct
        }
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'BrukerMS1Config':
        """Create a BrukerMS1Config instance from URL parameters."""
        return cls(
            mz_ppm=data.get(SageQueryParam.BRUKER_MS1_MZ_PPM.value, DEFAULT_MS1_MZ_PPM),
            ims_pct=data.get(SageQueryParam.BRUKER_MS1_IMS_PCT.value, DEFAULT_MS1_IMS_PCT)
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrukerMS1Config':
        """Create a BrukerMS1Config instance from a dictionary."""
        if data is None:
            return cls()
        
        return cls(
            mz_ppm=data.get('mz_ppm', DEFAULT_MS1_MZ_PPM),
            ims_pct=data.get('ims_pct', DEFAULT_MS1_IMS_PCT)
        )

    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS1_MZ_PPM.value, value=self.mz_ppm)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS1_IMS_PCT.value, value=self.ims_pct)


DEFAULT_SMOOTHING_WINDOW: int = 1
DEFAULT_CENTROIDING_WINDOW: int = 1
DEFAULT_CALIBRATION_TOLERANCE: float = 0.1
DEFAULT_CALIBRATE: bool = False

class SpectrumProcessingParams(BaseModel, frozen=True):
    """Configuration for spectrum processing parameters."""
    smoothing_window: Optional[int] = Field(default=DEFAULT_SMOOTHING_WINDOW, ge=1, validate_default=True)
    centroiding_window: Optional[int] = Field(default=DEFAULT_CENTROIDING_WINDOW, ge=1, validate_default=True)
    calibration_tolerance: Optional[float] = Field(default=DEFAULT_CALIBRATION_TOLERANCE, ge=0, validate_default=True)
    calibrate: Optional[bool] = Field(default=DEFAULT_CALIBRATE, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('smoothing_window') is None:
            data['smoothing_window'] = DEFAULT_SMOOTHING_WINDOW
        if data.get('centroiding_window') is None:
            data['centroiding_window'] = DEFAULT_CENTROIDING_WINDOW
        if data.get('calibration_tolerance') is None:
            data['calibration_tolerance'] = DEFAULT_CALIBRATION_TOLERANCE
        if data.get('calibrate') is None:
            data['calibrate'] = DEFAULT_CALIBRATE
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
    
    def to_url_params(self) -> Dict[str, Any]:
        return {
            SageQueryParam.BRUKER_MS2_SMOOTHING_WINDOW.value: self.smoothing_window,
            SageQueryParam.BRUKER_MS2_CENTROIDING_WINDOW.value: self.centroiding_window,
            SageQueryParam.BRUKER_MS2_CALIBRATION_TOLERANCE.value: self.calibration_tolerance,
            SageQueryParam.BRUKER_MS2_CALIBRATE.value: self.calibrate
        }
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'SpectrumProcessingParams':
        """Create a SpectrumProcessingParams instance from URL parameters."""
        return cls(
            smoothing_window=data.get(SageQueryParam.BRUKER_MS2_SMOOTHING_WINDOW.value, DEFAULT_SMOOTHING_WINDOW),
            centroiding_window=data.get(SageQueryParam.BRUKER_MS2_CENTROIDING_WINDOW.value, DEFAULT_CENTROIDING_WINDOW),
            calibration_tolerance=data.get(SageQueryParam.BRUKER_MS2_CALIBRATION_TOLERANCE.value, DEFAULT_CALIBRATION_TOLERANCE),
            calibrate=data.get(SageQueryParam.BRUKER_MS2_CALIBRATE.value, DEFAULT_CALIBRATE)
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpectrumProcessingParams':
        """Create a SpectrumProcessingParams instance from a dictionary."""
        if data is None:
            return cls()
        
        return cls(
            smoothing_window=data.get('smoothing_window', DEFAULT_SMOOTHING_WINDOW),
            centroiding_window=data.get('centroiding_window', DEFAULT_CENTROIDING_WINDOW),
            calibration_tolerance=data.get('calibration_tolerance', DEFAULT_CALIBRATION_TOLERANCE),
            calibrate=data.get('calibrate', DEFAULT_CALIBRATE)
        )

    def update_url_params(self) -> None:
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_SMOOTHING_WINDOW.value, value=self.smoothing_window)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_CENTROIDING_WINDOW.value, value=self.centroiding_window)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_CALIBRATION_TOLERANCE.value, value=self.calibration_tolerance)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_CALIBRATE.value, value=self.calibrate)


DEFAULT_MOBILITY_WIDTH: float = 0.1
DEFAULT_MOBILITY_OVERLAP: float = 0.005
DEFAULT_UNKNOWN_VALUE: Any = None

class UniformMobilityParams(BaseModel, frozen=True):
    """Configuration for uniform mobility parameters."""
    mobility_width: Optional[float] = Field(default=DEFAULT_MOBILITY_WIDTH, ge=0, validate_default=True)
    mobility_overlap: Optional[float] = Field(default=DEFAULT_MOBILITY_OVERLAP, ge=0, validate_default=True)
    uknown_value: Optional[Any] = Field(default=DEFAULT_UNKNOWN_VALUE, validate_default=True)

    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'UniformMobility': [[self.mobility_width, self.mobility_overlap], self.uknown_value]}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniformMobilityParams':
        """Create a UniformMobilityParams instance from a dictionary."""
        if data is None:
            return cls()
        
        mobility_params = data.get('UniformMobility', [[DEFAULT_MOBILITY_WIDTH, DEFAULT_MOBILITY_OVERLAP], DEFAULT_UNKNOWN_VALUE])
        if not isinstance(mobility_params, list) or len(mobility_params) != 2:
            raise ValueError("UniformMobility must be a list of two elements: [mobility_width, mobility_overlap]")
        if len(mobility_params[0]) != 2:
            raise ValueError("UniformMobility first element must be a list of two floats: [mobility_width, mobility_overlap]")
        
        return cls(
            mobility_width=mobility_params[0][0],
            mobility_overlap=mobility_params[0][1],
            uknown_value=mobility_params[1]
        )
    
    
    def to_url_params(self) -> Dict[str, Any]:
        """Convert to URL parameters."""
        return {
            SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_WIDTH.value: self.mobility_width,
            SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_OVERLAP.value: self.mobility_overlap,
            SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_UNKNOWN.value: self.uknown_value
        }

    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'UniformMobilityParams':
        """Create a UniformMobilityParams instance from URL parameters."""
        return cls(
            mobility_width=data.get(SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_WIDTH.value, DEFAULT_MOBILITY_WIDTH),
            mobility_overlap=data.get(SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_OVERLAP.value, DEFAULT_MOBILITY_OVERLAP),
            uknown_value=data.get(SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_UNKNOWN.value, DEFAULT_UNKNOWN_VALUE)
        )
    
    def update_url_params(self) -> None:
        """Update URL parameters for uniform mobility."""
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_WIDTH.value, value=self.mobility_width)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_OVERLAP.value, value=self.mobility_overlap)
        #stp.text_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_UNIFORM_MOBILITY_UNKNOWN.value, value=self.uknown_value)
    
DEFAULT_NUM: int = 10

class EvenMobilityParams(BaseModel, frozen=True):

    """Configuration for even mobility parameters."""
    num: Optional[int] = Field(default=DEFAULT_NUM, ge=1, validate_default=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"Even": self.num}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvenMobilityParams':
        """Create a EvenMobilityParams instance from a dictionary."""
        if data is None:
            return cls()
        
        return cls(
            num=data.get('Even', DEFAULT_NUM)
        )
    
    def to_url_params(self) -> Dict[str, Any]:
        """Convert to URL parameters."""
        return {
            SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_EVEN_NUM.value: self.num
        }
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'EvenMobilityParams':
        """Create a EvenMobilityParams instance from URL parameters."""
        return cls(
            num=data.get(SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_EVEN_NUM.value, DEFAULT_NUM)
        )

    def update_url_params(self) -> None:
        """Update URL parameters for even mobility."""
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_EVEN_NUM.value, value=self.num)

DEFAULT_FRAME_SPLITTING_TYPE: Literal["Quadrupole", "Window"] = "Quadrupole"
DEFAULT_FRAME_SPLITTING_VALUE: Optional[Union[UniformMobilityParams, EvenMobilityParams]] = None

class FrameSplittingParams(BaseModel, frozen=True):
    """Configuration for frame splitting parameters."""
    split_type: Literal["Quadrupole", "Window"] = Field(default=DEFAULT_FRAME_SPLITTING_TYPE, validate_default=True)
    value: Optional[Union[UniformMobilityParams, EvenMobilityParams]] = Field(default=DEFAULT_FRAME_SPLITTING_VALUE, validate_default=True)


    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            self.split_type: self.value.to_dict() if self.value else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameSplittingParams':
        """Create a FrameSplittingParams instance from a dictionary."""
        if data is None:
            return cls()
        
        keys = list(data.keys())
        if len(keys) == 0:
            type_ = DEFAULT_FRAME_SPLITTING_TYPE
            value = None
        else:
            type_ = keys[0]
            
        if type_ not in ["Quadrupole", "Window"]:
            raise ValueError(f"Frame splitting type must be either 'Quadrupole' or 'Window', got '{type_}'")
        
        value = data.get(type_, None)
        if value is None:
            pass
        elif type_ == "UniformMobility":
            value = UniformMobilityParams.from_dict(data)
        elif type_ == "Even":
            value = EvenMobilityParams.from_dict(data)

        return cls(
            split_type=type_,
            value=value
        )
        
    def to_url_params(self) -> Dict[str, Any]:
        """Convert to URL parameters."""
        # type = quad | window
        # update underlying dtypes
        d = {
            SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_TYPE.value: self.split_type,
        }
        if self.value is None:
            d.update({SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value: None})
        else:
            d.update(self.value.to_url_params())
        return d

    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'FrameSplittingParams':
        """Create a FrameSplittingParams instance from URL parameters."""
        major_type = data.get(SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_TYPE.value, DEFAULT_FRAME_SPLITTING_TYPE)
        minor_type = data.get(SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value, "None")
        
        if minor_type == "None":
            value = None
        elif minor_type == "UniformMobility":
            value = UniformMobilityParams.from_url_params(data)
        elif minor_type == "Even":
            value = EvenMobilityParams.from_url_params(data)


        return cls(
            split_type=major_type,
            value=value
        )
    
    def update_url_params(self) -> None:
        """Update URL parameters for frame splitting."""
        stp.selectbox.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_TYPE.value, value=self.split_type)
        
        if self.value is None:
            stp.selectbox.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value, value=None)
        elif isinstance(self.value, UniformMobilityParams):
            self.value.update_url_params()
            stp.selectbox.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value, value="UniformMobility")
        elif isinstance(self.value, EvenMobilityParams):
            self.value.update_url_params()
            stp.selectbox.set_url_value(url_key=constants.SageQueryParam.BRUKER_MS2_FRAME_SPLITTING_MINOR_TYPE.value, value="Even")
class BrukerMS2Config(BaseModel, frozen=True):
    """Configuration for Bruker MS2 data."""
    spectrum_processing_params: Optional[SpectrumProcessingParams] = Field(default_factory=SpectrumProcessingParams, validate_default=True)
    frame_splitting_params: Optional[FrameSplittingParams] = Field(default_factory=FrameSplittingParams, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('spectrum_processing_params') is None:
            data['spectrum_processing_params'] = SpectrumProcessingParams()
        if data.get('frame_splitting_params') is None:
            data['frame_splitting_params'] = FrameSplittingParams()
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'spectrum_processing_params': self.spectrum_processing_params.to_dict(),
            'frame_splitting_params': self.frame_splitting_params.to_dict()
        }
    
    def to_url_params(self) -> Dict[str, Any]:
        result = {}
        result.update(self.spectrum_processing_params.to_url_params())
        result.update(self.frame_splitting_params.to_url_params())
        return result
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'BrukerMS2Config':
        """Create a BrukerMS2Config instance from URL parameters."""
        return cls(
            spectrum_processing_params=SpectrumProcessingParams.from_url_params(data),
            frame_splitting_params=FrameSplittingParams.from_url_params(data)
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrukerMS2Config':
        """Create a BrukerMS2Config instance from a dictionary."""
        if data is None:
            return cls()
        
        return cls(
            spectrum_processing_params=SpectrumProcessingParams.from_dict(data.get('spectrum_processing_params', {})),
            frame_splitting_params=FrameSplittingParams.from_dict(data.get('frame_splitting_params', {}))
        )

    def update_url_params(self) -> None:
        self.spectrum_processing_params.update_url_params()
        self.frame_splitting_params.update_url_params()

class BrukerConfig(BaseModel, frozen=True):
    """Configuration for Bruker data processing."""
    ms1: Optional[BrukerMS1Config] = Field(default_factory=BrukerMS1Config, validate_default=True)
    ms2: Optional[BrukerMS2Config] = Field(default_factory=BrukerMS2Config, validate_default=True)

    #@model_validator(mode='before')
    def set_default_for_none_fields(cls, data: Any) -> Any:
        """Replace None values with their defaults"""
        if data.get('ms1') is None:
            data['ms1'] = BrukerMS1Config()
        if data.get('ms2') is None:
            data['ms2'] = BrukerMS2Config()
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ms1': self.ms1.to_dict(),
            'ms2': self.ms2.to_dict()
        }
    
    def to_url_params(self) -> Dict[str, Any]:
        result = {}
        result.update(self.ms1.to_url_params())
        result.update(self.ms2.to_url_params())
        return result
    
    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'BrukerConfig':
        """Create a BrukerConfig instance from URL parameters."""
        return cls(
            ms1=BrukerMS1Config.from_url_params(data),
            ms2=BrukerMS2Config.from_url_params(data)
        )
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrukerConfig':
        """Create a BrukerConfig instance from a dictionary."""
        if data is None:
            return cls()
        
        return cls(
            ms1=BrukerMS1Config.from_dict(data.get('ms1', {})),
            ms2=BrukerMS2Config.from_dict(data.get('ms2', {}))
        )

    def update_url_params(self) -> None:
        self.ms1.update_url_params()
        self.ms2.update_url_params()

DEFAULT_PRECURSOR_CHARGE: Tuple[int, int] = (2, 4)
DEFAULT_ISOTOPE_ERRORS: Tuple[int, int] = (0, 0)
DEFAULT_DEISOTOPE: bool = False
DEFAULT_CHIMERA: bool = False
DEFAULT_WIDE_WINDOW: bool = False
DEFAULT_PREDICT_RT: bool = True
DEFAULT_MIN_PEAKS: int = 15
DEFAULT_MAX_PEAKS: int = 150
DEFAULT_MIN_MATCHED_PEAKS: int = 4
DEFAULT_REPORT_PSMS: int = 1
DEFAULT_OUTPUT_DIRECTORY: str = "."

class SageConfig(BaseModel, frozen=True):
    """Complete configuration for Sage search engine."""
    # Define constants for default values
    
    database: Optional[DatabaseConfig] = Field(default_factory=DatabaseConfig, validate_default=True)
    precursor_tol: PrecursorToleranceConfig
    fragment_tol: FragmentToleranceConfig
    output_directory: Optional[str] = Field(default=DEFAULT_OUTPUT_DIRECTORY, min_length=1, validate_default=True)
    mzml_paths: Optional[List[str]] = Field(default_factory=list, min_length=0, validate_default=True)
    precursor_charge: Tuple[int, int] = Field(default=DEFAULT_PRECURSOR_CHARGE, min_length=2, max_length=2, validate_default=True)
    isotope_errors: Tuple[int, int] = Field(default=DEFAULT_ISOTOPE_ERRORS, min_length=2, max_length=2, validate_default=True)
    deisotope: Optional[bool] = Field(default=DEFAULT_DEISOTOPE, validate_default=True)
    chimera: Optional[bool] = Field(default=DEFAULT_CHIMERA, validate_default=True)
    wide_window: Optional[bool] = Field(default=DEFAULT_WIDE_WINDOW, validate_default=True)
    predict_rt: Optional[bool] = Field(default=DEFAULT_PREDICT_RT, validate_default=True)
    min_peaks: Optional[int] = Field(default=DEFAULT_MIN_PEAKS, gt=0)
    max_peaks: Optional[int] = Field(default=DEFAULT_MAX_PEAKS, gt=0)
    min_matched_peaks: Optional[int] = Field(default=DEFAULT_MIN_MATCHED_PEAKS, gt=0)
    max_fragment_charge: Optional[int] = Field(default=None, ge=1, validate_default=True)
    report_psms: Optional[int] = Field(default=DEFAULT_REPORT_PSMS, gt=0)
    quant: Optional[QuantConfig] = Field(default_factory=QuantConfig, validate_default=True)
    bruker_config: Optional[BrukerConfig] = Field(default_factory=BrukerConfig, validate_default=True)

    @field_validator('mzml_paths')
    @classmethod
    def validate_mzml_paths(cls, v):
        if not all(isinstance(path, str) and path.strip() for path in v):
            raise ValueError("All mzML paths must be non-empty strings")
        return v
    
    @field_validator('precursor_charge')
    @classmethod
    def validate_precursor_charge(cls, v):
        if len(v) != 2 or not all(isinstance(c, int) for c in v):
            raise ValueError("Precursor charge must be a tuple of two positive integers")
        
        if v[0] > v[1]:
            raise ValueError("Precursor charge range must be in the format (min, max) where min <= max")

        return tuple(v)
    
    @field_validator('isotope_errors')
    @classmethod
    def validate_isotope_errors(cls, v):
        if len(v) != 2 or not all(isinstance(e, int) for e in v):
            raise ValueError("Isotope errors must be a tuple of two integers")
        
        if v[0] > v[1]:
            raise ValueError("Isotope error range must be in the format (min, max) where min <= max")

        return tuple(v)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary excluding the DEFAULT constants."""
        result = {
            'database': self.database.to_dict(),
            'precursor_tol': self.precursor_tol.to_dict(),
            'fragment_tol': self.fragment_tol.to_dict(),
            'output_directory': self.output_directory,
            'mzml_paths': self.mzml_paths,
            'precursor_charge': self.precursor_charge,
            'isotope_errors': self.isotope_errors,
            'deisotope': self.deisotope,
            'chimera': self.chimera,
            'wide_window': self.wide_window,
            'predict_rt': self.predict_rt,
            'min_peaks': self.min_peaks,
            'max_peaks': self.max_peaks,
            'min_matched_peaks': self.min_matched_peaks,
            'max_fragment_charge': self.max_fragment_charge,
            'report_psms': self.report_psms,
            'quant': self.quant.to_dict(),
            'bruker_config': self.bruker_config.to_dict()
        }
    
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SageConfig':
        """Create a SageConfig instance from a dictionary."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            database=DatabaseConfig.from_dict(data.get('database', {})),
            precursor_tol=PrecursorToleranceConfig.from_dict(data.get('precursor_tol', {})),
            fragment_tol=FragmentToleranceConfig.from_dict(data.get('fragment_tol', {})),
            output_directory=data.get('output_directory', DEFAULT_OUTPUT_DIRECTORY),
            mzml_paths=data.get('mzml_paths', []),
            precursor_charge=tuple(data.get('precursor_charge', DEFAULT_PRECURSOR_CHARGE)),
            isotope_errors=tuple(data.get('isotope_errors', DEFAULT_ISOTOPE_ERRORS)),
            deisotope=data.get('deisotope', DEFAULT_DEISOTOPE),
            chimera=data.get('chimera', DEFAULT_CHIMERA),
            wide_window=data.get('wide_window', DEFAULT_WIDE_WINDOW),
            predict_rt=data.get('predict_rt', DEFAULT_PREDICT_RT),
            min_peaks=data.get('min_peaks', DEFAULT_MIN_PEAKS),
            max_peaks=data.get('max_peaks', DEFAULT_MAX_PEAKS),
            min_matched_peaks=data.get('min_matched_peaks', DEFAULT_MIN_MATCHED_PEAKS),
            max_fragment_charge=data.get('max_fragment_charge'),
            report_psms=data.get('report_psms', DEFAULT_REPORT_PSMS),
            quant=QuantConfig.from_dict(data.get('quant', {})),
            bruker_config=BrukerConfig.from_dict(data.get('bruker_config', {}))
        )

    def to_url_params(self) -> Dict[str, Any]:
        d = {
            SageQueryParam.OUTPUT_DIRECTORY.value: self.output_directory,
            SageQueryParam.MZML_PATHS.value: self.mzml_paths,
            SageQueryParam.PRECURSOR_MIN_CHARGE.value: self.precursor_charge[0],
            SageQueryParam.PRECURSOR_MAX_CHARGE.value: self.precursor_charge[1],
            SageQueryParam.ISOTOPE_MIN_ERROR.value: self.isotope_errors[0],
            SageQueryParam.ISOTOPE_MAX_ERROR.value: self.isotope_errors[1],
            SageQueryParam.DEISOTOPE.value: self.deisotope,
            SageQueryParam.CHIMERA.value: self.chimera,
            SageQueryParam.WIDE_WINDOW.value: self.wide_window,
            SageQueryParam.PREDICT_RT.value: self.predict_rt,
            SageQueryParam.MIN_PEAKS.value: self.min_peaks,
            SageQueryParam.MAX_PEAKS.value: self.max_peaks,
            SageQueryParam.MIN_MATCHED_PEAKS.value: self.min_matched_peaks,
            SageQueryParam.MAX_FRAGMENT_CHARGE.value: self.max_fragment_charge,
            SageQueryParam.REPORT_PSMS.value: self.report_psms
        }

        d = {**d, **self.quant.to_url_params()}
        d = {**d, **self.database.to_url_params()}
        d = {**d, **self.precursor_tol.to_url_params()}
        d = {**d, **self.fragment_tol.to_url_params()}
        d = {**d, **self.bruker_config.to_url_params()}

        return d

    @classmethod
    def from_url_params(cls, data: Dict[str, Any]) -> 'SageConfig':
        """Create a SageConfig instance from URL parameters."""
        # Ensure all fields are present, using defaults where necessary
        return cls(
            database=DatabaseConfig.from_url_params(data),
            precursor_tol=PrecursorToleranceConfig.from_url_params(data),
            fragment_tol=FragmentToleranceConfig.from_url_params(data),
            output_directory=data.get(SageQueryParam.OUTPUT_DIRECTORY.value, DEFAULT_OUTPUT_DIRECTORY),
            mzml_paths=data.get(SageQueryParam.MZML_PATHS.value, []),
            precursor_charge=(data.get(SageQueryParam.PRECURSOR_MIN_CHARGE.value, DEFAULT_PRECURSOR_CHARGE[0]),
                              data.get(SageQueryParam.PRECURSOR_MAX_CHARGE.value, DEFAULT_PRECURSOR_CHARGE[1])),
            isotope_errors=(data.get(SageQueryParam.ISOTOPE_MIN_ERROR.value, DEFAULT_ISOTOPE_ERRORS[0]),
                            data.get(SageQueryParam.ISOTOPE_MAX_ERROR.value, DEFAULT_ISOTOPE_ERRORS[1])),
            deisotope=data.get(SageQueryParam.DEISOTOPE.value, DEFAULT_DEISOTOPE),
            chimera=data.get(SageQueryParam.CHIMERA.value, DEFAULT_CHIMERA),
            wide_window=data.get(SageQueryParam.WIDE_WINDOW.value, DEFAULT_WIDE_WINDOW),
            predict_rt=data.get(SageQueryParam.PREDICT_RT.value, DEFAULT_PREDICT_RT),
            min_peaks=data.get(SageQueryParam.MIN_PEAKS.value, DEFAULT_MIN_PEAKS),
            max_peaks=data.get(SageQueryParam.MAX_PEAKS.value, DEFAULT_MAX_PEAKS),
            min_matched_peaks=data.get(SageQueryParam.MIN_MATCHED_PEAKS.value, DEFAULT_MIN_MATCHED_PEAKS),
            max_fragment_charge=data.get(SageQueryParam.MAX_FRAGMENT_CHARGE.value),
            report_psms=data.get(SageQueryParam.REPORT_PSMS.value, DEFAULT_REPORT_PSMS),
            quant=QuantConfig.from_url_params(data),
            bruker_config=BrukerConfig.from_url_params(data)
        )

    def update_url_params(self) -> None:

        output_dir = Path(self.output_directory)

        parent_folder = output_dir.parent if output_dir.parent != Path('.') else None
        base_folder = output_dir.name if output_dir.name != '.' else None

        stp.text_input.set_url_value(url_key=constants.SageQueryParam.OUTPUT_DIRECTORY.value, value=str(parent_folder))
        stp.text_input.set_url_value(url_key=constants.SageQueryParam.SEARCH_NAME.value, value=str(base_folder))

        mzml_df = pd.DataFrame(self.mzml_paths, columns=['mzML Path'])
        stp.data_editor.set_url_value(url_key=constants.SageQueryParam.MZML_PATHS.value, value=mzml_df)

        stp.number_input.set_url_value(url_key=constants.SageQueryParam.PRECURSOR_MIN_CHARGE.value, value=self.precursor_charge[0])
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.PRECURSOR_MAX_CHARGE.value, value=self.precursor_charge[1])
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.ISOTOPE_MIN_ERROR.value, value=self.isotope_errors[0])
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.ISOTOPE_MAX_ERROR.value, value=self.isotope_errors[1])
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.DEISOTOPE.value, value=self.deisotope)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.CHIMERA.value, value=self.chimera)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.WIDE_WINDOW.value, value=self.wide_window)
        stp.checkbox.set_url_value(url_key=constants.SageQueryParam.PREDICT_RT.value, value=self.predict_rt)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.MIN_PEAKS.value, value=self.min_peaks)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.MAX_PEAKS.value, value=self.max_peaks)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.MIN_MATCHED_PEAKS.value, value=self.min_matched_peaks)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.MAX_FRAGMENT_CHARGE.value, value=self.max_fragment_charge)
        stp.number_input.set_url_value(url_key=constants.SageQueryParam.REPORT_PSMS.value, value=self.report_psms)

        self.quant.update_url_params()
        self.database.update_url_params()
        self.precursor_tol.update_url_params()
        self.fragment_tol.update_url_params()     
        self.bruker_config.update_url_params()  

# Example usage and factory functions
def create_default_config(
    fasta_path: str,
) -> SageConfig:
    """Create a default Sage configuration."""
    return SageConfig(
        database=DatabaseConfig(
            fasta=fasta_path
        ),
        precursor_tol=PrecursorToleranceConfig(value=[-10.0, 10.0], unit="ppm"),
        fragment_tol=FragmentToleranceConfig(value=[-10.0, 10.0], unit="ppm"),
    )

if __name__ == "__main__":
    # Example usage
    sage_config = create_default_config(
        fasta_path="example.fasta"
    )
    print(sage_config.model_dump_json(indent=2))
    print(sage_config.to_dict())
    print(SageConfig.from_dict(sage_config.to_dict()).model_dump_json(indent=2))


    db_config = DatabaseConfig(
        bucket_size=None,
        fasta="example.fasta",
        enzyme=EnzymeConfig(
            missed_cleavages=2,
            min_len=5,
            max_len=50,
            cleave_at="KR",
            restrict="P",
            c_terminal=True,
            semi_enzymatic=False
        ),
        peptide_min_mass=500.0,
        peptide_max_mass=5000.0,
        ion_kinds=["b", "y"],
        min_ion_index=2,
        decoy_tag="rev_",
        generate_decoys=True,
        static_mods={"C": 57.02146},
        variable_mods={"M": [15.99491, 16.99913]},
        max_variable_mods=2
    )

    json_data = '{"bucket_size": 32768, "fasta": "example.fasta", "enzyme": {"missed_cleavages": 2, "min_len": 5, "max_len": 50, "cleave_at": "KR", "restrict": "P", "c_terminal": true, "semi_enzymatic": false}, "peptide_min_mass": 500.0, "peptide_max_mass": 5000.0, "ion_kinds": ["b", "y"], "min_ion_index": 2, "decoy_tag": "rev_", "generate_decoys": true, "static_mods": {"C": 57.02146}, "variable_mods": {"M": [15.99491, 16.99913]}, "max_variable_mods": 2}'
    print(DatabaseConfig.model_validate_json(json_data))

    print(db_config.model_dump_json(indent=2))

    print(sage_config.to_url_params())

    for key in sage_config.to_url_params():
        print(f"{key.upper()} = '{key}'")