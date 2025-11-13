import logging
import asyncio
from typing import List, Dict
import aiohttp
import random
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import time

logger = logging.getLogger(__name__)

# User Agents محدثة
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15"
]

# Proxies (يمكن إضافة proxies حقيقية)
PROXIES = []

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2


class AdvancedScraper:
    """سكرابر متقدم يتجاوز الحماية"""
    
    def __init__(self):
        self.session = None
        self.playwright = None
        self.browser = None
    
    async def init(self):
        """تهيئة السكرابر"""
        try:
            self.session = aiohttp.ClientSession()
            logger.info("✅ تم تهيئة السكرابر")
        except Exception as e:
            logger.error(f"❌ خطأ في التهيئة: {e}")
    
    async def close(self):
        """إغلاق السكرابر"""
        if self.session:
            await self.session.close()
        if self.browser:
            await self.browser.close()
    
    def _get_random_user_agent(self) -> str:
        """الحصول على User Agent عشوائي"""
        return random.choice(USER_AGENTS)
    
    def _get_random_proxy(self) -> str:
        """الحصول على proxy عشوائي"""
        if PROXIES:
            return random.choice(PROXIES)
        return None
    
    async def _fetch_with_retry(self, url: str, method: str = "GET", **kwargs) -> str:
        """جلب الصفحة مع إعادة محاولة"""
        
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                proxy = self._get_random_proxy()
                
                logger.info(f"🔄 المحاولة {attempt + 1}/{MAX_RETRIES}: {url}")
                
                async with self.session.request(
                    method,
                    url,
                    headers=headers,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False,
                    **kwargs
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        logger.info(f"✅ نجح: {url}")
                        return text
                    elif response.status == 403:
                        logger.warning(f"⚠️ محجوب (403): {url}")
                    elif response.status == 429:
                        logger.warning(f"⚠️ طلبات كثيرة (429): {url}")
                        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    else:
                        logger.warning(f"⚠️ حالة {response.status}: {url}")
            
            except Exception as e:
                logger.warning(f"⚠️ خطأ في المحاولة {attempt + 1}: {str(e)}")
                await asyncio.sleep(RETRY_DELAY)
        
        logger.error(f"❌ فشل بعد {MAX_RETRIES} محاولات: {url}")
        return None
    
    async def _fetch_with_playwright(self, url: str) -> str:
        """جلب الصفحة باستخدام Playwright"""
        
        try:
            if not self.browser:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
            
            logger.info(f"🌐 جاري الجلب بـ Playwright: {url}")
            
            page = await self.browser.new_page()
            
            await page.set_extra_http_headers({
                "User-Agent": self._get_random_user_agent()
            })
            
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            await asyncio.sleep(2)
            
            content = await page.content()
            await page.close()
            
            logger.info(f"✅ نجح Playwright: {url}")
            return content
        
        except Exception as e:
            logger.error(f"❌ خطأ Playwright: {str(e)}")
            return None
    
    async def search_fasel(self, query: str) -> List[Dict]:
        """البحث في Fasel HD"""
        
        try:
            url = f"https://faselhd.link/search/{query.replace(' ', '+')}"
            
            html = await self._fetch_with_retry(url)
            
            if not html:
                html = await self._fetch_with_playwright(url)
            
            if not html:
                logger.warning(f"❌ فشل جلب: {url}")
                return []
            
            soup = BeautifulSoup(html, "html.parser")
            results = []
            
            items = soup.find_all("div", class_=["movie-item", "film-item", "search-result"])
            
            for item in items[:10]:
                try:
                    title_elem = item.find("h3") or item.find("a")
                    link_elem = item.find("a")
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get("href", "")
                        
                        quality_text = item.get_text()
                        quality = "720p"
                        if "1080" in quality_text:
                            quality = "1080p"
                        elif "480" in quality_text:
                            quality = "480p"
                        
                        results.append({
                            'title': title,
                            'quality': quality,
                            'source': 'Fasel HD',
                            'link': link,
                            'type': 'movie'
                        })
                
                except Exception as e:
                    logger.warning(f"⚠️ خطأ في استخراج العنصر: {e}")
                    continue
            
            logger.info(f"✅ Fasel: {len(results)} نتائج")
            return results
        
        except Exception as e:
            logger.error(f"❌ خطأ Fasel: {str(e)}")
            return []
    
    async def search_wecima(self, query: str) -> List[Dict]:
        """البحث في Wecima"""
        
        try:
            url = f"https://wecima.show/search/{query.replace(' ', '+')}"
            
            html = await self._fetch_with_retry(url)
            
            if not html:
                html = await self._fetch_with_playwright(url)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, "html.parser")
            results = []
            
            items = soup.find_all("div", class_=["movie-item", "film-item"])
            
            for item in items[:10]:
                try:
                    title_elem = item.find("h3") or item.find("a")
                    link_elem = item.find("a")
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get("href", "")
                        
                        results.append({
                            'title': title,
                            'quality': '720p',
                            'source': 'Wecima',
                            'link': link,
                            'type': 'series'
                        })
                
                except:
                    continue
            
            logger.info(f"✅ Wecima: {len(results)} نتائج")
            return results
        
        except Exception as e:
            logger.error(f"❌ خطأ Wecima: {e}")
            return []
    
    async def search_eflix(self, query: str) -> List[Dict]:
        """البحث في Eflix"""
        
        try:
            url = f"https://eflix.cam/search/{query.replace(' ', '+')}"
            
            html = await self._fetch_with_retry(url)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, "html.parser")
            results = []
            
            items = soup.find_all("div", class_=["movie", "film"])
            
            for item in items[:10]:
                try:
                    title_elem = item.find("h3")
                    if title_elem:
                        title = title_elem.text.strip()
                        
                        results.append({
                            'title': title,
                            'quality': '720p',
                            'source': 'Eflix',
                            'link': url,
                            'type': 'mixed'
                        })
                
                except:
                    continue
            
            logger.info(f"✅ Eflix: {len(results)} نتائج")
            return results
        
        except Exception as e:
            logger.error(f"❌ خطأ Eflix: {e}")
            return []
    
    async def search_all(self, query: str) -> List[Dict]:
        """البحث في جميع المواقع بالتوازي"""
        
        logger.info(f"🔍 جاري البحث عن: {query}")
        
        tasks = [
            self.search_fasel(query),
            self.search_wecima(query),
            self.search_eflix(query)
        ]
        
        results_list = await asyncio.gather(*tasks)
        
        all_results = []
        for results in results_list:
            all_results.extend(results)
        
        unique_results = []
        seen_titles = set()
        
        for result in all_results:
            if result['title'] not in seen_titles:
                unique_results.append(result)
                seen_titles.add(result['title'])
        
        logger.info(f"✅ إجمالي النتائج: {len(unique_results)}")
        return unique_results


advanced_scraper = AdvancedScraper()