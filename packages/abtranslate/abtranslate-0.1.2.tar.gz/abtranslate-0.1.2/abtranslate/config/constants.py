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
                        "inter_threads" : psutil.cpu_count(logical=False), 
                        "intra_threads" : 0, 
                        "max_queued_batches" : 0, 
                        "flash_attention" : False, 
                        "tensor_parallel" : False, 
                        "files" : None}

DEFAULT_CT2_TRANSLATION_CONFIG = {  "target_prefix": None, 
                                    "max_batch_size": 0, 
                                    "batch_type": 'examples', 
                                    "asynchronous": False, 
                                    "beam_size": 2, 
                                    "patience": 1, 
                                    "num_hypotheses": 1, 
                                    "length_penalty": 1, 
                                    "coverage_penalty": 0, 
                                    "repetition_penalty": 1, 
                                    "no_repeat_ngram_size": 0, 
                                    "disable_unk": False, 
                                    "suppress_sequences":  None, 
                                    "end_token": None, 
                                    "return_end_token": False, 
                                    "prefix_bias_beta": 0, 
                                    "max_input_length": 1024, 
                                    "max_decoding_length": 256, 
                                    "min_decoding_length": 1, 
                                    "use_vmap": False, 
                                    "return_scores": False, 
                                    "return_logits_vocab": False, 
                                    "return_attention": False, 
                                    "return_alternatives": False, 
                                    "min_alternative_expansion_prob": 0, 
                                    "sampling_topk": 1, 
                                    "sampling_topp": 1, 
                                    "sampling_temperature": 1, 
                                    "replace_unknowns": False, 
                                    "callback" : None}