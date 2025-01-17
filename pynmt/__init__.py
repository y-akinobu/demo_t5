try:
    import sentencepiece
except ModuleNotFoundError:
    import os
    os.system('pip install sentencepiece')

try:
    import transformers
except ModuleNotFoundError:
    import os
    os.system('pip install transformers')

import torch
# from torch.utils.data import Dataset, DataLoader
from transformers import MT5ForConditionalGeneration, MT5Tokenizer

from google_drive_downloader import GoogleDriveDownloader

USE_GPU = torch.cuda.is_available()
DEVICE = torch.device('cuda:0' if USE_GPU else 'cpu')
print('DEVICE :', DEVICE)


MODEL_DIR = "./content/model/"

class NMT(object):
    model: object
    def __init__(self, dir):
        self.trained_model = MT5ForConditionalGeneration.from_pretrained(dir).to(DEVICE)
        self.tokenizer = MT5Tokenizer.from_pretrained(dir, is_fast=True)
        # additional_special_tokens = ['<A>', '<B>', '<C>', '<D>', '<E>', '<a>', '<b>', '<c>', '<d>', '<e>']
        # self.tokenizer.add_tokens(additional_special_tokens)
        
    def translate_beam(self, src_sentence: str):
        self.trained_model.config.update({"num_beams": 5})
        input_ids = self.tokenizer(src_sentence, return_tensors='pt').input_ids.to(DEVICE)
        predict = self.trained_model.generate(input_ids,
                         return_dict_in_generate=True,
                         output_scores=True,
                         length_penalty = 5,
                         num_return_sequences = 5,
                         early_stopping = True)
        pred_list = sorted([[self.tokenizer.decode(predict.sequences[i], skip_special_tokens=True), predict.sequences_scores[i].item()] for i in range(len(predict))], key=lambda x:x[1], reverse=True)
        sentences_list = [ i[0] for i in pred_list ]
        scores_list = [ i[1] for i in pred_list ]                   
        return sentences_list, scores_list

def make_pynmt(model_id='1qZmBK0wHO3OZblH8nabuWrrPXU6JInDc', model_file='./model.zip'):
    GoogleDriveDownloader.download_file_from_google_drive(
        file_id=model_id, dest_path=model_file, unzip=True)
    nmt = NMT(MODEL_DIR)

    def pynmt(sentence):
        pred, prob = nmt.translate_beam(sentence)
        return pred, prob

    return pynmt

