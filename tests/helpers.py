import pytest


def skip_if_out_of_memory(error: Exception) -> None:
    # ONNX modeli RAM'e sigmazsa "bad allocation" firlatir; bu makine durumu,
    # kod hatasi degil - testin kirmizi yanmasi sinyali bozar
    if "bad allocation" in str(error):
        pytest.skip("model bellege sigmadi (bad allocation): calisan uygulamalari kapat")
    raise error
