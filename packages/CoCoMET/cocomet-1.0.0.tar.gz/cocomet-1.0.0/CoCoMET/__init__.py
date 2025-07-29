"""
<p style="text-align: center">===============Welcome To CoCoMET===============</p>

<p style="text-align: center">A toolkit of the Advanced Study of Cloud and Environment iNTerations (ASCENT) program.</p>

<p style="text-align: center">This project was supported by the U.S. Department of Energy (DOE) Early Career Research Program, Atmospheric System Research (ASR) program, and the Office of Workforce Development for Teachers and Scientists (WDTS) under the Science Undergraduate Laboratory Internships Program (SULI).</p>

<p style="text-align: center">If you are using this software for a publication, please cite: Hahn et al. (2025) https://doi.org/10.5194/egusphere-2025-1328</p>

<p style="text-align: center">=============================================</p>
"""

__all__ = [
    "user_interface_layer",
    "run_tracker_wrapper",
    "goes_load",
    "mesonh_load",
    "multi_nexrad_load",
    "nexrad_load",
    "rams_load",
    "standard_radar_load",
    "wrf_load",
    "mesonh_calculate_products",
    "rams_calculate_products",
    "wrf_calculate_products",
    "goes_tobac",
    "mesonh_tobac",
    "multi_nexrad_tobac",
    "nexrad_tobac",
    "rams_tobac",
    "standard_radar_tobac",
    "wrf_tobac",
    "mesonh_moaap",
    "rams_moaap",
    "wrf_moaap",
    "mesonh_tams",
    "rams_tams",
    "wrf_tams",
    "tracker_output_translation_layer",
    "analysis",
    "post_processor",
    "user_utils",
]

from CoCoMET.analysis.calc_var import calc_var
from CoCoMET.MOAAP import moaap
from CoCoMET.TAMS import run
from CoCoMET.user_utils import *

from .goes_load import *
from .goes_tobac import *
from .mesonh_calculate_products import *
from .mesonh_load import *
from .mesonh_moaap import *
from .mesonh_tams import *
from .mesonh_tobac import *
from .mesonhcube import *
from .multi_nexrad_load import *
from .multi_nexrad_tobac import *
from .nexrad_load import *
from .nexrad_tobac import *
from .post_processor import *
from .rams_calculate_products import *
from .rams_configure import *
from .rams_load import *
from .rams_moaap import *
from .rams_tams import *
from .rams_tobac import *
from .ramscube import *
from .run_tracker_wrapper import *
from .standard_radar_load import *
from .standard_radar_tobac import *
from .tracker_output_translation_layer import *
from .user_interface_layer import *
from .wrf_calculate_products import *
from .wrf_load import *
from .wrf_moaap import *
from .wrf_tams import *
from .wrf_tobac import *
from .wrfcube import *

print(
    "===============Welcome To CoCoMET===============\n\n"
    + "A toolkit of the Advanced Study of Cloud and Environment iNTerations (ASCENT) program.\n\n"
    + "This project was supported by the U.S. Department of Energy (DOE) Early Career Research Program, Atmospheric System Research (ASR) program, and the Office of Workforce Development for Teachers and Scientists (WDTS) under the Science Undergraduate Laboratory Internships Program (SULI).\n\n"
    + "If you are using this software for a publication, please cite: Hahn et al. (2025) https://doi.org/10.5194/egusphere-2025-1328\n\n"
    "=============================================\n"
)
