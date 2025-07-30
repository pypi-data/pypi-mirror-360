from typing import List

from .package import ArgosPackage

class ITranslator():
    def translate(text: str) -> str:
        raise NotImplementedError()

    def translate_batch(batch: List[str]) -> List[str]:
        raise NotImplementedError()
    