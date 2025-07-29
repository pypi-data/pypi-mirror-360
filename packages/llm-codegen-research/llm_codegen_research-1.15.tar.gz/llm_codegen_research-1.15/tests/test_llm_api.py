"""Test our connection and usage of the LLM APIs."""

from llm_cgr import BASE_SYSTEM_PROMPT, generate, generate_bool, generate_list, get_llm


def test_generate(model):
    """
    Test the generate method.
    """
    user = "How many r's are in 'strawberry'?"
    response = generate(
        user=user,
        model=model,
        system=BASE_SYSTEM_PROMPT,
    )
    assert isinstance(response, str)
    assert len(response) > 0


def test_generate_list(openai_model):
    """
    Test the generate_list method.
    """
    user = "List the first 5 prime numbers."
    response = generate_list(user=user, model=openai_model)
    assert isinstance(response, list)
    assert len(response) > 0
    assert all(isinstance(item, str) for item in response)


def test_generate_bool(openai_model):
    """
    Test the generate_bool method.
    """
    user = "Is the sky blue?"
    response = generate_bool(user=user, model=openai_model)
    assert isinstance(response, bool)
    assert response in {True, False}
    assert response is not None


def test_chat_flow(openai_model):
    """
    Test the chat flow method.
    """
    llm = get_llm(model=openai_model)

    response = llm.chat(user="Hello, can you help me with code?")
    assert isinstance(response, str)
    assert len(response) > 0

    response = llm.chat(user="Great, how can you help me?")
    assert isinstance(response, str)
    assert len(response) > 0

    history = llm.history
    assert isinstance(history, list)
    assert len(history) == 4
    assert all(isinstance(item, dict) for item in history)
    assert all(len(item) == 2 for item in history)

    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello, can you help me with code?"

    assert history[1]["role"] == "assistant"
    assert len(history[1]["content"]) > 0

    assert history[2]["role"] == "user"
    assert history[2]["content"] != "Hello, can you help me with code?"

    assert history[3]["role"] == "assistant"
    assert len(history[3]["content"]) > 0
