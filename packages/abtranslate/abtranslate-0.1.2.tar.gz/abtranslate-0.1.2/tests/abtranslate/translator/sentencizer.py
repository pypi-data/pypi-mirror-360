import stanza

class Sentencizer:
    def split_sentences(text:str) -> list[str]:
        raise NotImplementedError()    
        
class StanzaSentencizer:
    def __init__(self, model_dir, lang_code):
        self.model_dir = str(model_dir)
        self.lang_code = lang_code
        self.processor = None

    def lazy_load(self):
        
        if not self.processor:
            self.processor = stanza.Pipeline(
                lang=self.lang_code,
                dir=self.model_dir,
                processors="tokenize",
                use_gpu=False,
                logging_level="WARNING",
            )
        return self.processor
        
    
    def split_sentences(self, text:str) -> list[str]:
        processor = self.lazy_load()
        sbd = processor(text)
        return [sentence.text for sentence in sbd.sentences]