from googleapiclient.discovery import build
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import re

# ===============================
# 1. SET API KEY & VIDEO ID
# ===============================
API_KEY = "AIzaSyBNbv7e71WZieftC2VqGD9L5XwKKLIkjHw"
VIDEO_ID = "DzwkcbTQ7ZE"  

youtube = build('youtube', 'v3', developerKey=API_KEY)

# ===============================
# 2. AMBIL KOMENTAR
# ===============================
def get_comments(video_id):
    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )

    response = request.execute()

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments

print("Mengambil komentar...")
comments = get_comments(VIDEO_ID)

df = pd.DataFrame({"comment": comments})

# ===============================
# 3. CLEANING TEXT
# ===============================
def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower()

df['clean_comment'] = df['comment'].apply(clean_text)

# ===============================
# 4. SENTIMENT ANALYSIS
# ===============================
kata_positif = [
    "bagus","keren","mantap","hebat","sukses","semangat",
    "lanjutkan","tulus","sehat","aamiin","bermanfaat",
    "lindungi","maju","setuju","bangga","terbaik"
]

kata_negatif = [
    "jelek","buruk","gagal","parah","benci","nyesal",
    "pengkhianat","goblok","bodoh","bacot","mundur",
    "terburuk","pikunn","anjing","dzalim","tipu",
    "korupsi","memalukan","payah"
]

def classify_sentiment(text):
    score = 0

    for word in kata_positif:
        if word in text:
            score += 1

    for word in kata_negatif:
        if word in text:
            score -= 1

    if score > 0:
        return "Positive", score
    elif score < 0:
        return "Negative", score
    else:
        return "Neutral", 0

df[['sentiment', 'score']] = df['clean_comment'].apply(
    lambda x: pd.Series(classify_sentiment(x))
)

# ===============================
# 5. STATISTIK
# ===============================
mean_score = df['score'].mean()
median_score = df['score'].median()
std_score = df['score'].std()

print("\n=== STATISTIK SENTIMEN ===")
print("Mean:", round(mean_score,3))
print("Median:", median_score)
print("Standard Deviation:", round(std_score,3))

# ===============================
# 6. JUMLAH & PERSENTASE
# ===============================
sentiment_counts = df['sentiment'].value_counts()
sentiment_percentage = df['sentiment'].value_counts(normalize=True) * 100

print("\n=== JUMLAH SENTIMEN ===")
print(sentiment_counts)

print("\n=== PERSENTASE SENTIMEN ===")
print(round(sentiment_percentage,2))

# ===============================
# 7. FREKUENSI KATA
# ===============================
stopwords = [
    "dan","di","yang","untuk","dari","ini","itu","ke",
    "dengan","pada","kita","pak","nya","atau","ada"
]

all_words = " ".join(df['clean_comment']).split()
filtered_words = [word for word in all_words if word not in stopwords]

word_counts = Counter(filtered_words)
top_words = word_counts.most_common(10)

print("\nTop 10 Kata:")
for word, count in top_words:
    print(word, ":", count)

# ===============================
# 8. AUTO INSIGHT (INI YANG KEREN 🔥)
# ===============================
def generate_insight(df, top_words):
    pos = (df['sentiment'] == 'Positive').sum()
    neg = (df['sentiment'] == 'Negative').sum()
    neu = (df['sentiment'] == 'Neutral').sum()

    print("\n=== INSIGHT OTOMATIS ===")

    # Kesimpulan
    if pos > neg:
        print("Mayoritas komentar BERSIFAT POSITIF.")
    elif neg > pos:
        print("Mayoritas komentar BERSIFAT NEGATIF.")
    else:
        print("Komentar cenderung NETRAL.")

    # Top kata
    print("\nTop kata yang sering muncul:")
    for word, count in top_words[:5]:
        print("-", word)

    # Saran
    print("\n=== SARAN ===")
    if neg > pos:
        print("- Perlu evaluasi konten.")
        print("- Banyak kritik dari penonton.")
    else:
        print("- Konten diterima dengan baik.")
        print("- Pertahankan atau lanjutkan konten serupa.")

generate_insight(df, top_words)

# ===============================
# 9. SAVE DATA
# ===============================
df.to_csv("youtube_insight_result.csv", index=False)

print("\n✅ Data disimpan sebagai youtube_insight_result.csv")

# ===============================
# 10. VISUALISASI
# ===============================
df['sentiment'].value_counts().plot(kind='bar')
plt.title("Distribusi Sentimen")
plt.xlabel("Sentimen")
plt.ylabel("Jumlah Komentar")
plt.show()