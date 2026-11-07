"""Hesaplama mantığı testleri. Çalıştırmak için: python test_envanter.py  (veya: pytest)"""
import pandas as pd

import envanter_mantik as em


def test_beklenen_stok_formulu():
    assert em.beklenen_stok(10, 5, 2, 8, 1) == 8


def test_yeni_satir_fark_hesabi():
    satir = em.yeni_satir("Süt", 10, 5, 8, 2, 1, 7)
    assert satir["Beklenen Stok"] == 8
    assert satir["Fark"] == -1


def test_bos_urun_adi_reddedilir():
    try:
        em.yeni_satir("   ", 1, 0, 0, 0, 0, 1)
    except ValueError:
        return
    raise AssertionError("Boş ürün adı kabul edilmemeliydi")


def test_negatif_miktar_reddedilir():
    try:
        em.yeni_satir("Süt", -1, 0, 0, 0, 0, 0)
    except ValueError:
        return
    raise AssertionError("Negatif miktar kabul edilmemeliydi")


def test_ornek_tablo_ozeti():
    df = em.ornek_tablo()
    assert list(df.columns) == em.KOLONLAR
    assert em.ozet(df) == {"toplam_urun": 12, "net_fark": -2, "eksik": 3, "fazla": 2}
    assert em.eksik_urunler(df)[0][1] == -3


def test_satir_ekle_bos_tabloya():
    df = em.satir_ekle(em.bos_tablo(), em.yeni_satir("Çay", 1, 0, 0, 0, 0, 1))
    assert len(df) == 1 and df.loc[0, "Fark"] == 0


def test_duzenle_bozuk_veriyi_toparlar():
    ham = pd.DataFrame({"Ürün Adı": ["Çay", None], "Fark": ["2", None]})
    df = em.duzenle(ham)
    assert len(df) == 1
    assert df.loc[0, "Fark"] == 2
    assert list(df.columns) == em.KOLONLAR


if __name__ == "__main__":
    testler = [(ad, f) for ad, f in globals().items() if ad.startswith("test_")]
    for ad, f in testler:
        f()
        print("OK ", ad)
    print(f"{len(testler)} test geçti")
