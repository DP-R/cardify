# 🎴 Cardify - A4 Transport PDF to Smart Card Converter

**Cardify** is a web application and Python automation suite that extracts vehicle registration details and driving licence data from full-page A4 government PDFs (`a4.pdf` & `dl_a4.pdf`) and converts them into compact, high-DPI smart cards matching standard Indian Transport Department layouts (`card.pdf` & `dl_card.pdf`).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## ✨ Features

- 🚗 **Vehicle RC Card Conversion**: Converts A4 Form 23 Registration Certificates into two-sided RC smart cards.
- 🪪 **Driving Licence (DL) Conversion**: Converts A4 Form 6 Driving Licences into standard DL smart cards.
- ⚡ **Auto-Detection**: Upload any A4 PDF and Cardify automatically identifies whether it's an RC or DL document.
- 📷 **Photo & QR Extraction**: Automatically crops user photos and QR codes from the source document and embeds them seamlessly.
- 🎯 **Pixel-Perfect Alignment**: Preserves official fonts, line spacings, badge colors (NT & AP), vector emblems, and rotated edge text.
- 🌐 **Interactive Web UI**: Modern glassmorphism dark-mode UI with drag & drop upload, real-time PDF page previews, and instant downloads.
- 🛠️ **CLI Utility**: Independent command-line conversion scripts for batch or programmatic processing.

---

## 🚀 Deployment (Free Public Live Link)

### 1. Deploy to Render (Recommended for Permanent 24/7 Hosting)
1. Fork or push this repository to your GitHub account.
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
3. Connect this GitHub repository.
4. Render will automatically detect `render.yaml` and deploy your live web application with a public `https://cardify-xxx.onrender.com` URL!

### 2. Run Locally
```bash
# Clone the repository
git clone https://github.com/DP-R/cardify.git
cd cardify

# Install dependencies
pip install -r requirements.txt

# Start Web Server
python3 app.py
```
Open **`http://localhost:5000`** in your browser.

---

## 🛠️ Standalone CLI Scripts

You can also use the converter scripts independently via command line:

### RC Converter
```bash
python3 rc_converter.py [input_a4.pdf] [output_card.pdf]
```

### DL Converter
```bash
python3 dl_converter.py [input_dl_a4.pdf] [output_dl_card.pdf]
```

---

## 📁 Repository Structure

```
.
├── app.py                   # Flask Web Server & API backend
├── rc_converter.py          # Standalone Vehicle RC PDF Card converter
├── dl_converter.py          # Standalone Driving Licence PDF Card converter
├── templates/
│   └── index.html           # Modern Glassmorphism Web UI
├── requirements.txt         # Python dependencies
├── Procfile                 # Production server process file
├── render.yaml              # Render 1-click cloud deployment config
└── README.md                # Project documentation
```

---

## 📄 License
MIT License. Created with ❤️ for transport document conversion.
