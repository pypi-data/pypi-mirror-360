from pathlib import Path, PosixPath
import psutil

# Paths
MAIN_DIR = PosixPath("~/.local/share/abtranslate").expanduser()
PACKAGE_DIR = MAIN_DIR/"packages"

# Url's 
PACKAGES_INDEX = None

# Values
BATCH_SIZE = 32
DEFAULT_CT2_CONFIG = {  
                        "compute_type" : 'default', 
                        "inter_threads" : 1, 
                        "intra_threads" : 0,
                    }

DEFAULT_CT2_TRANSLATION_CONFIG = {   
                                    "beam_size": 2, 
                                    "patience": 1, 
                                    "num_hypotheses": 1, 
                                    "replace_unknowns": True, 
                                }