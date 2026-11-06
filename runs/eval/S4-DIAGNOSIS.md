# S4 DIAGNOSIS: why the Auto Ontology arm produced no answers

Diagnosis written after run 42127124473, from the evidence committed with
that run (runs/eval/s4/ event streams, runs/eval/compose-logs.txt,
runs/eval/catalog.yaml) and from the pinned upstream source at commit
cdaf61e1bd0cf3820d11d72b43bb460816aebbd3. It does not modify RESULTS.md
and no part of the evaluation was rerun.

## Verdict

The Auto Ontology arm was silent because the product, run at its shipped
default configuration, answers questions with its own internal models, and
every internal model pin in that default configuration pointed at
nvidia/nemotron-3-nano-30b-a3b, a model NVIDIA retired on 2026-09-01.
Each internal call failed with HTTP 410 Gone, SQL generation returned
nothing after three attempts, and the product's chat pipeline fell back
to its canned failure result for all 12 questions.

## The mechanism, step by step

1. The harness drove the product through its own chat API
   (POST /api/chat/completions on the running stack) and recorded the
   server-sent event stream per question. The harness recorded faithfully
   what the product returned; nothing was swallowed on the harness side.

2. Inside the product, each question ran the text-to-SQL graph:
   question_intent, question_extraction, retrieve_candidates,
   prepare_candidates, construct_sql_from_candidates. Retrieval ran on the
   embedding and rerank models, which answer normally. The LLM steps did
   not. The API service log records, verbatim:

   "The model 'nvidia/nemotron-3-nano-30b-a3b' has reached its end of life
   on 2026-09-01T09:00:00Z and is no longer available."

   "Reasoning LLM also failed for QuestionExtractionModel: Exception:
   [410] Gone"

   Question extraction fell back to the original question text and the
   graph continued.

3. At SQL construction the same failure was terminal. The log records
   three failed attempts for SQLGenerationModel, then, verbatim:

   "LLM returned None after 3 attempts."

   "Generated unconstructable SQL response: LLM failed to produce a
   response...."

   The graph routed to its designed fallback node,
   unconstructable_sql_response, and the chat API returned a result whose
   answer is, verbatim from every committed event stream:

   "response": "LLM failed to produce a response.", "sql_code": "",
   "sql_response_from_db": null

   With sql_code empty and no database response, the harness recorded
   "(no answer)" and "No SQL was produced." for every question. That
   recording is accurate: no SQL was produced.

4. The same root cause had already degraded S3. During ontology
   compilation the ingestion service's LLM steps (foreign and primary key
   inference, column descriptions, table terms) failed with the same
   HTTP 410 and were skipped with warnings; the service logged that the
   column description batch had failed and that it was proceeding without
   them. Compilation completed through the deterministic path, which is
   why the catalog exported in 15.42 s is structurally complete but
   carries no authored semantics: in runs/eval/catalog.yaml, every
   table and column description in the data layer is blank (77 of the
   88 description fields are empty, and the 11 that are not are
   templated lines of the form "Business entity represented by
   table ..." plus date format notes, not definitions). A catalog
   with no definitions in it had nothing that could surface the four
   planted definitional
   conflicts, which is consistent with the reconciliation outcome in
   RESULTS.md (all four conflicts ignored, counted marks resting on bare
   table names).

## Why the internal models were the retired ones

The stack was run the way the spec required: the default hosted NIM
configuration, meaning the upstream built-in defaults. At the pinned
upstream commit, the shipped .env.example sets all three internal model
roles to the retired model, verbatim:

DEFAULT_MODELS_MODEL=nvidia/nemotron-3-nano-30b-a3b
REASONING_MODEL=nvidia/nemotron-3-nano-30b-a3b
NON_REASONING_MODEL=nvidia/nemotron-3-nano-30b-a3b

The harness deliberately dropped the template's model lines from the
stack environment so these built-in defaults applied, and supplied only
the API key. The evaluation's own pinned chat model,
nvidia/nemotron-3.5-lightning-30b-a3b, was never invoked inside the
product: it is the model the raw-schema arm called directly (8 of 12
correct) and the model the preflight verified. The product's internal
roles accept environment overrides, but by design the run did not set
them; overriding them would have measured a hand-configured stack, not
the default one the spec named.

## Uniformity across the 12 questions

Total. All 12 committed files runs/eval/s4/Q01 to Q12
.ontology.events.json are byte-identical (3750 bytes each, same content
hash): the same two passes through the same six nodes, the same terminal
node unconstructable_sql_response, the same fallback result. No question
failed in a different way from any other, because no question ever
reached a working LLM inside the product.

## Classification

- Product behavior (primary cause). At the pinned commit, the product's
  shipped defaults point every internal LLM role at a model its own
  vendor retired before this run, and the product degrades silently when
  those calls fail: the smoke checks pass, a catalog is exported, and
  the chat endpoint returns a generic fallback sentence instead of an
  error anyone would act on. Nothing in the run signals that the
  semantic layer is running without its models.
- Evaluation scope (contributing factor, disclosed). The Auto Ontology
  arm measures the product exactly as it ships by default against the
  hosted endpoint. It does not measure the product's text-to-SQL pipeline
  with a live model wired into its internal roles, because the spec's
  default-configuration rule forbade setting those overrides. The
  0 of 12 is a true result about the default configuration and a
  non-result about the pipeline's capability with a working model.
- Model behavior (exonerated). The pinned chat model did not cause the
  silence; it was never called by the Auto Ontology arm. Given the raw
  schema directly, the same model answered 8 of 12.

## What this diagnosis does and does not license in public

Licensed:

- Out of the box, against NVIDIA's hosted endpoint, the product's chat
  answered 0 of 12 questions, because its built-in default model has
  been retired, and the product degrades silently instead of reporting
  that its models are gone.
- The generated ontology was fast (15.42 s) and structurally complete,
  but carried no authored definitions: every table and column
  description blank, and none of the four planted definitional
  conflicts surfaced.
- The control arm, the same live model given only the raw schema,
  answered 8 of 12.

Not licensed:

- Any claim that Auto Ontology's text-to-SQL pipeline, with a live model
  in its internal roles, answers worse than a model given the raw
  schema. That configuration was not run.
- Any claim attributing the 0 of 12 to the pinned chat model, or to the
  quality of the generated ontology as a question-answering asset. The
  ontology was never actually used by a working model in that arm.
- Any claim about scale or production schemas; the fixture limits in
  RESULTS.md stand unchanged.

## What remains unknown

- How the pipeline performs once its internal model roles point at a
  live model. Answering that needs a new run under a spec amendment that
  sets the overrides; it is a different measurement from the one the
  spec defined.
- Why each event stream contains two identical passes through the graph
  (an internal retry at the chat layer is the plausible reading; the
  committed logs tail only the last question's processing, so the
  repetition is observed, not explained). It does not affect the
  verdict: both passes end at the same node for the same reason.
