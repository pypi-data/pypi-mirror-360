from typing import TYPE_CHECKING
from pathlib import Path 
import copy
import json

from zipfile import ZipFile

from abtranslate.config import PACKAGE_DIR
from abtranslate.config import DEFAULT_CT2_CONFIG
from abtranslate.utils.file_manager import extract_package
from  .sentencizer import StanzaSentencizer
from .tokenizer import SentencePieceTokenizer, BPETokenizer
from .argos_translator import ArgosTranslator

class Package:
    def get_source_language_code(self):
        raise NotImplementedError()
    def get_target_language_code(self):
        raise NotImplementedError()
    def load_translator(self)  :
        raise NotImplementedError()

class ArgosPackage(Package):
    """A package, can be either installed locally or available from a remote package index.

    Attributes:
        package_path: The path to the installed package. None if not installed.

        package_version: The version of the package.

        argos_version: The version of Argos Translate the package is intended for.

        from_code: The code of the language the package translates from.

        from_name: Human readable name of the language the package translates from.

        to_code: The code of the language the package translates to.

        to_name: Human readable name of the language the package translates to.

        links: A list of links to download the package


    Packages are a zip archive of a directory with metadata.json
    in its root the .argosmodel file extension. By default a
    OpenNMT CTranslate2 directory named model/ is expected in the root directory
    along with a sentencepiece model named sentencepiece.model or a bpe.model
    for tokenizing and Stanza data for sentence boundary detection.
    Packages may also optionally have a README.md in the root.

    from_code and to_code should be ISO 639 codes if applicable.

    Example metadata.json
    {
        "package_version": "1.0",
        "argos_version": "1.0",
        "from_code": "en",
        "from_name": "English",
        "to_code": "es",
        "to_name": "Spanish",
        "links": ["https://example.com/en_es.argosmodel"]
    }
    """
    code: str
    package_path: Path
    package_version: str
    argos_version: str
    from_code: str
    from_name: str
    from_codes: list
    to_code: str
    to_codes: list
    to_name: str
    links: list
    type: str
    languages: list
    dependencies: list
    source_languages: list
    target_languages: list
    links: list[str]

    def __init__(self, package_path):
        """Create a new Package from path.

        Args:
            package_path: Path to installed package directory.

        """
        if type(package_path) == str:
            # Convert strings to pathlib.Path objects
            package_path = Path(package_path)
        self.package_path = package_path
        metadata_path = package_path / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(
                "Error opening package at " + str(metadata_path) + " no metadata.json"
            )
        with open(metadata_path) as metadata_file:
            metadata = json.load(metadata_file)
            self.load_metadata_from_json(metadata)

        sp_model_path = package_path / "sentencepiece.model"
        bpe_model_path = package_path / "bpe.model"
        # Tokenizer
        if sp_model_path.exists():
            self.tokenizer = SentencePieceTokenizer(sp_model_path)
        elif bpe_model_path.exists():
            self.tokenizer = BPETokenizer(bpe_model_path, self.from_code, self.to_code)
        
        stanza_model_path = package_path / "stanza"
        # Sentencizer
        if stanza_model_path.exists():
            self.sentencizer = StanzaSentencizer(stanza_model_path, self.from_code) 
            
    def load_metadata_from_json(self, metadata):
        """Loads package metadata from a JSON object.

        Args:
            metadata: A json object from json.load

        """
        self.code = metadata.get("code")
        self.package_version = metadata.get("package_version", "")
        self.argos_version = metadata.get("argos_version", "")
        self.from_code = metadata.get("from_code")
        self.from_name = metadata.get("from_name", "")
        self.from_codes = metadata.get("from_codes", list())
        self.to_code = metadata.get("to_code")
        self.to_codes = metadata.get("to_codes", list())
        self.to_name = metadata.get("to_name", "")
        self.links = metadata.get("links", list())
        self.type = metadata.get("type", "translate")
        self.languages = metadata.get("languages", list())
        self.dependencies = metadata.get("dependencies", list())
        self.source_languages = metadata.get("source_languages", list())
        self.target_languages = metadata.get("target_languages", list())
        self.target_prefix = metadata.get("target_prefix", "")

        # Add all package source and target languages to
        # source_languages and target_languages
        if self.from_code is not None or self.from_name is not None:
            from_lang = dict()
            if self.from_code is not None:
                from_lang["code"] = self.from_code
            if self.from_name is not None:
                from_lang["name"] = self.from_name
            self.source_languages.append(from_lang)
        if self.to_code is not None or self.to_name is not None:
            to_lang = dict()
            if self.to_code is not None:
                to_lang["code"] = self.to_code
            if self.to_name is not None:
                to_lang["name"] = self.to_name
            self.source_languages.append(to_lang)
        self.source_languages += copy.deepcopy(self.languages)
        self.target_languages += copy.deepcopy(self.languages)

    def get_model_path(self) -> str:
        return str(self.package_path/"model")
    
    def get_source_language_code(self):
        return self.from_code
    
    def get_target_language_code(self):
        return self.to_code
    
    def load_translator(self, translator_config=DEFAULT_CT2_CONFIG, optimized_config=False) -> ArgosTranslator:
        return ArgosTranslator(self, device="cpu" ,translator_config=translator_config, optimized_config=optimized_config)
    

def load_argostranslate_model(model_file:str) -> ArgosPackage:
    """Get model package from file"""
    if type(model_file) == str :
        model_file = Path(model_file)
    model_path = model_file.resolve()
    package_path = extract_package(model_file=model_path, extract_dir=PACKAGE_DIR)
    model_path = Path(model_file)
    if model_path.suffix == ".argosmodel" or model_path.suffix == ".zip":
        return ArgosPackage(package_path)
    else:
        raise Exception(f"Load model error: unsupported model file: {model_path}")

def download_model(source_language_code, target_language_code):
    """Get model package downloaded from repository"""
    pass

