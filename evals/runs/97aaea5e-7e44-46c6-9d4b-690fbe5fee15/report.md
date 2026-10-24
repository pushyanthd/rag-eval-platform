# Retrieval evaluation `97aaea5e-7e44-46c6-9d4b-690fbe5fee15`

- Dataset: `fiqa` (`test`)
- Variants: `bm25`, `dense_bge_small`, `hybrid_rrf`, `hybrid_rrf_rerank`
- Seed: `42`
- Results: `200`
- Indexes: `bm25`=`7c89aa4f509ca2fd7a8b589f9ceda2afe87a20cdabecad187cf6d5fa899cf2fe`, `dense_bge_small`=`7c89aa4f509ca2fd7a8b589f9ceda2afe87a20cdabecad187cf6d5fa899cf2fe`, `hybrid_rrf`=`7c89aa4f509ca2fd7a8b589f9ceda2afe87a20cdabecad187cf6d5fa899cf2fe`, `hybrid_rrf_rerank`=`7c89aa4f509ca2fd7a8b589f9ceda2afe87a20cdabecad187cf6d5fa899cf2fe`

## Quality metrics

| Variant | Metric | Mean | 95% CI | Queries |
|---|---|---:|---:|---:|
| bm25 | nDCG@10 | 0.3333 | [0.2445, 0.4261] | 50 |
| bm25 | Recall@10 | 0.4105 | [0.3024, 0.5257] | 50 |
| bm25 | Recall@100 | 0.5740 | [0.4679, 0.6715] | 50 |
| bm25 | MRR@10 | 0.4192 | [0.2985, 0.5411] | 50 |
| dense_bge_small | nDCG@10 | 0.4598 | [0.3576, 0.5594] | 50 |
| dense_bge_small | Recall@10 | 0.5410 | [0.4357, 0.6495] | 50 |
| dense_bge_small | Recall@100 | 0.7293 | [0.6445, 0.8124] | 50 |
| dense_bge_small | MRR@10 | 0.5282 | [0.4173, 0.6417] | 50 |
| hybrid_rrf | nDCG@10 | 0.4236 | [0.3359, 0.5104] | 50 |
| hybrid_rrf | Recall@10 | 0.5481 | [0.4417, 0.6467] | 50 |
| hybrid_rrf | Recall@100 | 0.7276 | [0.6369, 0.8076] | 50 |
| hybrid_rrf | MRR@10 | 0.4927 | [0.3824, 0.6008] | 50 |
| hybrid_rrf_rerank | nDCG@10 | 0.4818 | [0.3935, 0.5676] | 50 |
| hybrid_rrf_rerank | Recall@10 | 0.5914 | [0.4938, 0.6848] | 50 |
| hybrid_rrf_rerank | Recall@100 | 0.7276 | [0.6390, 0.8122] | 50 |
| hybrid_rrf_rerank | MRR@10 | 0.5626 | [0.4590, 0.6700] | 50 |

## Stage latency

| Variant | Stage | P50 (ms) | P95 (ms) | Samples |
|---|---|---:|---:|---:|
| bm25 | hydrate_results | 4.56 | 5.12 | 50 |
| bm25 | sparse_retrieve | 1.81 | 4.39 | 50 |
| dense_bge_small | dense_embed_query | 22.69 | 26.96 | 50 |
| dense_bge_small | dense_retrieve | 43.71 | 47.19 | 50 |
| dense_bge_small | hydrate_results | 4.93 | 5.55 | 50 |
| hybrid_rrf | dense_embed_query | 22.16 | 27.56 | 50 |
| hybrid_rrf | dense_retrieve | 43.75 | 50.48 | 50 |
| hybrid_rrf | fuse | 0.46 | 0.51 | 50 |
| hybrid_rrf | hydrate_results | 5.02 | 5.83 | 50 |
| hybrid_rrf | sparse_retrieve | 1.75 | 4.14 | 50 |
| hybrid_rrf_rerank | dense_embed_query | 21.55 | 25.31 | 50 |
| hybrid_rrf_rerank | dense_retrieve | 43.83 | 45.40 | 50 |
| hybrid_rrf_rerank | fuse | 0.47 | 0.51 | 50 |
| hybrid_rrf_rerank | hydrate_results | 5.52 | 6.13 | 50 |
| hybrid_rrf_rerank | rerank | 3285.78 | 3487.37 | 50 |
| hybrid_rrf_rerank | sparse_retrieve | 1.72 | 4.07 | 50 |

## Variant comparisons

Paired bootstrap over queries. A difference is significant only when its
95% interval excludes zero.

| Variant A | Variant B | Metric | A - B | 95% CI | Significant |
|---|---|---|---:|---:|---|
| bm25 | dense_bge_small | nDCG@10 | -0.1265 | [-0.2363, -0.0129] | yes |
| bm25 | dense_bge_small | Recall@10 | -0.1305 | [-0.2410, -0.0188] | yes |
| bm25 | dense_bge_small | Recall@100 | -0.1552 | [-0.2621, -0.0488] | yes |
| bm25 | dense_bge_small | MRR@10 | -0.1090 | [-0.2407, +0.0336] | no |
| bm25 | hybrid_rrf | nDCG@10 | -0.0903 | [-0.1612, -0.0193] | yes |
| bm25 | hybrid_rrf | Recall@10 | -0.1376 | [-0.2207, -0.0647] | yes |
| bm25 | hybrid_rrf | Recall@100 | -0.1536 | [-0.2407, -0.0764] | yes |
| bm25 | hybrid_rrf | MRR@10 | -0.0734 | [-0.1730, +0.0351] | no |
| bm25 | hybrid_rrf_rerank | nDCG@10 | -0.1485 | [-0.2284, -0.0664] | yes |
| bm25 | hybrid_rrf_rerank | Recall@10 | -0.1810 | [-0.2764, -0.0928] | yes |
| bm25 | hybrid_rrf_rerank | Recall@100 | -0.1536 | [-0.2400, -0.0757] | yes |
| bm25 | hybrid_rrf_rerank | MRR@10 | -0.1434 | [-0.2487, -0.0452] | yes |
| dense_bge_small | hybrid_rrf | nDCG@10 | +0.0362 | [-0.0286, +0.1030] | no |
| dense_bge_small | hybrid_rrf | Recall@10 | -0.0071 | [-0.0857, +0.0686] | no |
| dense_bge_small | hybrid_rrf | Recall@100 | +0.0017 | [-0.0612, +0.0671] | no |
| dense_bge_small | hybrid_rrf | MRR@10 | +0.0355 | [-0.0500, +0.1265] | no |
| dense_bge_small | hybrid_rrf_rerank | nDCG@10 | -0.0220 | [-0.0902, +0.0422] | no |
| dense_bge_small | hybrid_rrf_rerank | Recall@10 | -0.0505 | [-0.1250, +0.0200] | no |
| dense_bge_small | hybrid_rrf_rerank | Recall@100 | +0.0017 | [-0.0607, +0.0645] | no |
| dense_bge_small | hybrid_rrf_rerank | MRR@10 | -0.0344 | [-0.1224, +0.0517] | no |
| hybrid_rrf | hybrid_rrf_rerank | nDCG@10 | -0.0582 | [-0.1197, -0.0023] | yes |
| hybrid_rrf | hybrid_rrf_rerank | Recall@10 | -0.0433 | [-0.0998, +0.0095] | no |
| hybrid_rrf | hybrid_rrf_rerank | Recall@100 | +0.0000 | [+0.0000, +0.0000] | no |
| hybrid_rrf | hybrid_rrf_rerank | MRR@10 | -0.0699 | [-0.1551, +0.0103] | no |
