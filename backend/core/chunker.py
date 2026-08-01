from backend.core.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError(f"chunk_size pozitif olmali: {chunk_size}")
    # overlap >= chunk_size olursa pencere ilerlemez, sonsuz donguye girilir
    if not 0 <= overlap < chunk_size:
        raise ValueError(
            f"overlap 0 ile chunk_size arasinda olmali: "
            f"overlap={overlap}, chunk_size={chunk_size}"
        )

    chunks = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(
            {
                "chunk_index": len(chunks),
                # start_char/end_char orijinal metne isaret ettigi icin parca kirpilmaz
                "chunk_text": text[start:end],
                "start_char": start,
                "end_char": end,
            }
        )
        if end == len(text):
            break
        start += step

    return chunks
