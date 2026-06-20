import os
import json
import urllib.request
from datetime import datetime

def run_youtube_bot():
    print("Démarrage du scanner de tendances YouTube...")
    
    # Récupération sécurisée de la clé API
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("Erreur : La clé YOUTUBE_API_KEY est introuvable.")
        return

    # Requête officielle vers l'API YouTube (Top 10 des vidéos les plus populaires en France)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode=FR&maxResults=10&key={api_key}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        video_items = data.get("items", [])
        structured_videos = []
        
        for video in video_items:
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})
            
            title = snippet.get("title", "Sans titre")
            description = snippet.get("description", "Aucune description.")
            tags = snippet.get("tags", [])
            views = stats.get("viewCount", "0")
            likes = stats.get("likeCount", "0")
            video_id = video.get("id")
            
            # Transformation des tags en #Hashtags exploitables
            hashtags = [f"#{tag.replace(' ', '')}" for tag in tags[:8]] if tags else ["#Trending", "#Viral"]
            
            # Nettoyage rapide de la description pour l'affichage
            clean_desc = description.split('\n')[0] if '\n' in description else description
            if len(clean_desc) > 200:
                clean_desc = clean_desc[:200] + "..."

            structured_videos.append({
                "title": title,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "views": views,
                "likes": likes,
                "hashtags": hashtags,
                "description": clean_desc,
                "channel_title": snippet.get("channelTitle")
            })
            
        # Sauvegarde au format JSON
        os.makedirs("data", exist_ok=True)
        maintenant = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        output_data = {
            "last_updated": maintenant,
            "videos": structured_videos
        }
        
        with open("data/youtube_viral.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
            
        print(f"Succès ! {len(structured_videos)} vidéos synchronisées.")
        
    except Exception as e:
        print(f"Erreur technique : {e}")
        raise e

if __name__ == "__main__":
    run_youtube_bot()
