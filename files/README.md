# 📊 Sales Data Analyzer

**Avtomatik tahlil** + **AI chat** bilan satish ma'lumotlarini tahlil qiluvchi Streamlit app.

## ✨ Asosiy xususiyatlar

### 🔍 Avtomatik tahlil (fayl yuklanishi bilan)
- 💰 **Eng ko'p/kam daromad** - avtomatik aniqlanadi
- 📦 **Miqdor statistikasi** - umumiy va o'rtacha
- 📈 **Foyda tahlili** - top va bottom ko'rsatkichlar
- 🏆 **Top 3 performerlar** - kategoriya bo'yicha
- ⚠️ **Past 3 performerlar** - kamchiliklar

### 🤖 AI Chat (Claude Sonnet 4)
- Natural language savollar (o'zbekcha/inglizcha)
- Data haqida batafsil javoblar
- 4 ta tayyor namuna savol

### 📊 Vizualizatsiya
- **Bar chart** - top N kategoriyalar
- **Pie chart** - taqsimot
- **Data table** - qidirish bilan

---

## 🚀 Streamlit Cloud'da Deploy qilish

### 1️⃣ GitHub repository yarating
```bash
git init
git add .
git commit -m "Sales analyzer app"
git remote add origin https://github.com/USERNAME/sales-analyzer.git
git push -u origin main
```

### 2️⃣ Streamlit Cloud'da deploy qiling
1. [share.streamlit.io](https://share.streamlit.io) ga kiring
2. GitHub bilan login qiling
3. **"New app"** → repository, branch, `app.py` tanlang
4. **"Advanced settings" → "Secrets"** ga qo'shing:

```toml
ANTHROPIC_API_KEY = "sk-ant-sizning-api-kalitingiz"
```

5. **"Deploy!"** bosing

### 3️⃣ URL olasiz
```
https://username-sales-analyzer-xxxxx.streamlit.app
```

---

## 🧪 Lokal ishga tushirish

```bash
# Dependencies o'rnatish
pip install -r requirements.txt

# API key sozlash
mkdir .streamlit
echo 'ANTHROPIC_API_KEY = "sk-ant-..."' > .streamlit/secrets.toml

# Ishga tushirish
streamlit run app.py
```

---

## 📁 Fayl tuzilishi

```
sales-analyzer/
├── app.py                  # Asosiy Streamlit app
├── requirements.txt        # Dependencies
├── sample_data.csv         # Test ma'lumotlar
├── .streamlit/
│   └── secrets.toml        # API key (gitignore!)
└── README.md
```

---

## 🔑 Anthropic API Key olish

1. [console.anthropic.com](https://console.anthropic.com) ga kiring
2. **"API Keys"** → **"Create Key"**
3. Kalit nusxasini oling
4. `.streamlit/secrets.toml` ga yozing yoki app ichida kiriting

---

## 📊 Sample data

`sample_data.csv` faylida test uchun ma'lumotlar bor:
- 30 ta buyurtma
- Toshkent, Samarkand, Fergana, Bukhara regionlari
- iPhone, Samsung TV, Nike, Adidas mahsulotlari
- Revenue, quantity, profit ustunlari

---

## 💡 Qanday ishlaydi?

1. **Fayl yuklang** → CSV yoki Excel
2. **Avtomatik tahlil** → darhol 6 ta insight ko'rsatiladi
3. **Grafik ko'ring** → bar, pie chartlar
4. **AI'dan so'rang** → natural language savollar

---

## 🛠️ Texnologiyalar

- Streamlit
- Pandas
- Plotly
- Anthropic Claude API

---

## ⚠️ Eslatma

- API key **maxfiy** saqlansin (secrets.toml'ni gitignore qiling)
- Chat ishlatish uchun API key **majburiy**
- Avtomatik tahlil API keysiz ham ishlaydi
