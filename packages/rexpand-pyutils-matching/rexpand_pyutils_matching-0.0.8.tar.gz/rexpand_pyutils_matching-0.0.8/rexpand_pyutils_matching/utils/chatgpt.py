from openai import OpenAI


def ask_chatgpt(
    message,
    model="gpt-4o-mini",
    temperature=0,
    top_p=1,
    max_tokens=2000,
    text={"format": {"type": "text"}},
    api_key=None,
):
    if not api_key:
        raise ValueError("api_key is required")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_tokens,
        reasoning={},
        tools=[],
        input=[{"role": "user", "content": message}],
        text=text,
        stream=False,
        store=True,
    )

    return response
