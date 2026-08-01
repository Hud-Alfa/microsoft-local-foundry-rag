import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import (  # noqa: E402
    ANSWER_RANDOM_SEED,
    ANSWER_TEMPERATURE,
    CHAT_MODEL_ALIAS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL_ALIAS,
    MAX_CONTEXT_CHARS,
    TOP_K,
)
from backend.core.rag_service import ask_question, create_collection, index_document  # noqa: E402
from backend.database.db import get_connection, init_db  # noqa: E402
from backend.prompts.system_prompts import EMPTY_QUESTION_ANSWER  # noqa: E402

TESTS_DIR = Path(__file__).resolve().parent
QUESTIONS_PATH = TESTS_DIR / "test_questions.json"
RESULTS_PATH = TESTS_DIR / "evaluation_results.json"
SAMPLES_DIR = TESTS_DIR.parent / "data" / "samples"

TURKISH_MAP = str.maketrans("çğıöşüâîÇĞİÖŞÜ", "cgiosuaiCGIOSU")
REFUSAL_MARKERS = ("bulunmuyor", "bulunmamakta", "belirtilmemis", "yer almamakta", "bilgi yok")


def normalize(text: str) -> str:
    return text.translate(TURKISH_MAP).lower()


def is_refusal(answer: str) -> bool:
    normalized = normalize(answer)
    return any(marker in normalized for marker in REFUSAL_MARKERS)


def has_keyword(answer: str, keywords: list[str]) -> bool:
    normalized = normalize(answer)
    return any(normalize(keyword) in normalized for keyword in keywords)


def score(question_spec: dict, answer: str, retrieved_texts: list[str]) -> dict:
    category = question_spec["category"]
    snippet = question_spec.get("expected_chunk_snippet")
    keywords = question_spec.get("expected_keywords", [])

    correct_chunk = None
    if snippet:
        correct_chunk = any(normalize(snippet) in normalize(text) for text in retrieved_texts)

    refused = is_refusal(answer)
    keyword_hit = has_keyword(answer, keywords) if keywords else None

    if category == "answerable":
        passed = bool(correct_chunk) and bool(keyword_hit) and not refused
    elif category == "unanswerable":
        # basari olcutu: uydurmamak
        passed = refused
    elif category == "empty":
        passed = answer.strip() == EMPTY_QUESTION_ANSWER and not retrieved_texts
    else:
        # belirsiz sorularda tek dogru cevap yok, insan degerlendirmesine birakilir
        passed = None

    return {
        "correct_chunk_retrieved": correct_chunk,
        "keyword_hit": keyword_hit,
        "refused": refused,
        "passed": passed,
    }


def load_chunk_texts(db_path: Path) -> dict[tuple[str, int], str]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT d.filename, c.chunk_index, c.chunk_text"
            " FROM chunks c JOIN documents d ON d.id = c.document_id"
        ).fetchall()
    finally:
        connection.close()
    return {(row["filename"], row["chunk_index"]): row["chunk_text"] for row in rows}


def build_collection(db_path: Path, document_name: str) -> int:
    init_db(db_path)
    collection_id = create_collection("degerlendirme", db_path=db_path)
    index_document(str(SAMPLES_DIR / document_name), collection_id, db_path=db_path)
    return collection_id


def summarize(results: list[dict]) -> dict:
    by_category: dict[str, dict] = {}
    for result in results:
        bucket = by_category.setdefault(
            result["category"], {"total": 0, "passed": 0, "manual": 0}
        )
        bucket["total"] += 1
        if result["passed"] is None:
            bucket["manual"] += 1
        elif result["passed"]:
            bucket["passed"] += 1

    scored = [result for result in results if result["passed"] is not None]
    chunk_checked = [
        result for result in results if result["correct_chunk_retrieved"] is not None
    ]
    durations = [result["duration_seconds"] for result in results]

    return {
        "total_questions": len(results),
        "passed": sum(1 for result in scored if result["passed"]),
        "scored": len(scored),
        "manual_review": len(results) - len(scored),
        "correct_chunk_rate": (
            round(sum(r["correct_chunk_retrieved"] for r in chunk_checked) / len(chunk_checked), 3)
            if chunk_checked
            else None
        ),
        "sources_shown_rate": round(
            sum(1 for result in results if result["sources_shown"]) / len(results), 3
        ),
        "average_seconds": round(sum(durations) / len(durations), 2),
        "slowest_seconds": round(max(durations), 2),
        "by_category": by_category,
    }


def run_evaluation() -> dict:
    question_set = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "evaluation.db"
        collection_id = build_collection(db_path, question_set["document"])
        chunk_texts = load_chunk_texts(db_path)

        results = []
        for question_spec in question_set["questions"]:
            start = time.time()
            answer_payload = ask_question(
                question_spec["question"], collection_id, db_path=db_path
            )
            duration = time.time() - start

            sources = answer_payload["sources"]
            retrieved_texts = [
                chunk_texts.get((source["filename"], source["chunk_index"]), "")
                for source in sources
            ]

            result = {
                "id": question_spec["id"],
                "category": question_spec["category"],
                "question": question_spec["question"],
                "answer": answer_payload["answer"],
                "duration_seconds": round(duration, 2),
                "sources_shown": bool(sources),
                "sources": sources,
                **score(question_spec, answer_payload["answer"], retrieved_texts),
            }
            results.append(result)
            print(
                f"[{result['category'][:4]}] #{result['id']:>2} "
                f"{'OK ' if result['passed'] else ('-- ' if result['passed'] is None else 'HATA')} "
                f"{result['duration_seconds']:>5.1f}s  {question_spec['question'][:45]}"
            )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "document": question_set["document"],
        "config": {
            "chat_model": CHAT_MODEL_ALIAS,
            "embedding_model": EMBEDDING_MODEL_ALIAS,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "top_k": TOP_K,
            "max_context_chars": MAX_CONTEXT_CHARS,
            "temperature": ANSWER_TEMPERATURE,
            "random_seed": ANSWER_RANDOM_SEED,
        },
        "summary": summarize(results),
        "results": results,
    }


def main() -> None:
    report = run_evaluation()
    RESULTS_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = report["summary"]
    print(
        f"\n{summary['passed']}/{summary['scored']} basarili "
        f"({summary['manual_review']} soru insan degerlendirmesine birakildi)"
    )
    print(f"dogru chunk orani : {summary['correct_chunk_rate']}")
    print(f"kaynak gosterme   : {summary['sources_shown_rate']}")
    print(f"ortalama sure     : {summary['average_seconds']}s (en yavas {summary['slowest_seconds']}s)")
    print(f"\nsonuclar: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
