import json
import os
from os.path import join, basename
import argparse
import pandas as pd

import json
import os
from os.path import join, basename
import numpy as np

class SPLASHSeq:
    def __init__(self, seq:str, name:str, anchor_len:str = 27, target_len:str = 27):
        self.seq = seq
        self.name = name
        self.anchor_len = anchor_len
        self.target_len = target_len       
        self.extender_len = self.anchor_len + self.target_len
        self.extenders = [self.seq[i:i+self.extender_len] for i in range(0, len(self.seq), self.extender_len)]
        self.anchors = [self.seq[i:i+self.anchor_len] for i in range(0, len(self.seq), self.extender_len)]
        self.targets = [self.seq[i+self.anchor_len:i+self.anchor_len+self.target_len] for i in range(0, len(self.seq), self.extender_len)]
        assert len(set(self.anchors)) == len(self.anchors), "Anchors must be unique"
        self.achor2indx = {anchor: i for i, anchor in enumerate(self.anchors)}
        self.target2indx = {target: i for i, target in enumerate(self.targets)}
        self.extender2indx = {extender: i for i, extender in enumerate(self.extenders)}
        self.index2anchor = {i: anchor for i, anchor in enumerate(self.anchors)}
        self.index2target = {i: target for i, target in enumerate(self.targets)}
        self.index2extender = {i: extender for i, extender in enumerate(self.extenders)}
        

    def get_target_from_anchor(self, anchor:str):
        return self.targets[self.achor2indx[anchor]]

    def get_extender_from_anchor(self, anchor:str):
        return self.extenders[self.achor2indx[anchor]]

    
    def __repr__(self):
        return f"SPLASHSeq(name={self.name}, seq={self.seq})"


class SPLASHSeqSet:
    def __init__(self, df):
        self.df = df
        self.seqs = df["seq"]
        self.names = df["sample"]
        self.splash_seqs = [SPLASHSeq(seq, name) for seq, name in zip(self.seqs, self.names)]
        self.ext2id = {ext: i for i, ext in enumerate(self.get_unique_extenders())}
        self.id2ext = {i: ext for i, ext in enumerate(self.get_unique_extenders())}

    def get_unique_extenders(self):
        extenders = set()
        for splash_seq in self.splash_seqs:
            extenders.update(splash_seq.extenders)
        return extenders
    
    def get_sample_ext_ids(self):
        sample_ext_map = {}
        for ss in self.splash_seqs:
            ext_ids = [self.ext2id[ext] for ext in ss.extenders]
            sample_ext_map[ss.name] = ext_ids
        return sample_ext_map
    
    def construct_ohe_df(self, k=54):
        df = self.df
        def get_kmers(sequence, k):
            return [sequence[i:i+k] for i in range(0, len(sequence) - k + 1, k)]
        df['kmers'] = df['seq'].apply(lambda seq: get_kmers(seq, k))
        kmers_df = pd.DataFrame(df['kmers'].tolist(), index=df['sample'])
        onehot_encoded_list = [pd.get_dummies(kmers_df[col]) for col in kmers_df.columns]
        onehot_encoded_df = pd.concat(onehot_encoded_list, axis=1)
        onehot_encoded_df.columns = [self.ext2id[i] for i in onehot_encoded_df.columns]
        sorted_columns = sorted(onehot_encoded_df.columns, key=lambda col: int(col))
        df_sorted = onehot_encoded_df[sorted_columns]
        return df_sorted*1
    
    def write_ohe_df(self, output_path):
        df = self.construct_ohe_df()
        df.to_csv(output_path)
        
    def write_id2ext_json(self, output_path):
        with open(output_path, "w") as f:
            json.dump(self.id2ext, f, indent=4)
    
    def write_seq_fasta(self, output_path):
        with open(output_path, "w") as f:
            for splash_seq in self.splash_seqs:
                f.write(f">{splash_seq.name}\n")
                f.write(f"{splash_seq.seq}\n")
    
    def write_extender_fasta(self, output_path):
        with open(output_path, "w") as f:
            for key, extender in self.id2ext.items():
                f.write(f">{key}\n")
                f.write(f"{extender}\n")
    
    def write_extender_fasta_cleaned(self, output_path):
        with open(output_path, "w") as f:
            for key, extender in self.id2ext.items():
                extender = extender.replace("N", "")
                f.write(f">{key}\n")
                f.write(f"{extender}\n")
                
    def write_sample_extenders_json(self, output_path):
        sample_ext_map = self.get_sample_ext_ids()
        with open(output_path, "w") as f:
            json.dump(sample_ext_map, f, indent = 4)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--out_prefix", type=str, required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    df = pd.read_csv(args.input, sep = "\t")
    splash_seqs = SPLASHSeqSet(df)
    splash_seqs.write_ohe_df(f"{args.out_prefix}_ohe.csv")
    splash_seqs.write_id2ext_json(f"{args.out_prefix}_id2extender.json")
    splash_seqs.write_extender_fasta(f"{args.out_prefix}_extenders.fasta")
    splash_seqs.write_extender_fasta_cleaned(f"{args.out_prefix}_extenders_cleaned.fasta")
    splash_seqs.write_sample_extenders_json(f"{args.out_prefix}_sample_extenders.json")

if __name__ == "__main__":
    main()
    