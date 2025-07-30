from typing import List
import string

from abtranslate.translator.sentencizer import Sentencizer

def generate_batch(self, sentences:list[str], batch_size):
        """
        Splits a list of sentence into batches of the given size.

        Args:
            sentences (list): The list to split.
            batch_size (int): The size of each batch.

        Yields:
            list: Batches of the original list.
        """
        if not isinstance(sentences, list):
            raise TypeError(f"Invalid type of parameter 'sentence', expected {list}, got: {type(sentences)}")
        for i in range(0, len(sentences), batch_size):
            yield sentences[i:i + batch_size]


def expand_to_sentence_level(list_text: List[str], sentencizer:Sentencizer, ignore_empty_paragraph=True, ignore_empty_row=False)  -> List[List[List[str]]]:
    """
    Split every paragraph/sentences in text entry to sublist.  
    Rows -> Paraghraps -> Sentences
    example =  [  # List of rows (e.g., daily entries or inspections)
                    [  # Row 1
                        [  # Paragraph 1 in Row 1 (e.g., defect report section)
                            "Left engine oil leak detected during pre-flight inspection",
                            "Maintenance notified and leak area cleaned for further inspection"
                        ],
                        [  # Paragraph 2 in Row 1 (e.g., corrective action)
                            "Technician replaced oil seal on left engine",
                            "Test run performed with no further leakage observed"
                        ]
                    ],
                    [  # Row 2
                        [  # Paragraph 1 in Row 2
                            "Right main landing gear retraction slower than normal on landing",
                            "Pilot noted gear indicator light delayed by 5 seconds"
                        ],
                        [  # Paragraph 2 in Row 2
                            "Hydraulic fluid level checked and topped up",
                            "Landing gear actuator lubricated and tested"
                        ]
                    ]
                ]
    """
    expanded_rows = []
    for text in list_text:
        paragraphs = []
        if text.strip() == "" and ignore_empty_row:
            continue
        for paragraph in split_paragraphs(text):
            if paragraph.strip() == "" and ignore_empty_paragraph:
                continue
            sentences =  sentencizer.split_sentences(paragraph)
            paragraphs.append(sentences)
        expanded_rows.append(paragraphs)
    return expanded_rows


def restore_expanded_to_rows_level(expanded_rows):
    rows = []
    for expanded_paragraps in expanded_rows:
        paragraphs = []
        for sentences in expanded_paragraps:
            paragraphs.append(" ".join(sentences)) 
        rows.append(join_paragraphs(paragraphs)) 
    return rows


def flatten_list(list_data: List[List[List[str]]], inner_type) -> List[str]:
    flattened = []

    def recurse(list_data):
        if len(list_data) == 0:
            return inner_type()
        
        if type(list_data[0]) == list:
            for inner_list in list_data:        
                recurse(inner_list)
        else:
            for data in list_data:        
                flattened.append(data)
    recurse(list_data)
    return flattened


def get_structure(lst, ignore_empty=False):
        struct =[]
        for e in lst:
            if len(e) ==  0 :
                if ignore_empty: continue
                struct.append(0) # inner list is empty list
            elif isinstance(e[0], str): # check if the list is list of items
                struct.append(len(e)) # count length of items
            else: # the lis is not inner list yet
                struct.append(get_structure(e, ignore_empty= ignore_empty))
        return struct


def apply_structure(flattened_list, structure):
    idx = [0]  # Use list to make it mutable inside recursive calls
    def recurse(substructure):
        if isinstance(substructure, int):  # Base case: leaf node (sentence count)
            if substructure == 0:
                return []
            start = idx[0]
            end = start + substructure
            if end > len(flattened_list):
                raise ValueError(f"Not enough sentences. Expected at least {end}, got {len(flattened_list)}.")
            idx[0] = end
            return flattened_list[start:end]
        elif isinstance(substructure, list):  # Recursive case
            return [recurse(s) for s in substructure]
        else:
            raise TypeError("Structure must be an int or list of ints")
    
    if sum(flatten_list(structure, int)) != len(flattened_list):
        raise ValueError(f"Structure {structure} doesn't compatible with list length {len(flattened_list)}. Length of list {len(flattened_list)} out of {sum(flatten_list(structure, int))} structure items required.")
    return recurse(structure)


def split_paragraphs(text:str ) -> list[str]:
    return text.split("\n")


def join_paragraphs(paragraphs:List[str] ) -> str:
    return "\n".join(paragraphs)


def is_valid_text(text:str) -> bool:
    if text == None:
        return False
    clean_str = text.replace(" ","")
    if clean_str == "":
        return False
    elif all(char in string.punctuation for char in clean_str):
        return False
    else:
        return True 