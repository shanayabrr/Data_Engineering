import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import re

# ===============================
# API KEY
# ===============================
API_KEY = "AIzaSyBNbv7e71WZieftC2VqGD9L5XwKKLIkjHw"

youtube = build('youtube', 'v3', developerKey=API_KEY)

# ===============================
# UI
# ===============================
st.title("📊 YouTube Comment Insight Analyzer")
st.write("DzwkcbTQ7ZE")

video_id = st.text_input("Video ID", "")

# ===============================
# AMBIL KOMENTAR
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

# ===============================
# CLEANING
# ===============================
def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower()

# ===============================
# SENTIMENT
# ===============================
kata_positif = ["bagus","keren","mantap","hebat","sukses"]
kata_negatif = ["jelek","buruk","gagal","parah","benci"]

def classify_sentiment(text):
    score = 0
    for word in kata_positif:
        if word in text:
            score += 1
    for word in kata_negatif:
        if word in text:
            score -= 1

    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"

# ===============================
# BUTTON
# ===============================
if st.button("Analyze"):

    st.write("Mengambil komentar...")

    comments = get_comments(video_id)
    df = pd.DataFrame({"comment": comments})

    df["clean"] = df["comment"].apply(clean_text)
    df["sentiment"] = df["clean"].apply(classify_sentiment)

    # ===============================
    # HASIL
    # ===============================
    st.subheader("📊 Distribusi Sentimen")
    sentiment_counts = df["sentiment"].value_counts()
    st.write(sentiment_counts)

    # Grafik
    fig, ax = plt.subplots()
    sentiment_counts.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    # ===============================
    # TOP WORDS
    # ===============================
    words = " ".join(df["clean"]).split()
    word_counts = Counter(words).most_common(5)

    st.subheader("🔤 Kata yang sering muncul")
    for word, count in word_counts:
        st.write(f"{word} : {count}")

    # ===============================
    # INSIGHT
    # ===============================
    st.subheader("🧠 Insight Otomatis")

    pos = sentiment_counts.get("Positive",0)
    neg = sentiment_counts.get("Negative",0)

    if pos > neg:
        st.success("Mayoritas komentar POSITIF 👍")
        st.write("Saran: lanjutkan konten serupa")
    elif neg > pos:
        st.error("Mayoritas komentar NEGATIF 👎")
        st.write("Saran: evaluasi konten")
    else:
        st.info("Komentar NETRAL")

    # ===============================
    # TABEL
    # ===============================
    st.subheader("💬 Contoh Komentar")
    st.dataframe(df.head(10))