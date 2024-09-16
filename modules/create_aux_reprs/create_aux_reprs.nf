#!/usr/bin/env nextflow

/* Create sequence representations from filtered anchors ancd anchor clusters */

process create_aux_reprs {
    tag "Create aux representation from $sample_sequence_tsv"
    publishDir params.outdir + "/aux_reprs", mode: 'copy'

    input:
    path(sample_sequence_tsv)
    
    output:
    path("${params.seq_aux_output_prefix}_extenders.fasta"), emit: extenders_fasta
    path("${params.seq_aux_output_prefix}_extenders_cleaned.fasta"), emit: extenders_cleaned_fasta
    path("${params.seq_aux_output_prefix}_sample_extenders.json"), emit: sample_extenders_map
    path("${params.seq_aux_output_prefix}_id2extender.json"), emit: id2ext
    path("${params.seq_aux_output_prefix}_ohe.csv"), emit: ohe_df

    script:
    """
    python $params.bin/create_aux_reprs.py --input $sample_sequence_tsv --out_prefix $params.seq_aux_output_prefix
    """
}

workflow {
    create_aux_reprs(params.sample_sequence_tsv)
}

