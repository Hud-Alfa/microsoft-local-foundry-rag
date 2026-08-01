NO_CONTEXT_ANSWER = "Verilen belgelerde bu bilgi bulunmuyor."
EMPTY_QUESTION_ANSWER = "Lutfen bir soru yazin."

# Kural sayisi bilerek az ve "once cevapla" sirasinda: reddetme kurallari agir bastiginda
# model baglamda acikca yazan bilgiyi de tartisip cevapsiz birakiyor (olculdu).
SYSTEM_PROMPT = f"""Sen, verilen belge parcalarina dayanarak soru cevaplayan bir dokuman asistanisin.

- Cevap baglamda varsa dogrudan ve tek cumlede cevapla, cozumleme yapma.
- Cevap baglamda yoksa yalnizca "{NO_CONTEXT_ANSWER}" yaz.
- Baglamda olmayan bilgiyi genel bilginle tamamlama.
- Sorunun dilinde yaz."""

USER_PROMPT_TEMPLATE = """Baglam:
{context}

Soru: {question}"""

CONTEXT_ITEM_TEMPLATE = """[{index}] Kaynak: {filename}
{chunk_text}"""

# Qwen3-Embedding asimetrik calisir: belge parcalari ham gomulur, sorgu talimatla
# gomulur. Olcumde dogru parcanin ikinciden ayrilma farki iki katina cikti.
QUERY_INSTRUCTION_TEMPLATE = (
    "Instruct: Verilen soruya cevap iceren belge parcasini bul\nQuery: {question}"
)
