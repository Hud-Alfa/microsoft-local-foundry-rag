import json
from pathlib import Path

import pytest

from backend.prompts.system_prompts import EMPTY_QUESTION_ANSWER
from tests.evaluate_rag import (
    QUESTIONS_PATH,
    has_keyword,
    is_refusal,
    normalize,
    score,
    summarize,
)

CATEGORIES = {"answerable", "unanswerable", "ambiguous", "empty"}


def _spec(category, keywords=None, snippet=None):
    return {
        "category": category,
        "expected_keywords": keywords or [],
        "expected_chunk_snippet": snippet,
    }


def test_question_set_covers_all_categories():
    question_set = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    categories = {question["category"] for question in question_set["questions"]}

    assert categories == CATEGORIES
    assert (Path(__file__).parent.parent / "data" / "samples" / question_set["document"]).is_file()


def test_question_ids_are_unique():
    question_set = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    ids = [question["id"] for question in question_set["questions"]]

    assert len(ids) == len(set(ids))


def test_normalize_folds_turkish_characters():
    assert normalize("Şifre GÖNDERİLMEZ") == "sifre gonderilmez"


def test_keyword_matching_ignores_turkish_characters():
    assert has_keyword("Ofis 17:00'de kapanır.", ["17"])
    assert has_keyword("Yıllık izin yirmi gündür", ["yirmi"])
    assert not has_keyword("Baska bir cevap", ["17"])


def test_is_refusal_detects_variants():
    assert is_refusal("Verilen belgelerde bu bilgi bulunmuyor.")
    assert is_refusal("Belgelerde garanti suresi belirtilmemiş.")
    assert not is_refusal("Yillik izin 20 is gunudur.")


def test_answerable_needs_chunk_keyword_and_no_refusal():
    spec = _spec("answerable", ["20"], "20 is gunu")

    good = score(spec, "Yillik izin 20 is gunudur.", ["... 20 is gunu ucretli izin ..."])
    assert good["passed"] is True
    assert good["correct_chunk_retrieved"] is True

    wrong_chunk = score(spec, "Yillik izin 20 is gunudur.", ["alakasiz parca"])
    assert wrong_chunk["passed"] is False

    refused = score(spec, "Verilen belgelerde bu bilgi bulunmuyor.", ["... 20 is gunu ..."])
    assert refused["passed"] is False


def test_unanswerable_passes_only_when_refused():
    spec = _spec("unanswerable")

    assert score(spec, "Verilen belgelerde bu bilgi bulunmuyor.", ["parca"])["passed"] is True
    assert score(spec, "Garanti suresi iki yildir.", ["parca"])["passed"] is False


def test_empty_question_expects_fixed_message_and_no_sources():
    spec = _spec("empty")

    assert score(spec, EMPTY_QUESTION_ANSWER, [])["passed"] is True
    assert score(spec, EMPTY_QUESTION_ANSWER, ["parca"])["passed"] is False
    assert score(spec, "Yillik izin 20 gun.", [])["passed"] is False


def test_ambiguous_is_left_to_human_review():
    result = score(_spec("ambiguous"), "Onarim suresi uc is gunudur.", ["parca"])

    assert result["passed"] is None


def test_summarize_counts_categories_and_manual_review():
    results = [
        {"category": "answerable", "passed": True, "correct_chunk_retrieved": True,
         "sources_shown": True, "duration_seconds": 10.0},
        {"category": "answerable", "passed": False, "correct_chunk_retrieved": False,
         "sources_shown": True, "duration_seconds": 20.0},
        {"category": "ambiguous", "passed": None, "correct_chunk_retrieved": None,
         "sources_shown": True, "duration_seconds": 12.0},
        {"category": "empty", "passed": True, "correct_chunk_retrieved": None,
         "sources_shown": False, "duration_seconds": 0.0},
    ]

    summary = summarize(results)

    assert summary["total_questions"] == 4
    assert summary["scored"] == 3
    assert summary["passed"] == 2
    assert summary["manual_review"] == 1
    assert summary["correct_chunk_rate"] == 0.5
    assert summary["sources_shown_rate"] == 0.75
    assert summary["average_seconds"] == pytest.approx(10.5)
    assert summary["slowest_seconds"] == 20.0
    assert summary["by_category"]["answerable"] == {"total": 2, "passed": 1, "manual": 0}
