# Retrieval evaluation `eca5b181-a0db-4046-a2ce-4c4e86d6d8ea`

- Dataset: `nfcorpus` (`test`)
- Variants: `bm25`, `dense_bge_small`, `hybrid_rrf`, `hybrid_rrf_rerank`
- Seed: `42`
- Results: `200`
- Indexes: `bm25`=`d6fae4ea000cade07b0b441896d3b9c6dd1d3eacbe14e4d739c41b816e19f8ae`, `dense_bge_small`=`d6fae4ea000cade07b0b441896d3b9c6dd1d3eacbe14e4d739c41b816e19f8ae`, `hybrid_rrf`=`d6fae4ea000cade07b0b441896d3b9c6dd1d3eacbe14e4d739c41b816e19f8ae`, `hybrid_rrf_rerank`=`d6fae4ea000cade07b0b441896d3b9c6dd1d3eacbe14e4d739c41b816e19f8ae`

## Quality metrics

| Variant | Metric | Mean | 95% CI | Queries |
|---|---|---:|---:|---:|
| bm25 | nDCG@10 | 0.3056 | [0.2256, 0.3874] | 50 |
| bm25 | Recall@10 | 0.1635 | [0.1096, 0.2305] | 50 |
| bm25 | Recall@100 | 0.2876 | [0.2088, 0.3753] | 50 |
| bm25 | MRR@10 | 0.5353 | [0.4173, 0.6553] | 50 |
| dense_bge_small | nDCG@10 | 0.3397 | [0.2524, 0.4225] | 50 |
| dense_bge_small | Recall@10 | 0.1582 | [0.1062, 0.2166] | 50 |
| dense_bge_small | Recall@100 | 0.3030 | [0.2446, 0.3691] | 50 |
| dense_bge_small | MRR@10 | 0.5412 | [0.4218, 0.6572] | 50 |
| hybrid_rrf | nDCG@10 | 0.3491 | [0.2688, 0.4316] | 50 |
| hybrid_rrf | Recall@10 | 0.1759 | [0.1212, 0.2364] | 50 |
| hybrid_rrf | Recall@100 | 0.3307 | [0.2621, 0.4037] | 50 |
| hybrid_rrf | MRR@10 | 0.5947 | [0.4753, 0.7057] | 50 |
| hybrid_rrf_rerank | nDCG@10 | 0.3560 | [0.2735, 0.4398] | 50 |
| hybrid_rrf_rerank | Recall@10 | 0.1797 | [0.1257, 0.2383] | 50 |
| hybrid_rrf_rerank | Recall@100 | 0.3307 | [0.2584, 0.4036] | 50 |
| hybrid_rrf_rerank | MRR@10 | 0.5742 | [0.4590, 0.6862] | 50 |

## Stage latency

| Variant | Stage | P50 (ms) | P95 (ms) | Samples |
|---|---|---:|---:|---:|
| bm25 | hydrate_results | 2.65 | 3.22 | 50 |
| bm25 | sparse_retrieve | 1.12 | 1.36 | 50 |
| dense_bge_small | dense_embed_query | 12.35 | 15.58 | 50 |
| dense_bge_small | dense_retrieve | 6.51 | 7.65 | 50 |
| dense_bge_small | hydrate_results | 3.18 | 3.73 | 50 |
| hybrid_rrf | dense_embed_query | 12.17 | 14.83 | 50 |
| hybrid_rrf | dense_retrieve | 6.53 | 7.59 | 50 |
| hybrid_rrf | fuse | 0.34 | 0.41 | 50 |
| hybrid_rrf | hydrate_results | 3.37 | 3.72 | 50 |
| hybrid_rrf | sparse_retrieve | 1.09 | 1.25 | 50 |
| hybrid_rrf_rerank | dense_embed_query | 11.84 | 15.51 | 50 |
| hybrid_rrf_rerank | dense_retrieve | 6.54 | 7.25 | 50 |
| hybrid_rrf_rerank | fuse | 0.35 | 0.40 | 50 |
| hybrid_rrf_rerank | hydrate_results | 4.33 | 4.91 | 50 |
| hybrid_rrf_rerank | rerank | 3142.58 | 3486.54 | 50 |
| hybrid_rrf_rerank | sparse_retrieve | 1.11 | 1.31 | 50 |

## Variant comparisons

Paired bootstrap over queries. A difference is significant only when its
95% interval excludes zero.

| Variant A | Variant B | Metric | A - B | 95% CI | Significant |
|---|---|---|---:|---:|---|
| bm25 | dense_bge_small | nDCG@10 | -0.0341 | [-0.0886, +0.0147] | no |
| bm25 | dense_bge_small | Recall@10 | +0.0052 | [-0.0172, +0.0311] | no |
| bm25 | dense_bge_small | Recall@100 | -0.0154 | [-0.0698, +0.0460] | no |
| bm25 | dense_bge_small | MRR@10 | -0.0059 | [-0.0976, +0.0877] | no |
| bm25 | hybrid_rrf | nDCG@10 | -0.0435 | [-0.0744, -0.0144] | yes |
| bm25 | hybrid_rrf | Recall@10 | -0.0125 | [-0.0219, -0.0039] | yes |
| bm25 | hybrid_rrf | Recall@100 | -0.0432 | [-0.0683, -0.0168] | yes |
| bm25 | hybrid_rrf | MRR@10 | -0.0593 | [-0.1330, +0.0123] | no |
| bm25 | hybrid_rrf_rerank | nDCG@10 | -0.0504 | [-0.0902, -0.0135] | yes |
| bm25 | hybrid_rrf_rerank | Recall@10 | -0.0162 | [-0.0301, -0.0040] | yes |
| bm25 | hybrid_rrf_rerank | Recall@100 | -0.0432 | [-0.0669, -0.0178] | yes |
| bm25 | hybrid_rrf_rerank | MRR@10 | -0.0389 | [-0.1174, +0.0374] | no |
| dense_bge_small | hybrid_rrf | nDCG@10 | -0.0093 | [-0.0422, +0.0268] | no |
| dense_bge_small | hybrid_rrf | Recall@10 | -0.0177 | [-0.0416, +0.0019] | no |
| dense_bge_small | hybrid_rrf | Recall@100 | -0.0278 | [-0.0679, +0.0073] | no |
| dense_bge_small | hybrid_rrf | MRR@10 | -0.0534 | [-0.1091, -0.0018] | yes |
| dense_bge_small | hybrid_rrf_rerank | nDCG@10 | -0.0163 | [-0.0507, +0.0218] | no |
| dense_bge_small | hybrid_rrf_rerank | Recall@10 | -0.0215 | [-0.0441, -0.0017] | yes |
| dense_bge_small | hybrid_rrf_rerank | Recall@100 | -0.0278 | [-0.0683, +0.0082] | no |
| dense_bge_small | hybrid_rrf_rerank | MRR@10 | -0.0330 | [-0.0987, +0.0285] | no |
| hybrid_rrf | hybrid_rrf_rerank | nDCG@10 | -0.0069 | [-0.0344, +0.0217] | no |
| hybrid_rrf | hybrid_rrf_rerank | Recall@10 | -0.0037 | [-0.0158, +0.0071] | no |
| hybrid_rrf | hybrid_rrf_rerank | Recall@100 | +0.0000 | [+0.0000, +0.0000] | no |
| hybrid_rrf | hybrid_rrf_rerank | MRR@10 | +0.0205 | [-0.0422, +0.0891] | no |
