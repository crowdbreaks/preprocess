import numpy as np
import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from torchvision import transforms
import tensorflow as tf
import tensorflow_transform as tft
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('/drives/sdg/sample_tweets/preprocess/')

from utils.helpers import get_sampled_data

class TorchStandardScaler():
    """Standardize data by removing the mean and scaling to unit variance.  This object can be used as a transform in PyTorch data loaders.
    Args:
    mean (FloatTensor): The mean value for each feature in the data.
    scale (FloatTensor): Per-feature relative scaling."""

    def adapt(self, data_sample):
        self.means_ = data_sample.mean(axis=0, keepdim=False)
        self.stds_ = data_sample.std(axis=0, unbiased=True, keepdim=False)
    def call(self, inputs):
        return (inputs - self.means_)/self.stds_

def emb_pca():

    # The input text contains anonymized data and no URL from tweets matching with the keywords relevant for the project
    df = get_sampled_data()
    # Create an array that contains all the strings corresponding to the text of the tweets
    input_txt = df.tweet_text.tolist()
    # Use the tokenizer generated by CT-BERT
    tokenizer = BertTokenizer.from_pretrained('digitalepidemiologylab/covid-twitter-bert-v2')
    batch = tokenizer.__call__(input_txt[:100], return_tensors='pt', padding=True)
    # Use the CT-BERT model
    model = BertModel.from_pretrained('digitalepidemiologylab/covid-twitter-bert-v2')
    outputs = model(**batch)
    last_hidden_states = outputs[0]
    # Standardize the output
    scaler = TorchStandardScaler()
    scaler.adapt(last_hidden_states)
    norm_emb = scaler.call(last_hidden_states)
    # Keep the matrix that corresponds to the CLS token
    norm_emb = norm_emb[:,0,:]
    # Get the Numpy array from the tensor
    emb_arr = norm_emb.detach().numpy()
    # Get the DataFrame from the Numpy array
    emb_df = pd.DataFrame(emb_arr)
    # Export the DataFrame to a CSV File
    # emb_df.to_csv('sample_for_pca.csv', sep='\t', index=False, header=False)
    # Create a PCA transformer
    U, S, V = torch.pca_lowrank(norm_emb, center=True, niter=2)
    # Project data onto the first two principal components
    X_2d = torch.matmul(norm_emb, V[:,:2]).detach().numpy()
    fig = plt.figure()
    plt.scatter(X_2d[:,0], X_2d[:,1])
    # Labels and legend
    plt.xlabel('1st component')
    plt.ylabel('2nd component')
    fig.savefig('PCA_2d.png')
    return
if __name__== '__main__':
    emb_pca()

