
from transformers import AutoModel, AutoTokenizer, BertTokenizer, BertPreTrainedModel
from transformers.modeling_outputs import BaseModelOutputWithPastAndCrossAttentions
from transformers.tokenization_utils import BatchEncoding
import torch
from torch.types import Tensor
import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm
from typing import Union, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)

from .craftext_base_model_encoder import EncodeForm, BaseEncodeModel

class DistilBertEncode(BaseEncodeModel):
    """
        DistilBERT encoder with multiple embedding options.
        Supports tokenization, concatenated embeddings, CLS embeddings, and embeddings excluding stopwords.
        
    """
    
    
    def __init__(self, form_to_use: EncodeForm = EncodeForm.EMBED_CONCAT_ALL, n_splits: int = 1) -> None:
        """
        Unified implementation of DistilBERT encoder with multiple embedding options.


        :param form_to_use: The form of encoding to use, default is EMBED_CONCAT_ALL.
        :type form_to_use: EncodeForm
        
        :param n_splits: Number of splits for the EMBED_CLS_FOR_SPLITS form (default is 1).
        :type n_splits: int
        """
        super().__init__(form_to_use=form_to_use)

        model_name = "distilbert-base-uncased"
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logging.info(f"Using device: {self.device}")
        
        self.tokenizer: BertTokenizer   = AutoTokenizer.from_pretrained(model_name, cache_dir=".")
        self.model: BertPreTrainedModel = AutoModel.from_pretrained(model_name, cache_dir=".").to(self.device)
        self.n_splits = n_splits
        
        
        if form_to_use != EncodeForm.EMBED_CLS_FOR_SPLITS and self.n_splits > 1:
            raise ValueError("n_splits must be 1 for EMBED_CLS_FOR_SPLITS forms.")
        
        self.stopwords = {"a", "an", "the", "in", "on", "at", "by", "to", "for", "of", "with", "and", "or", "but", "so"}  # Пример списка предлогов

    def _safe_model_call(self, 
                         inputs: BatchEncoding,
                         last_hidden_states: bool = True,
                         output_attentions: bool = False,
                         output_hidden_states: bool = False,
                         cross_attentions: bool = False,
                         ) -> Tensor:
        
        """
        Safely calls the model with the given inputs, handling potential None outputs.


        :param inputs: Tokenized inputs to the model.
        :type inputs: BatchEncoding 

        :param last_hidden_states: Whether to return last hidden states.
        :type last_hidden_states: bool

        :param output_attentions: Whether to return attentions.
        :type output_attentions: bool

        :param output_hidden_states: Whether to return hidden states.
        :type output_hidden_states: bool

        :param cross_attentions: Whether to return cross attentions.
        :type cross_attentions: bool

        :return: Model outputs based on the requested options.
        :rtype: torch.Tensor
        """
        
        with torch.no_grad():
            outputs: BaseModelOutputWithPastAndCrossAttentions = self.model(**inputs, return_dict=True)
        
        # Return the requested output based on the flags
        if last_hidden_states:
            assert outputs.last_hidden_state is not None, "Model output.last_hidden_state is None"
            return outputs.last_hidden_state
        
        if output_attentions:
            raise NotImplementedError("Output attentions are not implemented in this model.")
        
        if output_hidden_states:
            raise NotImplementedError("Output hidden states are not implemented in this model.")
        
        if cross_attentions:
            raise NotImplementedError("Cross attentions are not implemented in this model.")
        
        raise ValueError("No valid output requested. Please specify at least one output type.")
    
    def _tokenizer_call(self, instructions: Union[List[str], str]) -> BatchEncoding:
        """
        Safely calls the tokenizer with the given instruction, handling potential None outputs.
        
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :return: Encoded instruction as a NumPy array.
        :rtype: BatchEncoding
        """
        
        inputs = self.tokenizer(instructions, return_tensors='pt', truncation=True, padding=True).to(self.device)
        
        if inputs is None or 'input_ids' not in inputs:
            raise ValueError("Tokenizer output is None or does not contain 'input_ids'")
        
        return inputs
    
    def encode(self, instructions: List[str]) -> NDArray:
        """
        Encodes the instruction based on the selected form_to_use.
        
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :return: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """
        
        n_splits = self.n_splits 
        if self.form_to_use == EncodeForm.TOKEN:
            return self.get_tokens(instructions)
        elif self.form_to_use == EncodeForm.EMBED_CONCAT_ALL:
            return self.get_concatenated_embeddings(instructions)
        elif self.form_to_use == EncodeForm.EMBED_CONCAT_NO_STOPWORDS:
            return self.get_concatenated_embeddings_no_stopwords(instructions)
        elif self.form_to_use == EncodeForm.EMBED_CLS_FOR_SPLITS:
            return self.get_cls_embeddings_for_splits(instructions, n_splits)
        else:
            return self.get_cls_embeddings(instructions)
        

    def get_concatenated_embeddings(self, instructions: List[str]) -> NDArray:
        """
        Generates a single embedding by concatenating embeddings of all tokens.
        
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :return: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """
        
        inputs = self._tokenizer_call(instructions)
                
        token_embeddings = self._safe_model_call(inputs, last_hidden_states=True)
        
        return token_embeddings.view(-1).cpu().numpy()

    def get_concatenated_embeddings_no_stopwords(self, instructions: List[str]) -> NDArray:
        """
        Generates a single embedding by concatenating embeddings of all tokens excluding stopwords.
        
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :return: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """
        
        tokens = []
        for instruction in instructions: # tokenize each instruction
            if instruction is None:
                instruction = 'None'
                
            instruction_tokens = self.tokenizer.tokenize(instruction)
            tokens.append("".join(filter(lambda x: x not in self.stopwords, instruction_tokens))) # Exclude stopwords

        inputs = self._tokenizer_call(tokens)

        token_embeddings = self._safe_model_call(inputs, last_hidden_states=True)
        
        return token_embeddings.view(-1).numpy()
    
    def get_cls_embeddings(self, instructions: List[str]) -> NDArray:
        """
        Generates CLS embeddings for the given instruction.
        
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :return: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """
        
        inputs = self._tokenizer_call(instructions)

        last_hidden_state = self._safe_model_call(inputs, last_hidden_states=True)
        
        cls_embeddings = last_hidden_state[:, 0, :]  
        concatenated_embedding = cls_embeddings.cpu().numpy() 
        
        return concatenated_embedding

    def get_cls_embeddings_for_splits(self, instructions: List[str], n_splits: int) -> NDArray:
        """
        Generates CLS embeddings for the given instruction, splitting it into n_splits parts.
                
        
        :param instruction: List of strings representing the instruction.
        :type instruction: List[str]
        
        :return: Encoded instruction as a NumPy array.
        :rtype: NDArray
        """ 
        
        batch_embeddings = []

        for instruction in tqdm(instructions, desc="Make embeddings from splitted instrctuctions"):
            if instruction is None:
                instruction = 'None'
            words = instruction.split("\n")
            split_size = max(1, len(words) // n_splits)
            splits = [' '.join(words[i:i + split_size]) for i in range(0, len(words), split_size)]

            while len(splits) < n_splits:
                splits.append("")
            splits = splits[:n_splits]
            
            inputs = self._tokenizer_call(splits)
            
            last_hidden_state = self._safe_model_call(inputs, last_hidden_states=True)

            cls_embeddings = last_hidden_state[:, 0, :]  # CLS
            concatenated_embedding = cls_embeddings.reshape(-1)
            batch_embeddings.append(concatenated_embedding.cpu().numpy())

        return np.array(batch_embeddings)

    def get_embeddings(self, instructions: List[str]) -> NDArray:
        return self.encode(instructions)

    def get_tokens(self, instruction: List[str]) -> NDArray:
        return self.tokenizer(instruction, max_length=30, truncation=True, padding="max_length", return_tensors='np')['input_ids']


def make_encoder(n_splits: int, form_to_use: EncodeForm = EncodeForm.EMBED_CONCAT_ALL):
    """
    Factory function to create a custom DistilBertEncode model with specified form and number of splits.
        
        
    :param n_splits: Number of splits for the model.
    :type: n_splits: int
    
    :param form_to_use: The form of encoding to use (default is EMBED_CONCAT_ALL).
    :type form_to_use: EncodeForm
    
    :return: A custom DistilBertEncode model class. 
    :rtype: DistilBertEncode 
    """
    
    class CustomBertEncodeModel(DistilBertEncode):
        def __init__(self, form_to_use=form_to_use):
            super().__init__(form_to_use=form_to_use, n_splits=n_splits)
    
    return CustomBertEncodeModel
