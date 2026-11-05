# Builder preflight finding (wo-gh-1), 2026-11-05

This is not a result of the evaluation. It is a blocker found while building the harness, and it must be resolved before S3 and S4 can produce evidence.

On 2026-11-05 a direct call to the hosted NIM endpoint `https://integrate.api.nvidia.com/v1/chat/completions` with the spec's chat model returned:

    HTTP 410 Gone: "The model 'nvidia/nemotron-3-nano-30b-a3b' has reached its end of life on 2026-09-01T09:00:00Z and is no longer available."

The same key works for the other two pinned models:
- `nvidia/nemotron-3-embed-1b` (embeddings): HTTP 200
- `nvidia/llama-nemotron-rerank-vl-1b-v2` (reranking): HTTP 200

Consequences under the spec as written:
- The pinned upstream commit's default configuration uses this model for ontology generation and chat. On the hosted endpoint, S3 (ontology generation) and the Auto Ontology arm of S4 cannot succeed.
- The spec forbids falling back to another model. The harness therefore fails closed at a preflight stage before S1 (`auto_ontology_eval.live.stage_preflight`), so it does not spend a 30-minute stack build first.

Decision needed from the spec owner (a spec change, not a builder choice): pin a replacement chat model and record that the upstream default is end-of-life. The hosted catalog on 2026-11-05 listed these candidates, among others:
- `nvidia/nemotron-3.5-lightning-30b-a3b`
- `nvidia/nemotron-nano-3-30b-a3b`
- `nvidia/nemotron-3-super-120b-a12b`

After the spec changes, update `config.CHAT_MODEL` and `tests/_support.CHAT_MODEL`. The harness uses that value for both S4 arms and for the upstream `.env`.
