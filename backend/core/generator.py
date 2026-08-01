from backend.core.config import (
    ANSWER_MAX_TOKENS,
    ANSWER_RANDOM_SEED,
    ANSWER_TEMPERATURE,
    CHAT_MODEL_ALIAS,
    MAX_CONTEXT_CHARS,
)
from backend.core.foundry import load_model
from backend.prompts.system_prompts import (
    CONTEXT_ITEM_TEMPLATE,
    NO_CONTEXT_ANSWER,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)

_chat_client = None


def get_chat_client():
    global _chat_client
    if _chat_client is None:
        client = load_model(CHAT_MODEL_ALIAS).get_chat_client()
        client.settings.temperature = ANSWER_TEMPERATURE
        client.settings.max_tokens = ANSWER_MAX_TOKENS
        client.settings.random_seed = ANSWER_RANDOM_SEED
        _chat_client = client
    return _chat_client


def fit_context(context_chunks: list[dict], max_chars: int = MAX_CONTEXT_CHARS) -> list[dict]:
    fitted = []
    used_chars = 0
    for chunk in context_chunks:
        chunk_length = len(chunk["chunk_text"])
        if fitted and used_chars + chunk_length > max_chars:
            break
        fitted.append(chunk)
        used_chars += chunk_length
    return fitted


def build_context(context_chunks: list[dict]) -> str:
    return "\n\n".join(
        CONTEXT_ITEM_TEMPLATE.format(
            index=index,
            filename=chunk["filename"],
            chunk_text=chunk["chunk_text"],
        )
        for index, chunk in enumerate(context_chunks, start=1)
    )


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    # baglam yoksa modele sormaya gerek yok, uydurma riskini bastan kesiyoruz
    if not context_chunks:
        return NO_CONTEXT_ANSWER

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                context=build_context(context_chunks), question=question
            ),
        },
    ]

    response = get_chat_client().complete_chat(messages)
    return response.choices[0].message.content.strip()
