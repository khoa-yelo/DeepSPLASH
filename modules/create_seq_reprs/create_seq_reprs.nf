#!/usr/bin/env nextflow

/* Create sequence representations from filtered anchors ancd anchor clusters */

process create_seq_reprs {
    tag "Create seq representation $anchor_list"
    publishDir params.outdir + "/seq_reprs", mode: 'copy'
    cpus params.seq_reprs_num_cores

    input:
    path(anchor_list)
    path(anchors_cluster)
    val(seq_repr_output_prefix)
    
    output:
    path("${seq_repr_output_prefix}_sample_sequences.tsv"), emit: sample_sequence_tsv
    path("${seq_repr_output_prefix}_sample_sequences.fasta"), emit: sample_sequence_fasta

    script:
    """
    Rscript $params.bin/process_splash_data_for_embedding.R --anchor_file $anchor_list --cluster_file $anchors_cluster \
    --output_prefix $seq_repr_output_prefix --id_mapping $params.id_mapping --satc_files $params.satc_files \
    --temp_dir $params.temp_dir --satc_util_bin $params.satc_util_bin --num_cores $params.seq_reprs_num_cores
    """
}

workflow {
    create_seq_reprs(params.anchor_list, params.anchors_cluster, params.seq_repr_output_prefix)
}

