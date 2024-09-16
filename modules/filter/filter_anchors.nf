/* Filter anchors based on effect size 
and number of non-zero samples */

process filter_anchors {
    // tag "filter_anchors from $splash_result_tsv"
    publishDir params.outdir + "/filtered_anchors", mode: 'copy'

    input:
    path(splash_result_tsv)
    val(filter_output_prefix)
    
    output:
    path("${filter_output_prefix}_anchor_list.txt"), emit: anchor_list
    path("${filter_output_prefix}_anchor_clusters.tsv"), emit: anchors_cluster

    script:
    """
    echo "See the truth"
    echo $filter_output_prefix
    Rscript $params.bin/select_important_anchors.R --input $splash_result_tsv --output_prefix $filter_output_prefix \
     --num_anchors $params.num_anchors --num_clusters $params.num_clusters --effect_size $params.effect_size \
     --lookup_table $params.lookup_table --temp_dir $params.temp_dir --splash_bin $params.splash_bin
    
    """
}

workflow {
    println params.splash_result_tsv
    println params.filter_output_prefix
    filter_anchors(params.splash_result_tsv, params.filter_output_prefix)

}

