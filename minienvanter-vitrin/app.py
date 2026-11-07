"""Minienvanter: market ve küçük işletmeler için stok mutabakat paneli.

İki modda çalışır:
  * Demo modu  : secrets ayarı yoksa. Örnek market verisiyle açılır, kayıtlar oturumda tutulur.
  * Bulut modu : .streamlit/secrets.toml içinde [connections.gsheets] varsa.
                 Kayıtlar Google Sheets'e canlı yazılır.
"""
import streamlit as st

import envanter_mantik as em

st.set_page_config(page_title="Minienvanter", layout="wide", page_icon="📦")

SAYFA = "Sayfa1"


def bulut_ayari_var():
    try:
        return "gsheets" in st.secrets["connections"]
    except Exception:
        return False


BULUT = bulut_ayari_var()


# ---------- Veri katmanı ----------
def sheets_baglantisi():
    from streamlit_gsheets import GSheetsConnection

    return st.connection("gsheets", type=GSheetsConnection)


def sheets_hatasi(hata):
    st.error(
        "Google Sheets bağlantısı kurulamadı. secrets ayarlarını ve tablonun "
        "servis hesabıyla paylaşıldığını kontrol edin."
    )
    st.caption(f"Teknik ayrıntı: {type(hata).__name__}")
    st.stop()


def veri_oku(taze=False):
    if BULUT:
        try:
            ham = sheets_baglantisi().read(worksheet=SAYFA, ttl=0 if taze else 10)
        except Exception as hata:
            sheets_hatasi(hata)
        return em.duzenle(ham)
    if "tablo" not in st.session_state:
        st.session_state.tablo = em.ornek_tablo()
    return st.session_state.tablo


def veri_yaz(df):
    if BULUT:
        try:
            sheets_baglantisi().update(worksheet=SAYFA, data=df)
            st.cache_data.clear()
        except Exception as hata:
            sheets_hatasi(hata)
    else:
        st.session_state.tablo = df


# ---------- Görünüm yardımcıları ----------
def renk_fark(deger):
    if deger < 0:
        return "background-color: #ffcccc; color: #990000; font-weight: bold"
    if deger > 0:
        return "background-color: #ccffcc; color: #006600; font-weight: bold"
    return ""


def tabloyu_goster(df):
    stil = df.style
    uygula = getattr(stil, "map", None) or stil.applymap  # eski pandas sürümleri için
    stil = uygula(renk_fark, subset=["Fark"])
    try:
        st.dataframe(stil, width="stretch", hide_index=True)
    except Exception:  # eski Streamlit sürümleri
        st.dataframe(stil, use_container_width=True, hide_index=True)


# ---------- Sayfa ----------
st.title("📦 Minienvanter")
st.caption("Stok sayımı ile kayıtlı hareketler arasındaki farkı saniyeler içinde bulun.")

if BULUT:
    st.success("☁️ Google Sheets'e bağlı: kayıtlar canlı olarak tabloya yazılır.")
else:
    st.info(
        "🧪 Demo modu: örnek market verisiyle çalışıyor. Kayıtlar yalnızca bu oturumda "
        "tutulur, sayfa yenilenince başa döner."
    )

with st.sidebar:
    st.header("📋 Yeni Hareket Girişi")
    with st.form("hareket_formu", clear_on_submit=True):
        urun = st.text_input("Ürün Adı")
        sol, sag = st.columns(2)
        with sol:
            baslangic = st.number_input("Başlangıç", min_value=0, value=0, step=1)
            gelen = st.number_input("Gelen (+)", min_value=0, value=0, step=1)
            t_gelen = st.number_input("Trf Gelen (+)", min_value=0, value=0, step=1)
        with sag:
            satan = st.number_input("Satan (-)", min_value=0, value=0, step=1)
            t_giden = st.number_input("Trf Giden (-)", min_value=0, value=0, step=1)
            fiziksel = st.number_input("Sayım (Fiziksel)", min_value=0, value=0, step=1)
        ekle = st.form_submit_button("Listeye Ekle")

    if not BULUT:
        st.divider()
        b1, b2 = st.columns(2)
        if b1.button("Örnek veri"):
            st.session_state.tablo = em.ornek_tablo()
            st.rerun()
        if b2.button("Temizle"):
            st.session_state.tablo = em.bos_tablo()
            st.rerun()

if ekle:
    try:
        satir = em.yeni_satir(urun, baslangic, gelen, satan, t_gelen, t_giden, fiziksel)
    except ValueError as hata:
        st.sidebar.warning(str(hata))
    else:
        veri_yaz(em.satir_ekle(veri_oku(taze=True), satir))
        st.toast(f"✅ {satir['Ürün Adı']} listeye eklendi!")

df = veri_oku()

if df.empty:
    st.info("Henüz veri girişi yapılmadı. Soldaki formdan ürün ekleyebilirsiniz.")
else:
    ozet = em.ozet(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Ürün", ozet["toplam_urun"])
    m2.metric("Net Fark", ozet["net_fark"])
    m3.metric("Eksik Çıkan", ozet["eksik"])
    m4.metric("Fazla Çıkan", ozet["fazla"])

    eksikler = em.eksik_urunler(df)
    if eksikler:
        liste = ", ".join(f"{ad} ({fark})" for ad, fark in eksikler[:8])
        st.warning(f"⚠️ Sayımda eksik çıkan ürünler: {liste}")

    st.subheader("📊 Güncel Liste")
    sadece_fark = st.checkbox("Sadece farklı çıkan ürünleri göster")
    tabloyu_goster(df[df["Fark"] != 0] if sadece_fark else df)

    st.download_button(
        label="📥 Listeyi indir (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),  # Excel'de Türkçe karakterler bozulmasın
        file_name="envanter_listesi.csv",
        mime="text/csv",
    )
