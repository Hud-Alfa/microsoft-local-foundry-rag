import importlib.util
from dataclasses import dataclass

import pytest

from backend.core import generator
from backend.core.config import CHAT_MODEL_ALIAS
from backend.prompts.system_prompts import NO_CONTEXT_ANSWER, SYSTEM_PROMPT

is_foundry_installed = importlib.util.find_spec("foundry_local_sdk") is not None


@dataclass
class FakeMessage:
    content: str


@dataclass
class FakeChoice:
    message: FakeMessage


@dataclass
class FakeResponse:
    choices: list[FakeChoice]


class FakeChatClient:
    def __init__(self, answer="  model cevabi  "):
        self.answer = answer
        self.calls = []

    def complete_chat(self, messages):
        self.calls.append(messages)
        return FakeResponse(choices=[FakeChoice(message=FakeMessage(self.answer))])


@pytest.fixture
def fake_client(monkeypatch):
    client = FakeChatClient()
    monkeypatch.setattr(generator, "get_chat_client", lambda: client)
    return client


def _chunk(filename, text, index=0):
    return {"filename": filename, "chunk_text": text, "chunk_index": index}


def test_answer_is_taken_from_model_response(fake_client):
    answer = generator.generate_answer("soru?", [_chunk("a.txt", "bilgi")])

    assert answer == "model cevabi"


def test_prompt_carries_system_rules_and_question(fake_client):
    generator.generate_answer("Gaz borusu kac cm?", [_chunk("a.txt", "boru 20 cm")])

    system_message, user_message = fake_client.calls[0]
    assert system_message == {"role": "system", "content": SYSTEM_PROMPT}
    assert user_message["role"] == "user"
    assert "Gaz borusu kac cm?" in user_message["content"]
    assert "boru 20 cm" in user_message["content"]


def test_context_chunks_are_numbered_with_filenames(fake_client):
    generator.generate_answer(
        "soru?",
        [_chunk("ilk.txt", "ilk parca"), _chunk("ikinci.pdf", "ikinci parca")],
    )

    content = fake_client.calls[0][1]["content"]
    assert "[1] Kaynak: ilk.txt" in content
    assert "[2] Kaynak: ikinci.pdf" in content
    assert content.index("ilk parca") < content.index("ikinci parca")


def test_empty_context_does_not_call_model(monkeypatch):
    def fail():
        raise AssertionError("baglam yokken model cagrilmamali")

    monkeypatch.setattr(generator, "get_chat_client", fail)

    assert generator.generate_answer("soru?", []) == NO_CONTEXT_ANSWER


def test_build_context_keeps_retriever_order():
    context = generator.build_context(
        [_chunk("a.txt", "birinci"), _chunk("b.txt", "ikinci"), _chunk("c.txt", "ucuncu")]
    )

    assert context.count("Kaynak:") == 3
    assert context.index("birinci") < context.index("ikinci") < context.index("ucuncu")


@pytest.mark.skipif(
    not is_foundry_installed,
    reason="Foundry Local SDK kurulu degil (pip install foundry-local-sdk-winml)",
)
def test_generate_answer_against_foundry_local():
    from backend.core.foundry import get_manager

    cached = get_manager().catalog.get_cached_models()
    # test multi-GB indirme tetiklemesin; model onceden indirilmisse calisir
    if not any(getattr(model, "alias", None) == CHAT_MODEL_ALIAS for model in cached):
        pytest.skip(f"{CHAT_MODEL_ALIAS} indirilmemis: foundry model download ile indir")

    answer = generator.generate_answer(
        "Servis kutusu kac adet olmali?",
        [_chunk("kural.txt", "Her binada tek bir servis kutusu bulunur.")],
    )

    # cevabin icerik kalitesi burada olculmez (kucuk modelde kirilgan olur),
    # o degerlendirme tests/evaluate_rag.py'ye ait
    assert isinstance(answer, str)
    assert answer.strip()
