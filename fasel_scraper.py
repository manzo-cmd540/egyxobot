import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


async def scrape_fasel(query: str):
    """البحث في Fasel HD"""
    
    try:
        search_url = f"https://faselhd.link/search/{query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        
        items = soup.find_all("div", class_="movie-item")[:5]
        
        for item in items:
            try:
                title_elem = item.find("h3")
                if title_elem:
                    title = title_elem.text.strip()
                    
                    results.append({
                        'title': title,
                        'quality': '720p',
                        'source': 'Fasel HD',
                        'link': 'https://faselhd.link'
                    })
            except:
                continue
        
        logger.info(f"✅ Fasel: {len(results)} نتائج")
        
        return results
    
    except Exception as e:
        logger.error(f"❌ خطأ في Fasel: {e}")
        return []