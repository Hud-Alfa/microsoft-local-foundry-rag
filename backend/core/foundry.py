import sys

from backend.core.config import FOUNDRY_APP_NAME


def get_manager():
    # SDK kurulu olmadan da modul import edilebilsin diye import fonksiyon icinde
    from foundry_local_sdk import Configuration, FoundryLocalManager

    # manager surec basina tekil: ikinci initialize cagrisi FoundryLocalException firlatir,
    # embedder ve generator ayni surecte yasadigi icin buradan tek noktadan kuruluyor
    if FoundryLocalManager.instance is None:
        FoundryLocalManager.initialize(Configuration(app_name=FOUNDRY_APP_NAME))
    return FoundryLocalManager.instance


def load_model(alias: str):
    def report_progress(percent: float) -> None:
        # ilk indirme yuzlerce MB surer, geri bildirim olmazsa uygulama donmus gorunur
        print(f"\r{alias} indiriliyor: {percent:.2f}%", end="", file=sys.stderr)
        if percent >= 100:
            print(file=sys.stderr)

    model = get_manager().catalog.get_model(alias)
    model.download(report_progress)
    model.load()
    return model
