# 🏛️ Türkmen Döwlet Maliýe Instituty (TDMai) Web Portal

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.0%20%7C%206.0-green?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JS](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

Türkmen döwlet maliýe institutynyň resmi web portaly. Bu taslama, ýokary okuw mekdebiniň talyplary, dalaşgärleri, mugallymlary we halkara hyzmatdaşlary üçin döwrebap, interaktiw we köp dilli maglumat platformasyny üpjün edýär.

---

## ✨ Özellikler (Features)

*   **🌐 Köp Dilli Goldaw (i18n):** Türkmen (TM), Iňlis (EN) we Rus (RU) dillerinde doly dinamik terjime ulgamy.
*   **📂 Dinamik Sahypalar we Menüler:** Dolandyryş panelinden doly dolandyrylýan köp derejeli (Top -> Sub -> Sub-Sub) dinamik menü we sahypa gurluşy.
*   **🎠 Döwrebap Banner (Slider):** Esasy sahypada awtomatiki (4 sekuntdan bir) we akjy (sagdan çepe) süýşýän dinamik banner.
*   **📰 Täzelikler Bölümi:** Okyjylaryň sanyny (views count) we çap edilen senesini yzarlaýan habarlar ulgamy.
*   **🏛️ Fakultetler we Kafedralar:** Ýokary okuw mekdebiniň gurluş düzümini (fakultetleri we olara degişli kafedralary) görkezýän maglumatlar binýady.
*   **🏆 Olimpiadalar Ulgamy:** Ýyllar boýunça geçirilen ylmy we ders olimpiadalarynyň netijelerini (PDF hasabatlary) ýüklemek we paýlaşmak ulgamy.
*   **🤝 Halkara Hyzmatdaşlyk:** Institutyň halkara hyzmatdaşlary, saparlar, daşary ýurt okuwlary we CirculEC taslamalary baradaky maglumatlaryň ýöriteleşdirilen bölümleri.
*   **📄 Hepdelik Hasabatlar:** Resmi hasabatlary we resminamalary PDF görnüşinde ýüklemek we talyplara elýeterli etmek bölümi.
*   **📱 Mobil Ulaşymlylyk (Responsive):** Planşetler we akylly telefonlar üçin doly optimizirlenen interfeýs.

---

## 🛠️ Kullanılan Teknolojiler (Tech Stack)

### Backend
*   **Python** - Esasy programma dili.
*   **Django** - Güýçli, ygtybarly we çalt işçi gurşaw (Web Framework).
*   **SQLite** - Gurluşly maglumatlar binýady (Ösüş gurşawy üçin).

### Frontend
*   **Vanilla HTML5 & CSS3** - Ösen grid, flexbox we premium wizual dizaýn ulgamy.
*   **Vanilla JavaScript (ES6+)** - Sliderler, mobil menü dolandyryşlary we animatsiyalar üçin.
*   **FontAwesome 6.4.0** - Döwrebap ikonkalar toplumy.

---

## ⚙️ Kurulum ve Çalıştırma (Installation & Setup)

Yerel bilgisayarınızda projeyi ayağa kaldırmak için aşağıdaki adımları sırasıyla takip edin:

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/bagtyyarmiriyew35-maker/Maliya_institut.git
cd Maliya_institut
```

### 2. Sanal Ortam Oluşturun ve Aktifleştirin
**Windows (PowerShell/CMD):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin
```bash
pip install django Pillow
```

### 4. Veritabanı Geçişlerini Uygulayın (Migrations)
```bash
python manage.py migrate
```

### 5. Yönetici (Superuser) Hesabı Oluşturun
Yönetici paneline (`/admin/`) giriş yapmak için bir superuser oluşturun:
```bash
python manage.py createsuperuser
```

### 6. Projeyi Çalıştırın
```bash
python manage.py runserver
```
Artık tarayıcınızdan `http://127.0.0.1:8000/` adresine giderek siteyi görüntüleyebilirsiniz.

---

## 🔒 Çevre Değişkenleri (Environment Variables)

Projenin canlı ortamda (Production) çalıştırılması sırasında güvenlik için `.env` dosyası kullanılmalıdır. Gerekli değişkenler şunlardır:

```env
# .env dosyası içeriği (Örnek)
DEBUG=False
SECRET_KEY=django-insecure-your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost,yourdomain.com
DB_NAME=db.sqlite3
```

> **Önemli:** `.gitignore` dosyası `.env` dosyasını ve yerel veritabanı dosyası olan `db.sqlite3`'ü GitHub'a yüklemeyi otomatik olarak engeller. Bu sayede hassas şifreleriniz ve yerel test verileriniz güvende kalır.
