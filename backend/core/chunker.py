import re

from backend.core.config import CHUNK_OVERLAP, CHUNK_SIZE

# paragraf = arada bos satir olmayan ardisik satirlar
PARAGRAPH_PATTERN = re.compile(r"[^\n]+(?:\n[^\n]+)*")


def _split_long_paragraph(
    start: int, end: int, chunk_size: int, overlap: int
) -> list[tuple[int, int]]:
    spans = []
    step = chunk_size - overlap
    position = start
    while position < end:
        window_end = min(position + chunk_size, end)
        spans.append((position, window_end))
        if window_end == end:
            break
        position += step
    return spans


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

    # Paragraf sinirlarina saygili paketleme: baslik kendi bolumuyle ayni parcada kalir,
    # olcumde dogru parcayi bulma 6/7 -> 7/7, ayrim gucu 0.087 -> 0.147 oldu.
    spans: list[tuple[int, int]] = []
    open_span: tuple[int, int] | None = None
    for match in PARAGRAPH_PATTERN.finditer(text):
        start, end = match.span()

        if end - start > chunk_size:
            if open_span is not None:
                spans.append(open_span)
                open_span = None
            spans.extend(_split_long_paragraph(start, end, chunk_size, overlap))
            continue

        if open_span is None:
            open_span = (start, end)
        elif end - open_span[0] <= chunk_size:
            open_span = (open_span[0], end)
        else:
            spans.append(open_span)
            open_span = (start, end)

    if open_span is not None:
        spans.append(open_span)

    return [
        {
            "chunk_index": index,
            # start_char/end_char orijinal metne isaret ettigi icin parca kirpilmaz
            "chunk_text": text[start:end],
            "start_char": start,
            "end_char": end,
        }
        for index, (start, end) in enumerate(spans)
    ]
