import torch
import torch.nn as nn
from evo import Evo
from Bio import SeqIO
import numpy as np
import argparse
import os
import time

class CustomEmbedding(nn.Module):
  def unembed(self, u):
    return u

def parse_args():
    parser = argparse.ArgumentParser(description='Embed sequences using Evo')
    parser.add_argument('--input', type=str, required=True, help='Path to input fasta file')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    return parser.parse_args()

def tokenize(sequences, tokenizer):
  input_ids = []
  for sequence in sequences:
    input_id = torch.tensor(
      tokenizer.tokenize(sequence),
      dtype=torch.int,
  )
    input_ids.append(input_id)

  return torch.stack(input_ids).to(device)

def embed_tokens(tokens, model):
  with torch.no_grad():
      logits, _ = model(tokens) # (batch, length, vocab)
  logits = logits.detach().cpu().float().squeeze().mean(dim=1).numpy()
  return logits

def embed_sequences(sequences, model, tokenizer):
    tokens = tokenize(sequences, tokenizer)
    return embed_tokens(tokens, model)

def main(model, tokenizer):
    args = parse_args()
    sequences = [str(record.seq) for record in SeqIO.parse(args.input, 'fasta')]
    sequences_batch = [sequences[i:i + batch_size] for i in range(0, len(sequences), batch_size)]
    embeddings = []
    tic = time.time()
    for i, sequences in enumerate(sequences_batch):
        print(f'Embedding batch {i + 1}/{len(sequences_batch)}')
        embeddings.append(embed_sequences(sequences, model, tokenizer))
    embeddings = np.concatenate(embeddings)
    np.save(args.output, embeddings)
    toc = time.time()
    print(f'Embedding complete in {toc - tic:.2f} seconds')

if __name__ == '__main__':
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    batch_size = 128
    evo_model = Evo('evo-1-8k-base')
    model, tokenizer = evo_model.model, evo_model.tokenizer
    model.unembed = CustomEmbedding()
    model.to(device)
    model.eval()
    main(model, tokenizer)
