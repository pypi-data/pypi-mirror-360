"""
Author: HECE - University of Liege, Pierre Archambeau, Christophe Dessers
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

# Constants defined for the postProcessHydology procedures
from ..PyTranslate import _

# Type of model
tom_linear_reservoir    = 1  
tom_VHM                 = 2 
tom_UH                  = 3
tom_GR4                 = 6
measures                = 5
tom_2layers_linIF       = 7
tom_2layers_UH          = 8
tom_HBV                 = 9
tom_SAC_SMA             = 10
tom_NAM                 = 11
compare_opti            = -1


tom_infil_no            = 0
tom_infil_cst           = 1
tom_infil_Horton        = 2


tom_netRain_no          = 0
tom_netRain_storage     = 1

tom_transf_no           = 0 # aucun modèle de transfert -> utilise les temps estimés
tom_transf_cst          = 1 # modèle de transfert avec temps constant


## dictionnay of the default indices for each landuse
DEFAULT_LANDUSE = {}
DEFAULT_LANDUSE[1] = _("forêt")
DEFAULT_LANDUSE[2] = _("prairie")
DEFAULT_LANDUSE[3] = _("culture")
DEFAULT_LANDUSE[4] = _("pavés/urbain")
DEFAULT_LANDUSE[5] = _("rivière")
DEFAULT_LANDUSE[6] = _("plan d'eau")


##
DATE_FORMAT_HYDRO = '%Y%m%d-%H%M%S' 


## Version of the code
VERSION_WOLFHYDRO_2023_0 = "2023.0"     # First version to include the versioning
VERSION_WOLFHYDRO_2023_1 = "2023.1"     # First version to include the versioning
VERSION_WOLFHYDRO = "2023.1"