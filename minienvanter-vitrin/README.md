# 📦 Minienvanter

Market ve küçük işletmelerde **stok sayımı ile kayıtlı hareketler arasındaki farkı** saniyeler içinde bulan, sade bir stok mutabakat paneli.

<!-- CANLI DEMO: Streamlit Community Cloud'a yükledikten sonra aşağıdaki satırı açıp linki yazın.
**🔗 [Canlı demoyu dene](https://SENIN-UYGULAMA-ADIN.streamlit.app)**
-->
<!-- EKRAN GÖRÜNTÜSÜ: docs/ekran.png dosyasını ekledikten sonra aşağıdaki satırı açın.
![Minienvanter ekran görüntüsü](docs/ekran.png)
-->

## Çözdüğü sorun

Birçok işletme sayımı hâlâ defter ya da elle hazırlanmış Excel tablolarıyla yapıyor. Sayım günü "olması gereken" ile "rafta olan" elle karşılaştırılıyor, bu da hem uzun sürüyor hem hata üretiyor.

Minienvanter her ürün için şu formülü otomatik uygular:

```
Beklenen Stok = (Başlangıç + Gelen + Transfer Gelen) - (Satan + Transfer Giden)
Fark          = Fiziksel Sayım - Beklenen Stok
```

Eksik çıkan ürünler kırmızı, fazla çıkanlar yeşil gösterilir; sayımdan hemen sonra nerede kaçak ya da hata olduğu görülür.

## Özellikler

- Ürün bazlı hareket girişi (başlangıç, gelen, satan, transfer, fiziksel sayım)
- Otomatik beklenen stok ve fark hesabı
- Özet göstergeler: toplam ürün, net fark, eksik ve fazla çıkan ürün sayısı
- Eksik çıkan ürünler için uyarı, "sadece farklı olanları göster" filtresi
- CSV dışa aktarma (Excel'de Türkçe karakter sorunu yok)
- **Demo modu:** kurulum gerektirmez, örnek market verisiyle açılır
- **Bulut modu:** kayıtlar Google Sheets'e canlı yazılır, birden fazla kişi aynı tabloyu kullanabilir

## Hızlı başlangıç (demo modu)

```bash
git clone https://github.com/Turkafer/Minienvanter.git
cd Minienvanter
pip install -r requirements.txt
streamlit run app.py
```

Ek ayar yapılmazsa uygulama demo modunda açılır.

## Google Sheets ile kullanım (bulut modu)

1. [Google Cloud Console](https://console.cloud.google.com)'da bir proje oluşturup **Google Sheets API**'yi etkinleştirin.
2. Bir **servis hesabı** oluşturun ve JSON anahtarını indirin.
3. Boş bir Google Sheets tablosu açın, ilk sayfanın adını `Sayfa1` yapın ve tabloyu servis hesabının e-postasıyla **Düzenleyici** olarak paylaşın.
4. `.streamlit/secrets.toml.example` dosyasını `.streamlit/secrets.toml` olarak kopyalayıp bilgileri doldurun.
5. `streamlit run app.py` ile başlatın. Üstte "Google Sheets'e bağlı" mesajını görmelisiniz.

> ⚠️ `secrets.toml` ve JSON anahtar dosyası `.gitignore` ile korunur. Bunları asla GitHub'a yüklemeyin. Streamlit Community Cloud'da aynı içeriği uygulamanın **Settings → Secrets** bölümüne yapıştırın.

## Proje yapısı

| Dosya | Görevi |
| --- | --- |
| `app.py` | Streamlit arayüzü ve veri katmanı (demo / Google Sheets) |
| `envanter_mantik.py` | Hesaplama ve veri düzenleme fonksiyonları (arayüzden bağımsız) |
| `test_envanter.py` | Hesaplama mantığı testleri (`python test_envanter.py`) |
| `.streamlit/secrets.toml.example` | Google Sheets bağlantısı için örnek ayar |

## Kullanılan teknolojiler

Python, Streamlit, pandas, Google Sheets API (`st-gsheets-connection`)

## Geliştirme fikirleri

- Kritik stok seviyesi için e-posta / Telegram bildirimi
- Kullanıcı girişi ve işlem geçmişi
- Barkod ile ürün girişi
