#!/usr/bin/env nextflow

/* DeepSPLASH workflow */

include { filter_anchors } from '../modules/filter/filter_anchors.nf'
include { create_seq_reprs } from '../modules/create_seq_reprs/create_seq_reprs.nf'

workflow {

    ch_filter = filter_anchors(params.splash_result_tsv, params.filter_output_prefix)
    println params.seq_repr_output_prefix
    ch_satc = create_seq_reprs(ch_filter.anchor_list, ch_filter.anchors_cluster, params.seq_repr_output_prefix)
    ch_aux = create_aux_reprs(ch_satc.sample_sequence_tsv)
    ch_embed_evo = embed_evo(ch_aux.extenders_fasta, "/embed_evo_out.npy")
}