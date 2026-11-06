"""Values pinned by the spec. Change them only after the spec changes."""

UPSTREAM_REPO_URL = "https://github.com/NVIDIA/auto-ontology.git"
UPSTREAM_COMMIT = "cdaf61e1bd0cf3820d11d72b43bb460816aebbd3"

# Default hosted NIM configuration named in S3.
# Chat pin history (spec owner amendments, 2026-11-05): the original pin
# nvidia/nemotron-3-nano-30b-a3b is end of life on the hosted endpoint
# (HTTP 410 Gone). The Amendment 1 pin nvidia/nemotron-nano-3-30b-a3b is
# catalog listed but returns HTTP 404 for this account. Amendment 2 pins
# the candidate that answered the harness live preflight (HTTP 200).
CHAT_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
EMBEDDING_MODEL = "nvidia/nemotron-3-embed-1b"
RERANK_MODEL = "nvidia/llama-nemotron-rerank-vl-1b-v2"

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

# The key reaches the run only through this environment variable, which the
# workflow fills from the repository secret of the same name.
API_KEY_ENV = "NVIDIA_API_KEY"

# Generation settings shared by both S4 arms. These are the settings the
# pinned upstream text-to-SQL client uses (auto_ontology/utils/llm_invoke.py,
# get_llm_client defaults, called without overrides from
# retrieval/text_to_sql/main.py); upstream sends no seed, so neither arm does.
GENERATION_SETTINGS = {"temperature": 0.0, "max_tokens": 8192}

# Run configurations. "default" measures the stack exactly as the pinned
# upstream ships it. "live-internals" (spec Amendment 3) additionally wires
# every internal chat model slot of the stack to CHAT_MODEL; nothing else
# changes between the two configurations.
DEFAULT_CONFIGURATION = "default"
LIVE_CONFIGURATION = "live-internals"
CONFIGURATIONS = (DEFAULT_CONFIGURATION, LIVE_CONFIGURATION)

# The pinned upstream's internal chat model slots at cdaf61e1: the
# REASONING and NON_REASONING triplets every internal LLM consumer
# resolves through (auto_ontology/utils/llm_invoke.py), and the shared
# DEFAULT_MODELS triplet each triplet field falls back to when unset
# (auto_ontology/utils/model_config.py; .env.example at the same commit).
INTERNAL_CHAT_MODEL_SLOTS = ("DEFAULT_MODELS_MODEL", "REASONING_MODEL", "NON_REASONING_MODEL")
