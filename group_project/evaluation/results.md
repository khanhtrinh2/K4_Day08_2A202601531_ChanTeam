# RAG Evaluation Results — Offline QA Run

## Run metadata

- Test cases: 18
- Framework: Offline lexical proxy (not RAGAS)
- Pipeline: Task 10 generate_with_citation
- Generated: 2026-08-04 08:50 UTC
- Config A: hybrid retrieval with `top_k=5`
- Config B: hybrid retrieval with `top_k=3`

## Overall scores (A/B)

| Metric | Config A | Config B | Δ (A−B) |
|---|---:|---:|---:|
| Faithfulness | 0.622 | 0.622 | +0.000 |
| Answer relevance | 1.000 | 1.000 | +0.000 |
| Context recall | 0.408 | 0.408 | +0.000 |
| Context precision | 0.922 | 0.926 | -0.004 |
| **Average** | **0.738** | **0.739** | **-0.001** |

## A/B conclusion

**Config B** has the higher average score in this run. Config A prioritises evidence coverage; Config B reduces context size and is useful when response latency or prompt cost is more important. Re-run with `--backend ragas` and a configured judge LLM before using this report as a production quality gate.

## Worst performers (Config A)

| # | Question | Faith. | Relevance | Recall | Precision | Weakest metric |
|---:|---|---:|---:|---:|---:|---|
| 1 | Người bán có bao lâu để phản hồi yêu cầu trả hàng? | 0.684 | 1.000 | 0.143 | 0.000 | Context precision |
| 2 | Tiêu đề sản phẩm phải tuân thủ tiêu chuẩn gì? | 0.588 | 1.000 | 0.167 | 1.000 | Context recall |
| 3 | Làm sao để theo dõi đơn hàng đang giao? | 0.500 | 1.000 | 0.286 | 1.000 | Context recall |

## Recommendations

1. Improve metadata and chunk boundaries around policy tables/lists so retrieval preserves the exact eligibility and time-limit clauses.
2. Add query rewriting for follow-up questions and evaluate each turn with its conversation context.
3. Use the RAGAS backend with an LLM judge in CI before releases; retain this offline mode only as a deterministic smoke test.
