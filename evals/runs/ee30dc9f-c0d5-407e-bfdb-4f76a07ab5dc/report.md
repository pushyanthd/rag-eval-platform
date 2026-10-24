# Retrieval evaluation `ee30dc9f-c0d5-407e-bfdb-4f76a07ab5dc`

- Dataset: `scifact` (`test`)
- Variants: `bm25`, `dense_bge_small`, `hybrid_rrf`, `hybrid_rrf_rerank`
- Seed: `42`
- Results: `200`
- Indexes: `bm25`=`f07c16036aa305192aab16b3bc3eab2a7db625e9c5d3e7d621851ba4a3e79f11`, `dense_bge_small`=`f07c16036aa305192aab16b3bc3eab2a7db625e9c5d3e7d621851ba4a3e79f11`, `hybrid_rrf`=`f07c16036aa305192aab16b3bc3eab2a7db625e9c5d3e7d621851ba4a3e79f11`, `hybrid_rrf_rerank`=`f07c16036aa305192aab16b3bc3eab2a7db625e9c5d3e7d621851ba4a3e79f11`

## Quality metrics

| Variant | Metric | Mean | 95% CI | Queries |
|---|---|---:|---:|---:|
| bm25 | nDCG@10 | 0.5671 | [0.4436, 0.6911] | 50 |
| bm25 | Recall@10 | 0.6480 | [0.5160, 0.7700] | 50 |
| bm25 | Recall@100 | 0.7960 | [0.6760, 0.9000] | 50 |
| bm25 | MRR@10 | 0.5429 | [0.4190, 0.6662] | 50 |
| dense_bge_small | nDCG@10 | 0.6808 | [0.5715, 0.7816] | 50 |
| dense_bge_small | Recall@10 | 0.8260 | [0.7200, 0.9200] | 50 |
| dense_bge_small | Recall@100 | 0.9800 | [0.9400, 1.0000] | 50 |
| dense_bge_small | MRR@10 | 0.6387 | [0.5234, 0.7471] | 50 |
| hybrid_rrf | nDCG@10 | 0.6248 | [0.5055, 0.7453] | 50 |
| hybrid_rrf | Recall@10 | 0.7460 | [0.6259, 0.8560] | 50 |
| hybrid_rrf | Recall@100 | 1.0000 | [1.0000, 1.0000] | 50 |
| hybrid_rrf | MRR@10 | 0.5914 | [0.4690, 0.7112] | 50 |
| hybrid_rrf_rerank | nDCG@10 | 0.6534 | [0.5428, 0.7577] | 50 |
| hybrid_rrf_rerank | Recall@10 | 0.8053 | [0.6933, 0.9081] | 50 |
| hybrid_rrf_rerank | Recall@100 | 1.0000 | [1.0000, 1.0000] | 50 |
| hybrid_rrf_rerank | MRR@10 | 0.6100 | [0.4941, 0.7195] | 50 |

## Stage latency

| Variant | Stage | P50 (ms) | P95 (ms) | Samples |
|---|---|---:|---:|---:|
| bm25 | hydrate_results | 4.41 | 4.87 | 50 |
| bm25 | sparse_retrieve | 1.50 | 2.05 | 50 |
| dense_bge_small | dense_embed_query | 23.90 | 33.51 | 50 |
| dense_bge_small | dense_retrieve | 8.94 | 12.40 | 50 |
| dense_bge_small | hydrate_results | 4.67 | 5.26 | 50 |
| hybrid_rrf | dense_embed_query | 22.52 | 28.58 | 50 |
| hybrid_rrf | dense_retrieve | 8.91 | 10.24 | 50 |
| hybrid_rrf | fuse | 0.41 | 0.45 | 50 |
| hybrid_rrf | hydrate_results | 4.76 | 5.45 | 50 |
| hybrid_rrf | sparse_retrieve | 1.51 | 1.62 | 50 |
| hybrid_rrf_rerank | dense_embed_query | 22.25 | 27.80 | 50 |
| hybrid_rrf_rerank | dense_retrieve | 8.89 | 10.36 | 50 |
| hybrid_rrf_rerank | fuse | 0.42 | 0.47 | 50 |
| hybrid_rrf_rerank | hydrate_results | 5.67 | 6.77 | 50 |
| hybrid_rrf_rerank | rerank | 3867.25 | 4399.58 | 50 |
| hybrid_rrf_rerank | sparse_retrieve | 1.51 | 1.57 | 50 |

## Variant comparisons

Paired bootstrap over queries. A difference is significant only when its
95% interval excludes zero.

| Variant A | Variant B | Metric | A - B | 95% CI | Significant |
|---|---|---|---:|---:|---|
| bm25 | dense_bge_small | nDCG@10 | -0.1137 | [-0.2146, -0.0021] | yes |
| bm25 | dense_bge_small | Recall@10 | -0.1780 | [-0.3080, -0.0480] | yes |
| bm25 | dense_bge_small | Recall@100 | -0.1840 | [-0.3040, -0.0759] | yes |
| bm25 | dense_bge_small | MRR@10 | -0.0959 | [-0.2097, +0.0138] | no |
| bm25 | hybrid_rrf | nDCG@10 | -0.0577 | [-0.1234, +0.0118] | no |
| bm25 | hybrid_rrf | Recall@10 | -0.0980 | [-0.1860, -0.0280] | yes |
| bm25 | hybrid_rrf | Recall@100 | -0.2040 | [-0.3240, -0.1000] | yes |
| bm25 | hybrid_rrf | MRR@10 | -0.0486 | [-0.1334, +0.0333] | no |
| bm25 | hybrid_rrf_rerank | nDCG@10 | -0.0862 | [-0.1676, -0.0057] | yes |
| bm25 | hybrid_rrf_rerank | Recall@10 | -0.1573 | [-0.2760, -0.0440] | yes |
| bm25 | hybrid_rrf_rerank | Recall@100 | -0.2040 | [-0.3200, -0.1000] | yes |
| bm25 | hybrid_rrf_rerank | MRR@10 | -0.0671 | [-0.1518, +0.0134] | no |
| dense_bge_small | hybrid_rrf | nDCG@10 | +0.0560 | [-0.0101, +0.1347] | no |
| dense_bge_small | hybrid_rrf | Recall@10 | +0.0800 | [-0.0600, +0.2200] | no |
| dense_bge_small | hybrid_rrf | Recall@100 | -0.0200 | [-0.0600, +0.0000] | no |
| dense_bge_small | hybrid_rrf | MRR@10 | +0.0473 | [-0.0086, +0.1144] | no |
| dense_bge_small | hybrid_rrf_rerank | nDCG@10 | +0.0274 | [-0.0608, +0.1194] | no |
| dense_bge_small | hybrid_rrf_rerank | Recall@10 | +0.0207 | [-0.0800, +0.1300] | no |
| dense_bge_small | hybrid_rrf_rerank | Recall@100 | -0.0200 | [-0.0600, +0.0000] | no |
| dense_bge_small | hybrid_rrf_rerank | MRR@10 | +0.0287 | [-0.0665, +0.1313] | no |
| hybrid_rrf | hybrid_rrf_rerank | nDCG@10 | -0.0285 | [-0.0936, +0.0319] | no |
| hybrid_rrf | hybrid_rrf_rerank | Recall@10 | -0.0593 | [-0.1533, +0.0280] | no |
| hybrid_rrf | hybrid_rrf_rerank | Recall@100 | +0.0000 | [+0.0000, +0.0000] | no |
| hybrid_rrf | hybrid_rrf_rerank | MRR@10 | -0.0186 | [-0.0868, +0.0480] | no |
