from typing import TypedDict, Union, Dict, List, Optional, Callable
from ctranslate2 import  GenerationStepResult
class CT2TranslatorConfig(TypedDict):
    # default configuration based on ctranslate2.Translator, see the documentation for more details https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html#ctranslate2.Translator 
    
    device: str 
    device_index: Union[int, List[int]]
    compute_type: Union[str, Dict[str, str]] 
    inter_threads: int 
    intra_threads: int     
    max_queued_batches: int 
    flash_attention: bool 
    tensor_parallel: bool 
    files: object

class CT2TranslationConfig(TypedDict):
    target_prefix: Optional[List[Optional[List[str]]]] 
    max_batch_size: int 
    batch_type: str 
    asynchronous: bool 
    beam_size: int 
    patience: float 
    num_hypotheses: int 
    length_penalty: float 
    coverage_penalty: float 
    repetition_penalty: float 
    no_repeat_ngram_size: int 
    disable_unk: bool 
    suppress_sequences: Optional[List[List[str]]] 
    end_token: Optional[Union[str, List[str], List[int]]] 
    return_end_token: bool 
    prefix_bias_beta: float 
    max_input_length: int 
    max_decoding_length: int 
    min_decoding_length: int 
    use_vmap: bool 
    return_scores: bool 
    return_logits_vocab: bool 
    return_attention: bool 
    return_alternatives: bool 
    min_alternative_expansion_prob: float 
    sampling_topk: int 
    sampling_topp: float 
    sampling_temperature: float 
    replace_unknowns: bool
    callback: Callable[[GenerationStepResult], bool]