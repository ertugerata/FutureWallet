import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- 1. AYARLAR ---
SYMBOL = "BTC-USD"
HEDEF_FIYAT = 100000   # Hedeflenen Fiyat ($)
VADE_GUN = 10          # Kaç gün içinde?

# --- 2. VERİ ÇEKME ---
print(f"{SYMBOL} verileri (Tüm Zamanlar) indiriliyor...")
# ATH'yi doğru bulmak için 'max' (tüm zamanlar) periyodunu çekiyoruz
df = yf.download(SYMBOL, period="max", interval="1d", progress=False)

if df.empty:
    raise ValueError("Veri çekilemedi.")

# En güncel kapanış ve Tarihi Zirve (ATH)
guncel_fiyat = float(df['Close'].iloc[-1])
tarihi_zirve = float(df['High'].max())

print("-" * 30)
print(f"Güncel Fiyat: ${guncel_fiyat:,.2f}")
print(f"Tarihi Zirve (ATH): ${tarihi_zirve:,.2f}") # İşte aradığınız cevap burada çıkacak

# Hedef Durumu
if HEDEF_FIYAT > tarihi_zirve:
    print(f"DURUM: Hedef ({HEDEF_FIYAT}), tarihi zirvenin üzerinde. (Yeni Rekor Denemesi)")
else:
    print(f"DURUM: Hedef ({HEDEF_FIYAT}), tarihi zirvenin altında. (Toparlanma Hareketi)")

# Gereken yükseliş oranı
if HEDEF_FIYAT <= guncel_fiyat:
    gereken_artis_orani = 0
    print("UYARI: Fiyat zaten hedefin üzerinde!")
else:
    gereken_artis_orani = (HEDEF_FIYAT - guncel_fiyat) / guncel_fiyat
    print(f"Gereken Yükseliş: %{gereken_artis_orani*100:.2f}")
print("-" * 30)

# --- 3. ÖZELLİK MÜHENDİSLİĞİ (Gelişmiş) ---
# Temel değişimler
df['Getiri'] = df['Close'].pct_change()
df['Volatilite'] = df['Getiri'].rolling(window=7).std()

# YENİ: Drawdown (Zirveden Uzaklık)
# Fiyatın o ana kadarki en yüksek tepesinden ne kadar aşağıda olduğu
# Bu, 'düşüşten dönüş' ihtimallerini yakalamak için çok kritiktir.
df['Running_Max'] = df['High'].cummax()
df['Drawdown'] = (df['Close'] / df['Running_Max']) - 1

# YENİ: Hedefe Uzaklık (Target Proximity)
# Fiyatın hedefe ne kadar yakın olduğu psikolojik bir faktördür
df['Hedefe_Yakinlik'] = (HEDEF_FIYAT - df['Close']) / df['Close']

# Ortalamalar ve Momentum
df['SMA_20'] = df['Close'].rolling(window=20).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['Trend_Gucu'] = (df['SMA_20'] - df['SMA_50']) / df['SMA_50']

# --- 4. ETİKETLEME (TARGET) ---
# Gelecek VADE_GUN içindeki en yüksek fiyat hedefe değdi mi?
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=VADE_GUN)
df['Gelecek_Max'] = df['High'].rolling(window=indexer).max()

# Mantık: Gelecekteki En Yüksek Fiyat >= (Şu anki Fiyat + Gereken Artış)
# Not: Yüzdesel mantığı koruyoruz çünkü fiyat 20k iken %5 artış ile 100k iken %5 artış benzer dinamiktir.
df['Target'] = (df['Gelecek_Max'] >= df['Close'] * (1 + gereken_artis_orani)).astype(int)

# NaN temizliği
df.dropna(inplace=True)

# --- 5. MODEL EĞİTİMİ ---
features = ['Getiri', 'Volatilite', 'Drawdown', 'Trend_Gucu', 'Hedefe_Yakinlik']
X = df[features]
y = df['Target']

# Son 200 günü test için ayıralım (Kripto'da son dönem trendleri önemlidir)
test_size = 200
X_train = X.iloc[:-test_size]
y_train = y.iloc[:-test_size]
X_test = X.iloc[-test_size:]
y_test = y.iloc[-test_size:]

model = XGBClassifier(n_estimators=200, learning_rate=0.02, max_depth=5, eval_metric='logloss')
model.fit(X_train, y_train)

# --- 6. SONUÇ ---
# Modelin son dönem başarısı
acc = accuracy_score(y_test, model.predict(X_test))
print(f"Modelin Son 200 Gündeki Doğruluk Oranı: %{acc*100:.2f}")

# Tahmin
son_veri = X.iloc[[-1]]
olasilik = model.predict_proba(son_veri)[0][1]

print(f"\n>>> TAHMİN SONUCU <<<")
print(f"Süre: {VADE_GUN} Gün")
print(f"Hedef: ${HEDEF_FIYAT:,.0f}")
print(f"Gerçekleşme İhtimali: %{olasilik * 100:.2f}")

# Hangi veri daha etkili oldu?
print("\nEtkili Faktörler:")
imps = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print(imps.head(3))
