import os

# FIXED: the original version hardcoded a high-entropy API key literal here
# (see git history for the planted, vulnerable version this replaced). Real
# secrets now load from environment variables and are never committed - see
# .env.example for the variable name, which holds no real value.
THIRD_PARTY_API_KEY = os.environ.get("THIRD_PARTY_API_KEY")
