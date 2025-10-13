# Olgahan Kimya ERP — Teknik Analiz ve Taslak

> Bu doküman, Olgahan Kimya ERP için kapsam, mimari, veri modeli, akışlar, yetkilendirme, analizler ve yol haritasını tek bir yerde toplar. Notlar Türkçe ve üretim odaklıdır.

---

## 1) Amaç ve Kapsam (Özet)
- Poşet ve deterjan üretim süreçlerini **sipariş → üretim emri → lot → paketleme → depo → sevkiyat** zincirinde yönetmek.
- Al–sat ürünlerin (Hammadde, Kağıt, EDT, Sarf vb.) satış ve stok takibini kapsamak.
- Fotoğraf, not, tarih ve kullanıcı bazlı **tam izlenebilirlik** (audit/log) sağlamak.
- **Mobil uyumlu**, hızlı ve sade bir arayüz.
- **Renk kodlu termin** görünürlüğü, **fire** takibi ve **performans analitiği**.

## 2) Varsayımlar (İş Kuralları için Başlangıç)
- Para birimi: **TRY (₺)**, KDV ve indirim/bindirim desteklenir.
- Tarih/format: **DD.MM.YYYY**, saat **24h**.
- Stok değerleme: varsayılan **FIFO** (FEFO seçeneği hammadde SKT’li ise).
- Barkod/QR: **Lot**, **Paket** ve **Sevkiyat Paleti** için (Code128/QR) oluşturulur.
- Resimler: sunucuda **otomatik sıkıştırma** (ör. 1600px * uzun kenar, WEBP/JPEG), EXIF temizleme.
- Dosya boyut limiti: 10–20 MB/resim (yapılandırılabilir).
- Kimlik doğrulama: **rol tabanlı**, oturum süre aşımı 2 saat.
- **Fire eşikleri**: **admin tarafından** ürün tipine göre belirlenir. **Varsayılan** (değiştirilebilir):
  - Poşet: Seviye1 %3 veya 15kg, Seviye2 %6 veya 30kg
  - Deterjan: Seviye1 %2 veya 10kg, Seviye2 %4 veya 20kg
- Veritabanı: **PostgreSQL** (JSONB, GIN indeksler); migrasyon **Alembic**.
- Dosya/Resim depolama: **S3 uyumlu** (MinIO) veya yerel depolama (MVP'de yerel, prod’da MinIO).
- Arka plan işler: **Celery** (broker: Redis veya RabbitMQ), izleme: **Flower**.

## 3) Roller ve Yetkiler (RBAC Matrisi)
| İşlem/Modül | Admin | Yönetici | Üretim Operatörü | Paketleme | Depocu | Sevkiyat | Plasiyer |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Kullanıcı/Rol Yönetimi | ✓ | – | – | – | – | – | – |
| Sipariş Oluştur/Güncelle | ✓ | ✓ | – | – | – | – | ✓ (kendi) |
| Üretim Emri Oluştur | ✓ | ✓ | – | – | – | – | – |
| Operatör Atama/Öncelik | ✓ | ✓ | – | – | – | – | – |
| Üretim Başlat/Bitir | – | – | ✓ | – | – | – | – |
| Fire/Not/Resim Ekle (Üretim) | – | – | ✓ | – | – | – | – |
| Paketleme Girişi | – | – | – | ✓ | – | – | – |
| Depo Kabul/Onay | – | – | – | – | ✓ | – | – |
| Sevkiyat Planlama/Teslim | – | – | – | – | – | ✓ | – |
| Raporlar/Analitik | ✓ | ✓ | kısıtlı | kısıtlı | ✓ | ✓ | kendi |

> Not: Admin’in termin minimumu altına inememe kuralını sistem genelinde doğrulayan bir validasyon bulunur.

## 4) Durum Makineleri (State Machines)
**4.1 Sipariş**: `Taslak → Onaylı → Üretim_Emri_Verildi → Üretimde → Paketlemede → Depoda → Sevkiyata_Hazır → Sevkiyat_Planlandı → Teslim_Edildi → Kapatıldı`

**4.2 Lot**: `Oluşturuldu → Üretimde → Üretim_Bitti → Paketlemede → Depoda → Sevkiyata_Hazır`

**4.3 Paket**: `Oluşturuldu → Depo_Kabul_Bekliyor → Depoya_Alındı → Sevkiyata_Hazır`

**4.4 Sevkiyat**: `Planlandı → Yüklendi → Teslimde → Teslim_Edildi`

Her geçiş, **kullanıcı-id**, **tarih/saat**, **IP**, **yorum**, **opsiyonel fotoğraf** ile loglanır.

## 5) Termin Renk Kodlaması (Sipariş Listesi)
- 🔴 **< 7 gün** kala
- 🟠 **8–15** gün kala
- 🟡 **16–30** gün kala
- 🔵 **Teslim edilmek üzere hazır** (durum bazlı)
- 🟢 **Teslim edildi** (durum bazlı)

> “kala” hesaplaması: `termin_tarihi - bugün` (takvim günü). Teslim/Gönderim durumları renk önceliğini ezebilir (örn. Teslim edildi ise 🟢 göster).

## 6) Fire Yönetimi
- **Seviye 1 Uyarı**: Lot veya sipariş bazlı fire %/kg **eşik1** üzeri → Admin ve Yönetici bildirim.
- **Seviye 2 Uyarı**: **eşik2** üzeri → kırmızı uyarı ve üst düzey raporlama.
- Eşikler ürün tipine göre yapılandırılabilir (Poşet, Deterjan, Al–sat).
- Fire kaydı: **kg**, **neden** (liste+serbest metin), **fotoğraf**, **kullanıcı**, **timestamp**.

## 7) Ürün Tipine Göre Hesaplamalar
**7.1 Poşet Üretimi**
- Girdi: Hammadde(ler) + **formül** + hedef ürün miktarı
- Fire dahil hedef üretim: `teorik_çıktı = (toplam_hammadde * verim)`, `fiili_çıktı = teorik_çıktı - fire`
- Alternatif formül: hedef ürün miktarı `Q` ise gereken hammadde: `Q / verim` (fire payı dahil edilir).

**7.2 Deterjan Üretimi**
- Girdi: **formül** (yüzdeler), başlangıç stok çekimi
- **Kalması gereken miktar**: formül ve batch büyüklüğüne göre teorik değerler → tartım sonrası **kalan = teorik - fiili tüketim**.
- Haftalık tartımda **teorik vs gerçek** karşılaştırılır, sapmalar istatistiklenir.

> Formüller versiyonlanır (valid_from/valid_to). Üretim emrine uygulandığında **snapshot** alınır.

## 8) Haftalık Tartım & Performans Analitiği
- Operatör/Paketleme için metrikler: **toplam üretim**, **fire kg/%**, **lot başına ortalama çevrim süresi**, **elek değişim sayısı**, **arıza bildirimi** sayısı ve **çözüm süresi**.
- **Kişi bazlı sıralama**: bölüme göre en düşük fire ve hedef/termin uyumu.
- **Z-skoru / IQR** ile aykırı değer tespiti; **trend** (7/30 gün) takibi.
- Haftalık tartım tablosu: kalması gereken (teorik) vs ölçülen; **%sapma** ve renkli vurgular.

## 9) İzlenebilirlik, Lot ve Etiketleme
- **Lot No**: `YYYYMMDD-ÜRÜN-Kısaltma-Sıra` (yapılandırılabilir).
- Her lot için **QR/Code128** etiketi (ürün, tarih, vardiya, operatör, formül versiyonu).
- Paket etiketi: **lot + paket sıra + kg/adet**.
- Sevkiyat paleti: **palet no + toplam m³/kg + sipariş referansları**.

## 10) Depo ve Stok
- **Çoklu depo** ve opsiyonel **raf/slot** desteği (MVP’de çoklu depo zorunlu, raf/slot opsiyonel).
- **Depo hareketleri**: giriş/çıkış, lot bazlı; **sayım** ve **uyumsuzluk** kayıtları.
- **Rezervasyon**: Üretim emri için hammadde rezervasyonu.
- **Al–sat**: Satın alma/satış entegrasyonu; stok seviyeleri ve fiyatlandırma.

## 11) Bildirimler
- Web push + e-posta (opsiyonel SMS/WhatsApp entegrasyonu).
- Tetikler: Fire seviye 1/2, arıza, termin kritik, sevkiyat gecikmesi, düşük stok.

## 12) Ekranlar (Mobil Öncelikli Taslak)
1. **Giriş & Rol seçim / yönlendirme**
2. **Sipariş Listesi** (renk kodlu, hızlı filtreler)
3. **Sipariş Detayı** (notlar, plasiyer düzenlemeleri, değişiklik log)
4. **Üretim Emirleri** (öncelik, atama, durum)
5. **Operatör Paneli** (başlat/bitir, hammadde seç, lot aç, fire/elek/arıza/nota fotoğraf)
6. **Paketleme Paneli** (bitmiş lotlar, paket tipi/adet/koli/rulo, fire, foto)
7. **Depo Kabul** (kg/tarih/saat onayı, fotoğraf, sevkiyata hazır işaretle)
8. **Sevkiyat Planlama** (m³ optimizasyon, araç kapasitesi, yükleme sırası)
9. **Teslim & Kanıt** (teslim fotoğrafı, e-imza opsiyonel)
10. **Raporlar/Analitik** (fire, performans, termin uyumu, plasiyer harita)
11. **Ayarlar** (minimum termin, fire eşikleri, formül versiyonları)

## 13) Veri Modeli (Çekirdek Tablolar)
- **users** (id, ad, rol, aktif, şifre_hash, …)
- **roles** (id, ad, izinler_json)
- **orders** (id, müşteri_id, plasiyer_id, durum, termin_tarihi, not, indirim/bindirim, karlılık, yakıt_gideri, …)
- **order_items** (id, order_id, ürün_id, miktar, birim, fiyat, teslim_durumu, …)
- **production_jobs** (id, order_item_id, öncelik, atanan_operatör, durum, formül_snapshot_json, …)
- **lots** (id, production_job_id, lot_no, durum, vardiya, …)
- **lot_logs** (id, lot_id, olay_tipi, kullanıcı_id, açıklama, foto_ref, tarih_saat, meta_json)
- **defects_waste** (id, bağlam_türü[lot/paket/order], bağlam_id, kg, neden_kodu, açıklama, seviye, foto_ref, kullanıcı_id, ts)
- **packaging** (id, lot_id, tip, adet, koli, rulo, fire_kg, foto_ref, durum)
- **warehouse_receipts** (id, paket_id, kg, tarih, saat, onaylayan, foto_ref, durum)
- **shipments** (id, durum, planlanan_tarih, araç_kapasite_m3, rota_json)
- **shipment_items** (id, shipment_id, paket_id, sıra, m3)
- **inventory** (id, ürün_id, lot_id?, depo_id, miktar, birim, hareket_türü, ts)
- **products** (id, ad, tip[poşet/deterjan/al-sat], birim, verim, etiket_şablon, …)
- **formulas** (id, ürün_id, versiyon, satırlar_json[%/kg], valid_from, valid_to)
- **weekly_weighings** (id, kullanıcı_id/bölüm, hafta, teorik_json, gerçek_json, hesaplanan_sapmalar)
- **attachments** (id, ref_türü, ref_id, dosya_yolu, mime, boyut, şema_versiyon)
- **audit_logs** (id, kullanıcı_id, modül, işlem, eski_yeni_json, ts, ip)

> Not: JSON kolonları PostgreSQL JSONB ile etkin indekslenebilir. SQLite başlangıç aşamasında yeterli olabilir; büyümede PostgreSQL’e geçiş önerilir.

## 14) API Taslağı (REST ilk etap, GraphQL opsiyonel)
- `POST /auth/login`
- `GET /orders?status=&termin<=&query=`
- `POST /orders` `PATCH /orders/{id}`
- `POST /orders/{id}/items` `PATCH /order-items/{id}`
- `POST /production-jobs` `PATCH /production-jobs/{id}`
- `POST /lots` `PATCH /lots/{id}` `GET /lots/{id}/logs`
- `POST /lots/{id}/waste` (fire)
- `POST /packaging` `PATCH /packaging/{id}`
- `POST /warehouse/receipts` `PATCH /warehouse/receipts/{id}`
- `POST /shipments` `PATCH /shipments/{id}` `POST /shipments/{id}/items`
- `GET /analytics/fire` `GET /analytics/performance` `GET /analytics/termin`
- `POST /attachments/upload` (çok parçalı), `GET /attachments/{id}` (izin kontrolü)

**Kimlik ve Yetki:** JWT + rol/izin middleware; her endpoint için izin kontrolü.

## 15) Raporlar & KPI’lar
- **Fire**: ürün tipine göre **kg**, **%**, **trend** (7/30/90g), **seviye dağılımı**.
- **Performans**: kişi/bölüm bazlı **OEE-benzeri** metrik seti (çevrim, fire, duruş) — sadeleştirilmiş.
- **Termin Uyumu**: zamanında teslim yüzdesi, dağılım, kritik sipariş listesi.
- **Sevkiyat**: üretim/sevkiyat oranı, bekleyen m³/kg.
- **Plasiyer Harita**: siparişleri **TL ağırlıklı baloncuk**larla gösteren ısı haritası.

## 16) Arıza & Elek Değişimi
- Operatör ekranında tek dokunuşla olay kaydı (kategori + not + fotoğraf).
- MTTR/MTBF benzeri basit göstergeler (duruş süreleri istenirse eklenebilir).

## 17) Güvenlik, Performans, Bakım
- Dosya yüklemelerinde **virüs taraması** (opsiyonel, kuyruklu işlem).
- Resim sıkıştırma için arka plan işçisi (RQ/Celery/Arq) — UI’da anlık durum gerekmez.
- Loglar için **immütabl** arşiv (append-only), 1 yıl çevrimiçi, 3 yıl arşiv önerisi.
- Yedekleme: günlük DB dump, haftalık tam, saklama 30–90 gün.

## 18) Sevkiyat m³ Optimizasyonu (Basit Heuristik)
- **Placeholder**: MVP’de yalnızca planlanan tarih alanı ve basit listeleme/filtreleme olacak. m³ optimizasyonu Faz 2’ye alınmıştır.

## 19) Yol Haritası (Aşama Aşama)
**Faz 1 (MVP)**
- RBAC, sipariş → üretim emri → lot → paketleme → depo kabul → sevkiyat hazır akışları
- Fotoğraf yükleme ve loglama, temel fire uyarıları (S1)
- Termin renk kodlu liste, temel raporlar
- **Çoklu depo** desteği
- **Admin ayarlı fire eşikleri** konfig ekranı

**Faz 2**
- Sevkiyat planlama ve m³ optimizasyonu, teslim kanıtı
- Haftalık tartım modülü ve performans panosu
- Fire uyarıları (S2) + yapılandırılabilir eşikler

**Faz 3**
- Harita & plasiyer analitiği, rota planlama
- ERP dışı entegrasyonlar (e‑Fatura/e‑İrsaliye, muhasebe, SMS)
- FEFO, ileri stok sayım fark analizleri

---

## 21) MVP — Net Kapsam ve Teknik Yığın
**Teknik Yığın**
- Backend: **Python + FastAPI**, ORM: **SQLAlchemy**, şema/migrasyon: **Alembic**, doğrulama: **Pydantic**
- Frontend: **Vue 3 + Vite + Pinia + Vue Router** (UI: **Vuetify** önerilir)
- DB: **PostgreSQL**
- Kuyruk/Arka Plan: **Celery + Flower** (broker: Redis/RabbitMQ, backend: Redis/Postgres)
- Depolama: **Yerel disk (MVP)** → **MinIO/S3 (prod)**
- Kimlik Doğrulama: **JWT (access/refresh)** + rol/izin middleware
- Günlükleme: **structured logging** (uvicorn log + app log), **audit_logs** tablosu

**MVP Ekranları**
1) Giriş / Şifre reset
2) Sipariş Listesi & Detayı (termin renk kodlu)
3) Üretim Emirleri (öncelik/atama)
4) Operatör Paneli (lot aç/kapat, fire/elek/arıza + foto)
5) Paketleme Paneli
6) Depo Kabul (çoklu depo seçimi)
7) Basit Sevkiyat (yalnızca “Sevkiyata Hazır” listesi + planlanan tarih)
8) Admin → Ayarlar: **Fire Eşiği** (ürün tipine göre), Termin minimumu, Depo tanımları
9) Raporlar: Fire (S1), Temel termin uyumu, Üretim/sevkiyat oranı (basit)

**MVP API’leri (özet)**
- Auth: `/auth/login`, `/auth/refresh`, `/auth/me`
- Ayarlar: `/settings/fire-thresholds`, `/settings/termin`, `/settings/warehouses`
- Sipariş: `/orders`, `/orders/{id}`, `/orders/{id}/items`
- Üretim: `/production-jobs`, `/lots`, `/lots/{id}/waste`, `/lots/{id}/logs`
- Paketleme: `/packaging`
- Depo: `/warehouses/receipts`
- Sevkiyat (placeholder): `/shipments` (planlanan_tarih alanı ile)
- Raporlar: `/analytics/fire`, `/analytics/termin`, `/analytics/ratio`
- Dosya: `/attachments/upload`, `/attachments/{id}`

**Veri Modeli (MVP çekirdek)**
- users, roles, audit_logs
- products (tip: poset/deterjan/al-sat)
- orders, order_items
- production_jobs, lots, lot_logs, defects_waste
- packaging, warehouse_receipts, warehouses (çoklu depo), inventory
- shipments (minimal alanlarla)
- settings (JSONB; fire eşikleri, termin minimumu, depo varsayılanı)
- attachments

**Arka Plan İşleri (Celery)**
- Resim sıkıştırma/thumbnail
- Fire uyarı tetikleyicileri (S1)
- Günlük kritik termin taraması (cron)

**DevOps**
- Docker Compose (web, worker, broker, db, storage, flower)
- CI: lint + test + alembic migration check
- Seed komutları: admin kullanıcı, varsayılan fire eşikleri, depo örnekleri

**Test Planı**
- Birim: formül/renk kodu/fire eşiği hesapları
- Entegrasyon: siparişten depoya akış
- E2E (Cypress): Operatör→Paketleme→Depo mutlu polka

---

## 22) Konfigürasyon Ekranı — Örnek Şema
```yaml
settings:
  fire_thresholds:
    poset: { level1_percent: 3, level1_kg: 15, level2_percent: 6, level2_kg: 30 }
    deterjan: { level1_percent: 2, level1_kg: 10, level2_percent: 4, level2_kg: 20 }
  termin:
    minimum_days: 7
  warehouses:
    - code: MERKEZ
      name: Merkez Depo
    - code: YAN
      name: Yan Depo
```

## 23) Sevkiyat — Placeholder Notu
- MVP’de yalnızca planlanan sevkiyat tarihi, ürün/hazır listeleri ve durum geçişleri olacak.
- Araç m³ optimizasyonu ve rota planlama Faz 2’ye taşındı.

