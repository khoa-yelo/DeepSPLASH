/* Embed sequence with Evo */

process embed_evo {
    // tag "filter_anchors from $splash_result_tsv"
    publishDir params.outdir + "/embed_evo", mode: 'copy'

    input:
    path(extenders_fasta)
    path(embed_evo_out)

    output:
    path($embed_evo_out), emit: embed_evo

    shell:
    """
    export HF_DATASETS_CACHE="/oak/stanford/groups/horence/khoa/shares/hf_cache"
    export TOKENIZERS_CACHE="/oak/stanford/groups/horence/khoa/shares/hf_cache"
    export TRANSFORMERS_CACHE="/oak/stanford/groups/horence/khoa/shares/hf_cache"
    export HF_HOME="/oak/stanford/groups/horence/khoa/shares/hf_cache"
    export HF_MODULE_CACHE="/oak/stanford/groups/horence/khoa/shares/hf_cache"
    
    # activate conda evo-design env
    source /opt/conda/etc/profile.d/conda.sh
    conda activate evo-design

    python $params.bin/embed_evo.py --input $extenders_fasta --output $embed_evo_out
    """
}

workflow {
    embed_evo(params.extenders_fasta, "/embed_evo_out.npy")
}

