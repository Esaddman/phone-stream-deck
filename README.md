turkish:# 🎛️ Mini Stream Deck (Telefonu Stream Deck Yapma)

Bilgisayarınızdaki uygulamaları, web sitelerini, klavye kısayollarını ve medya/ses kontrollerini **telefonunuzun tarayıcısı üzerinden** tek dokunuşla yönetmenizi sağlayan hafif ve kurulumsuz bir Python aracıdır.

---

## ✨ Özellikler
* **Sıfır Ek Kütüphane:** Sadece Python kurulu olması yeterlidir; `pip install` gerektirmez.
* **Tam Özelleştirilebilir Butonlar:** Telefon ekranından yeni buton ekleyebilir, rengini, emojisini, adını ve görevini değiştirebilirsiniz.
* **4 Farklı Görev Türü:**
  * **Uygulama / Dosya:** Chrome, Spotify, Discord, Steam veya herhangi bir `.exe` dosyasını açar.
  * **Web Sitesi:** İstediğiniz linki doğrudan tarayıcıda açar.
  * **Tuş Kısayolu:** `ctrl+c`, `win+d`, `alt+tab` gibi klavye kombinasyonlarını tetikler *(Windows)*.
  * **Medya & Ses:** Oynat/Durdur, Sonraki, Önceki, Ses Artır/Azalt ve Sessize Al komutlarını çalıştırır *(Windows)*.
* **Kırık Ekran Dostu Mod (Ekran Alanı Ayarı):** Telefonunuzun dokunmatiğinin sadece belirli bir bölgesi (üst, alt, sağ, sol) çalışıyorsa, arayüzü sadece çalışan alana sığdırabilirsiniz.
* **Güvenli Bağlantı:** Her kurulumda otomatik oluşan özel güvenlik anahtarı (`?k=...`) sayesinde ağınızdaki başkaları panelinize erişemez.

---

## 🚀 Nasıl Kurulur ve Çalıştırılır?

### 1. Gereksinimler
* Bilgisayarınızda **Python 3** kurulu olmalıdır. *(Kurulu değilse [python.org](https://python.org) adresinden indirebilirsiniz. Kurulumda **"Add Python to PATH"** kutucuğunu işaretlemeyi unutmayın.)*
* Bilgisayarınız ve telefonunuz **aynı Wi-Fi ağına** bağlı olmalıdır.

### 2. Başlatma
1. Bu depodaki `minideck.py` dosyasını bilgisayarınıza indirin.
2. Dosyaya çift tıklayın (veya terminal/CMD üzerinden `python minideck.py` komutunu çalıştırın).
3. Açılan siyah pencerede size özel üretilen adresi göreceksiniz:
   ```text
   http://1.xx
   ```
4. Telefonunuzun tarayıcısını (Chrome, Safari vb.) açın ve ekranda yazan bu adresi **sonundaki `?k=...` kısmı dahil** eksiksiz yazın.

> **💡 İpucu:** Windows Güvenlik Duvarı uyarı verirse **"Özel ağlar" (Private networks)** seçeneğine izin verin.

---

## 📱 Arayüz Kullanımı
* **➕ (Ekle):** Yeni bir uygulama, site, kısayol veya medya butonu oluşturur.
* **✏️ (Düzenle):** Mevcut butonların sırasını değiştirmenizi, düzenlemenizi veya silmenizi sağlar.
* **⚙️ (Ekran Alanı):** Panelin telefon ekranının neresinde (Alt, Üst, Sol, Sağ, Tam Ekran) ve yüzde kaç boyutunda görüneceğini ayarlar.
* **⛶ (Tam Ekran):** Tarayıcı çubuklarını gizleyerek tam ekran deneyimi sunar.

---

## ⚠️ Bilinen Notlar
* Yaptığınız buton ayarları otomatik olarak kodun bulunduğu klasörde `deck_ayar.json` dosyasına kaydedilir.
* Klavye kısayolları ve medya tuşları şu an için yalnızca **Windows** işletim sisteminde çalışmaktadır. Uygulama ve link açma özellikleri Windows, macOS ve Linux'ta çalışır.





English:# 🎛️ Mini Stream Deck (Turn Your Phone into a Stream Deck)

A lightweight, zero-dependency Python tool that lets you launch apps, open websites, trigger keyboard shortcuts, and control media/volume on your PC directly from your **phone's web browser** with a single tap.

---

## ✨ Features
* **Zero External Libraries:** Requires only standard Python; no `pip install` needed.
* **Fully Customizable Buttons:** Add new buttons, customize colors, emojis, labels, and actions directly from your phone.
* **4 Action Types:**
  * **App / File:** Launches Chrome, Spotify, Discord, Steam, or any custom `.exe` path.
  * **Website:** Opens any URL directly in your default browser.
  * **Keyboard Shortcuts:** Triggers key combinations like `ctrl+c`, `win+d`, or `alt+tab` *(Windows)*.
  * **Media & Volume:** Controls Play/Pause, Next, Previous, Volume Up/Down, and Mute *(Windows)*.
* **Broken-Screen Friendly Mode (Screen Area Settings):** If only a specific part of your phone's touchscreen works (top, bottom, left, or right), you can resize and dock the deck to fit only the working area.
* **Secure Local Access:** Automatically generates a unique security token (`?k=...`) on first run so unauthorized devices on your network cannot access your controls.

---

## 🚀 Setup & Usage

### 1. Requirements
* **Python 3** installed on your PC. *(Download from [python.org](https://python.org) if needed—make sure to check **"Add Python to PATH"** during installation.)*
* Both your PC and phone must be connected to the **same Wi-Fi network**.

### 2. How to Run
1. Download `minideck.py` from this repository.
2. Double-click the file (or run `python minideck.py` in your terminal/CMD).
3. A console window will display your unique local address:
   ```text
   http://1.xx
   ```
4. Open your phone's browser (Chrome, Safari, etc.) and enter the exact URL shown on your PC, **including the `?k=...` token at the end**.

> **💡 Tip:** If Windows Firewall prompts you, allow access on **"Private networks"**.

---

## 📱 Interface Controls
* **➕ (Add):** Create a new app, link, shortcut, or media button.
* **✏️ (Edit):** Reorder, modify, or delete existing buttons.
* **⚙️ (Screen Area):** Adjust where the deck appears on your screen (Top, Bottom, Left, Right, Full) and set its size percentage.
* **⛶ (Fullscreen):** Hides the browser address bar for a clean fullscreen experience.

---

## ⚠️ Notes
* All custom button layouts are automatically saved to `deck_ayar.json` in the same folder as the script.
* Keyboard shortcuts and media keys are currently supported on **Windows** only. App and website launching work across Windows, macOS, and Linux.
