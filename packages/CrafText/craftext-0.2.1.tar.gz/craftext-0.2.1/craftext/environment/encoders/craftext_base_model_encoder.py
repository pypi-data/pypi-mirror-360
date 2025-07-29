import os
from enum import Enum
from abc import ABC, abstractmethod
from numpy.typing import NDArray
from typing import List


os.environ['HF_HOME'] = "."


class EncodeForm(Enum):
    """
    Enum representing different forms of encoding.
    """
    TOKEN = "token" # Tokenized form of the instruction
    EMBED_CONCAT_ALL = "embed_concat_all"  # Concatenated embeddings of all tokens
    EMBED_CONCAT_NO_STOPWORDS = "embed_concat_no_stopwords"  # CLS embeddings of all tokens excluding stopwords
    EMBED_CLS_FOR_SPLITS = "embed_cls_for_splits"  # CLS embeddings for each split
    EMBEDDING = "default" # Default embedding form, typically CLS embeddings

class BaseEncodeModel(ABC):
    """
    Abstract base class for encoding models.
    This class defines the interface for encoding instructions into embeddings or tokens.
    
    """
    def __init__(self, form_to_use: EncodeForm = EncodeForm.EMBEDDING) -> None:
        """
        Abstract base class for encoding models.
        Must be implemented in a concrete class.
        
        
        :param form_to_use: The form of encoding to use, default is EMBEDDING.
        :type form_to_use: EncodeForm
        """
        self.form_to_use = form_to_use

    @abstractmethod
    def encode(self, instruction: List[str]) -> NDArray:
        """
        Abstract method to encode an instruction.
        Must be implemented in a concrete class.
        
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :returns: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """
        pass

    @abstractmethod
    def get_embeddings(self, instruction: List[str]) -> NDArray:
        """
        Abstract method to get embeddings.
        Must be implemented in a concrete class.
        
        
        :param instruction:  List of strings representing the instruction.
        :type instruction: List[str]
        
        :returns: Encoded instruction as a NumPy array.
        :rtype: NDArray
        
        """
        pass

    @abstractmethod
    def get_tokens(self, instruction: List[str]) -> NDArray:
        """
        Abstract method to get tokens.
        Must be implemented in a concrete class.
        
        
        :param instruction:  List of strings representing the instruction.
        :type instruction: List[str]
        
        :returns: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """
        pass


