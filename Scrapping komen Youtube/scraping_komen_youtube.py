from googleapiclient.discovery import build
import pandas as pd
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Konfigurasi
API_KEY = "AIzaSyDghaNhddOA5mSA1j5gXiQUZ0TYcTbusro"
VIDEO_ID = "DzwkcbTQ7ZE"

def get_youtube_comments(v_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=v_id,
        maxResults=100,
        textFormat="plainText"
    )
    response = request.execute()
    return [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]

try:
    # 1. Ambil data
    comments = get_youtube_comments(VIDEO_ID)
    print(f"Berhasil mengambil {len(comments)} komentar.")

    # 2. Simpan file
    pd.DataFrame(comments, columns=['Komentar']).to_csv("hasil_scraping.csv", index=False, encoding='utf-8')
    print("Data disimpan ke hasil_scraping.csv")

    # 3. Proses teks
    raw_text = " ".join(comments).lower()
    words = re.findall(r'\b\w+\b', raw_text)
    
    stopwords = {
        'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'adalah', 'ya', 'ga', 
        'gak', 'ada', 'dengan', 'bisa', 'untuk', 'aja', 'sudah', 'udah', 'bang',
        'kalau', 'kalo', 'juga', 'kok', 'si', 'nih', 'dia', 'saya', 'kamu'
    }
    
    clean_words = [w for w in words if w not in stopwords and len(w) > 2]
    final_string = " ".join(clean_words)

    # 4. Analisis frekuensi
    print("\nSTATISTIK KATA TERBANYAK:")
    for kata, jumlah in Counter(clean_words).most_common(10):
        print(f"{kata.capitalize():<15} : {jumlah}")

    # 5. Visualisasi WordCloud
    print("\nGenerate WordCloud...")
    wc = WordCloud(width=800, height=400, background_color='white').generate(final_string)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig("wordcloud_hasil.png")
    plt.show()

except Exception as e:
    print(f"Error: {e}")
