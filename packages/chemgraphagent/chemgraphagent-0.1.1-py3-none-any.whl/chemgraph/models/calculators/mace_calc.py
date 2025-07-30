"""MACE foundation models parameters for ChemGraph
Reference: https://github.com/ACEsuit/mace/blob/main/mace/calculators/foundations_models.py"""

import os
from pathlib import Path
from typing import Optional, Union
from pydantic import BaseModel, Field
import torch


class MaceCalc(BaseModel):
    """MACE (Message-passing Atomic and Continuous Environment) calculator configuration.

    This class defines the configuration parameters for MACE machine learning models
    used in molecular simulations. It supports different calculator types including
    MACE-MP, MACE-OFF, and MACE-ANI-CC.

    Parameters
    ----------
    calculator_type : str, optional
        Type of calculator to use. Options: 'mace_mp' (default), 'mace_off', or 'mace_anicc'
    model : str or Path, optional
        Name or path to the model file. If None, uses default model for selected calculator type.
    device : str, optional
        Device to use for calculations ('cpu' or 'cuda'), by default 'cuda' if available
    default_dtype : str, optional
        Default data type for the model ('float32' or 'float64'), by default 'float64'
    dispersion : bool, optional
        Whether to use D3 dispersion corrections (only for 'mace_mp'), by default False
    damping : str, optional
        Damping function for dispersion correction (only for 'mace_mp'),
        options: ['zero', 'bj', 'zerom', 'bjm'], by default 'bj'
    dispersion_xc : str, optional
        Exchange-correlation functional for D3 dispersion corrections (only for 'mace_mp'),
        by default 'pbe'
    dispersion_cutoff : float, optional
        Cutoff radius in Bohr for D3 dispersion corrections (only for 'mace_mp'),
        by default 21.167088422553647 (40.0 * units.Bohr)
    """

    calculator_type: str = Field(
        default="mace_mp",
        description="Type of calculator. Options: 'mace_mp' (default) or 'mace_off'.",
    )
    model: Optional[Union[str, Path]] = Field(
        default=None,
        description="Path to the model. If None, it will use the default model for the selected calculator type. "
        "Options: 'small', 'medium', 'large', 'small-0b', 'medium-0b', 'small-0b2', 'medium-0b2','large-0b2', 'medium-0b3', 'medium-mpa-0', 'medium-omat-0', 'mace-matpes-pbe-0', 'mace-matpes-r2scan-0'",
    )
    device: str = Field(
        default="cuda" if torch.cuda.is_available() else "cpu",
        description="Device to use for calculations (e.g., 'cpu', 'cuda').",
    )
    default_dtype: str = Field(
        default="float64",
        description="Default dtype for the model (float32 or float64).",
    )
    dispersion: bool = Field(
        default=False,
        description="Whether to use D3 dispersion corrections (only for 'mace_mp').",
    )
    damping: str = Field(
        default="bj",
        description="Damping function for dispersion correction (only for 'mace_mp'). Options: ['zero', 'bj', 'zerom', 'bjm'].",
    )
    dispersion_xc: str = Field(
        default="pbe",
        description="Exchange-correlation functional for D3 dispersion corrections (only for 'mace_mp').",
    )
    dispersion_cutoff: float = Field(
        default=21.167088422553647,  # Equivalent to 40.0 * units.Bohr,
        description="Cutoff radius in Bohr for D3 dispersion corrections (only for 'mace_mp').",
    )

    def get_calculator(self):
        """Get the appropriate MACECalculator instance based on the selected calculator type.

        Returns
        -------
        MACECalculator
            An instance of the appropriate MACE calculator

        Raises
        ------
        ValueError
            If an invalid calculator_type is specified
        """
        from mace.modules.models import ScaleShiftMACE

        # Allow loading slice and ScaleShiftMACE objects for compatibility with older model files
        torch.serialization.add_safe_globals([slice, ScaleShiftMACE])

        # Force torch to disable weights_only loading (allows full pickle loads) for MACE models
        os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"

        if self.calculator_type == "mace_mp":
            from mace.calculators import mace_mp

            return mace_mp(
                model=self.model,
                device=self.device,
                default_dtype=self.default_dtype,
                dispersion=self.dispersion,
                damping=self.damping,
                dispersion_xc=self.dispersion_xc,
                dispersion_cutoff=self.dispersion_cutoff,
            )
        elif self.calculator_type == "mace_off":
            from mace.calculators import mace_off

            return mace_off(
                model=self.model,
                device=self.device,
                default_dtype=self.default_dtype,
            )
        elif self.calculator_type == "mace_anicc":
            from mace.calculators import mace_anicc

            return mace_anicc(
                device=self.device,
                model_path=self.model,
            )
        else:
            raise ValueError(
                "Invalid calculator_type. Choose 'mace_mp' or 'mace_off' or 'mace_anicc'."
            )
