"""All prompts used in the project are defined here."""

# the default system prompt to be used across tasks
BASE_SYSTEM_PROMPT = "You are a helpful assistant."

# the default system prompt to be used across coding tasks
CODE_SYSTEM_PROMPT = "You are a helpful and knowledgeable code assistant!"

# the system prompt to be used for generating lists of words
LIST_SYSTEM_PROMPT = (
    "You are a helpful assistant that provides lists of words.\n"
    "You only respond in correctly formatted python lists, containing only strings."
)

# the system prompt to be used for generating a boolean value from the input
BOOL_SYSTEM_PROMPT = (
    "You are a helpful assistant that provides boolean values.\n"
    "You only respond in python boolean values, True or False, only, and nothing else."
)
