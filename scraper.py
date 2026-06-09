"""Scraping YouTube untuk Wisata Indonesia - 3 Kategori (Positif, Negatif, Netral)"""

import pandas as pd
import time
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ========== KONFIGURASI ==========
API_KEY = "" #YOUTUBE API KEY

# Keyword Positif (rekomendasi, keindahan, kepuasan)
KEYWORDS_POSITIF = [
    "surga tersembunyi di indonesia",
    "kuliner khas daerah wisata indonesia",
    "hotel estetik murah di bali",
    "itinerary liburan jogja seru",
    "rekomendasi wisata keluarga indonesia",
    "pesona budaya indonesia memukau",
    "hidden gem wisata indonesia",
    "trip murah tapi mewah indonesia",
    "pemandangan alam terbaik indonesia",
    "tips liburan hemat di indonesia"
]

# Keyword Negatif (keluhan, kritik, peringatan)
KEYWORDS_NEGATIF = [
    "penipuan harga tiket wisata",
    "pungli di tempat wisata indonesia",
    "wisata indonesia yang terbengkalai",
    "hindari tempat wisata ini",
    "pengalaman buruk liburan di bali",
    "wisata alam rusak karena sampah",
    "jebakan Batman kuliner wisata",
    "fasilitas wisata indonesia yang buruk",
    "tempat wisata paling kotor",
    "kapok liburan ke tempat ini"
]

# Keyword Netral/Informatif (panduan, fakta)
KEYWORDS_NETRAL = [
    "biaya liburan ke labuan bajo",
    "cara menuju raja ampat backpacker",
    "review jujur hotel di lombok",
    "rute perjalanan wisata bromo",
    "kondisi terkini tempat wisata",
    "peraturan terbaru masuk candi borobudur"
]

# Gabungkan semua dengan label sumber
KEYWORDS_SOURCE = (
    [(kw, 'positif') for kw in KEYWORDS_POSITIF] +
    [(kw, 'negatif') for kw in KEYWORDS_NEGATIF] +
    [(kw, 'netral') for kw in KEYWORDS_NETRAL]
)

# Target komentar per keyword
TARGET_PER_KEYWORD = 1000   # total: (10+10+6)*300 = 7800 komentar (bisa diubah)

# Filter komentar
MIN_PANJANG = 30
MAX_PANJANG = 150
MAX_VIDEOS_PER_KEYWORD = 10
KOMENTAR_PER_VIDEO = 200
OUTPUT_FILE = "wisata_indonesia_3_kategori.csv"

# ========== FUNGSI ==========
def rapihin_komentar(text):
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').lower()
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

youtube = build('youtube', 'v3', developerKey=API_KEY)

def search_videos(keyword, max_results):
    video_ids = []
    next_page_token = None
    remaining = max_results
    while remaining > 0:
        page_size = min(50, remaining)
        request = youtube.search().list(
            part='id',
            q=keyword,
            type='video',
            maxResults=page_size,
            pageToken=next_page_token,
            order='relevance'
        )
        response = request.execute()
        for item in response.get('items', []):
            video_ids.append(item['id']['videoId'])
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        remaining -= len(response.get('items', []))
    return video_ids

def filter_komen(video_id, max_to_collect, min_len, max_len, seen_texts):
    comments = []
    next_pg = None
    try:
        while len(comments) < max_to_collect:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_to_collect - len(comments)),
                pageToken=next_pg,
                textFormat='plainText'
            )
            response = request.execute()
            for item in response['items']:
                snippet = item['snippet']['topLevelComment']['snippet']
                raw_text = snippet['textDisplay']
                cleaned = rapihin_komentar(raw_text)
                comment_len = len(cleaned)
                if min_len <= comment_len <= max_len:
                    if cleaned in seen_texts:
                        continue
                    comments.append(cleaned)
                    seen_texts.add(cleaned)
                    if len(comments) >= max_to_collect:
                        break
            next_pg = response.get('nextPageToken')
            if not next_pg:
                break
            time.sleep(0.2)
    except HttpError as e:
        if e.resp.status == 403 and 'commentsDisabled' in str(e):
            print(f"  ⚠️ Komentar dinonaktifkan untuk video {video_id}, dilewati.")
        else:
            print(f"  ⚠️ Error lain pada video {video_id}: {e}")
    return comments

# ========== MAIN ==========
all_comments = []
seen_texts = set()

for keyword, sent_label in KEYWORDS_SOURCE:
    print(f"\n{'='*50}")
    print(f"Keyword: {keyword} (sentimen sumber: {sent_label}) | target {TARGET_PER_KEYWORD}")
    print(f"{'='*50}")
    
    video_ids = search_videos(keyword, MAX_VIDEOS_PER_KEYWORD)
    if not video_ids:
        print(f"  Tidak ada video ditemukan untuk keyword '{keyword}'.")
        continue
    
    collected = 0
    for v_id in video_ids:
        if collected >= TARGET_PER_KEYWORD:
            break
        sisa = TARGET_PER_KEYWORD - collected
        max_ambil = min(sisa, KOMENTAR_PER_VIDEO)
        komentar_baru = filter_komen(v_id, max_ambil, MIN_PANJANG, MAX_PANJANG, seen_texts)
        all_comments.extend(komentar_baru)
        collected += len(komentar_baru)
        print(f"  Progress: {collected}/{TARGET_PER_KEYWORD} | Total global: {len(all_comments)}")
        time.sleep(0.5)

# Simpan semua komentar (tanpa label, hanya teks)
df = pd.DataFrame(all_comments, columns=['comment'])
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"\n✅ TOTAL: {len(df)} komentar disimpan ke {OUTPUT_FILE}")
print("\nTip: Gunakan keyword_source untuk labeling otomatis nanti.")