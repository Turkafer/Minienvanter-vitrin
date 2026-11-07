"""Minienvanter: arayüzden bağımsız stok hesaplama ve veri düzenleme fonksiyonları.

Bu dosya Streamlit'e bağımlı değildir, bu yüzden tek başına test edilebilir.
"""
import pandas as pd

KOLONLAR = [
    "Ürün Adı",
    "Başlangıç",
    "Gelen",
    "Satan",
    "Trf Gelen",
    "Trf Giden",
    "Fiziksel Sayım",
    "Beklenen Stok",
    "Fark",
]
SAYISAL = [k for k in KOLONLAR if k != "Ürün Adı"]

# (ürün, başlangıç, gelen, satan, trf gelen, trf giden, fiziksel sayım)
ORNEK_URUNLER = [
    ("Süt 1 L", 48, 24, 61, 0, 0, 11),
    ("Ekmek", 60, 120, 168, 0, 0, 9),
    ("Yumurta 15'li", 30, 40, 52, 0, 0, 18),
    ("Ayçiçek Yağı 1 L", 36, 0, 25, 12, 6, 17),
    ("Makarna 500 g", 80, 0, 34, 0, 0, 49),
    ("Çay 500 g", 24, 12, 15, 0, 4, 15),
    ("Toz Şeker 1 kg", 50, 0, 22, 0, 0, 28),
    ("Su 5 L", 40, 60, 70, 0, 10, 18),
    ("Çamaşır Deterjanı 3 kg", 10, 0, 6, 5, 0, 9),
    ("Domates (kg)", 40, 0, 37, 0, 0, 5),
    ("Gazlı İçecek 2,5 L", 24, 24, 30, 0, 6, 12),
    ("Tuvalet Kağıdı 12'li", 15, 0, 9, 0, 3, 3),
]


def beklenen_stok(baslangic, gelen, t_gelen, satan, t_giden):
    """Olması gereken stok: (başlangıç + gelen + transfer gelen) - (satan + transfer giden)."""
    return (baslangic + gelen + t_gelen) - (satan + t_giden)


def yeni_satir(urun, baslangic, gelen, satan, t_gelen, t_giden, fiziksel):
    """Form girdisinden tablo satırı üretir. Geçersiz girişte ValueError fırlatır."""
    urun = (urun or "").strip()
    if not urun:
        raise ValueError("Ürün adı boş olamaz.")
    if min(baslangic, gelen, satan, t_gelen, t_giden, fiziksel) < 0:
        raise ValueError("Miktarlar negatif olamaz.")

    beklenen = beklenen_stok(baslangic, gelen, t_gelen, satan, t_giden)
    return {
        "Ürün Adı": urun,
        "Başlangıç": int(baslangic),
        "Gelen": int(gelen),
        "Satan": int(satan),
        "Trf Gelen": int(t_gelen),
        "Trf Giden": int(t_giden),
        "Fiziksel Sayım": int(fiziksel),
        "Beklenen Stok": int(beklenen),
        "Fark": int(fiziksel - beklenen),
    }


def bos_tablo():
    return pd.DataFrame(columns=KOLONLAR)


def ornek_tablo():
    return pd.DataFrame([yeni_satir(*u) for u in ORNEK_URUNLER], columns=KOLONLAR)


def satir_ekle(df, satir):
    """Tabloya satır ekler (boş tabloyla concat uyarısı vermeden)."""
    if df is None or df.empty:
        return pd.DataFrame([satir], columns=KOLONLAR)
    return pd.concat([df, pd.DataFrame([satir])], ignore_index=True)


def duzenle(df):
    """Dışarıdan (ör. Google Sheets) gelen tabloyu beklenen şemaya oturtur."""
    df = df.reindex(columns=KOLONLAR).dropna(how="all")
    df["Ürün Adı"] = df["Ürün Adı"].fillna("").astype(str)
    df[SAYISAL] = df[SAYISAL].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int)
    return df.reset_index(drop=True)


def ozet(df):
    if df.empty:
        return {"toplam_urun": 0, "net_fark": 0, "eksik": 0, "fazla": 0}
    return {
        "toplam_urun": int(len(df)),
        "net_fark": int(df["Fark"].sum()),
        "eksik": int((df["Fark"] < 0).sum()),
        "fazla": int((df["Fark"] > 0).sum()),
    }


def eksik_urunler(df):
    """Sayımda eksik çıkan ürünleri (ad, fark) olarak, en çok eksik olandan başlayarak döndürür."""
    if df.empty:
        return []
    eksik = df[df["Fark"] < 0].sort_values("Fark")
    return [(ad, int(f)) for ad, f in zip(eksik["Ürün Adı"], eksik["Fark"])]
