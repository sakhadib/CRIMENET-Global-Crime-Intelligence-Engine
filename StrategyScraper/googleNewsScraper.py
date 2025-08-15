import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Union
from urllib.parse import urlparse
import json
from .scraper import NewsScraper

class GoogleNewsScraper(NewsScraper):
    def __init__(self, rss_url: str = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"):
        self.rss_url = rss_url
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        """
        Scrapes Google News RSS and returns [{'title','link'}].
        Prefers the original article link from <description>, else uses <link>.
        """
        try:
            resp = self._session.get(self.rss_url, timeout=20)
            if resp.status_code != 200:
                return f"Error: Unable to fetch RSS. Status code {resp.status_code}"

            soup = BeautifulSoup(resp.content, "xml")
            results: List[Dict[str, str]] = []

            for item in soup.find_all("item"):
                raw_title = (item.title.get_text(strip=True) if item.title else "").strip()

                # Try original source link in description
                original = None
                desc = item.find("description")
                if desc and desc.string:
                    try:
                        d = BeautifulSoup(desc.string, "html.parser")
                        a = d.find("a")
                        if a and a.get("href"):
                            original = a.get("href").strip()
                    except Exception:
                        pass

                # Fallback to link element
                fallback = (item.link.get_text(strip=True) if item.link else "").strip()
                link = original or fallback

                if raw_title and link:
                    results.append({"title": raw_title, "link": link})

            return results

        except Exception as e:
            return f"Error: {e}"

    def ScrapeFullText(self, url: str) -> str:
        """
        Fetches and extracts full article text from the given URL.
        Works for many publishers, but structure may vary.
        Heuristics:
          1) <article> p
          2) div[itemprop="articleBody"] p
          3) JSON-LD articleBody
          4) All <p> with length filter
        """
        try:
            resp = self._session.get(url, timeout=25)
            if resp.status_code != 200:
                return f"Error: Unable to fetch the article. Status code {resp.status_code}"

            soup = BeautifulSoup(resp.content, "html.parser")

            def collect_paragraphs(container: Tag) -> List[str]:
                parts: List[str] = []
                for p in container.find_all("p"):
                    txt = p.get_text(" ", strip=True)
                    if txt:
                        parts.append(txt)
                return parts

            # 1) Standard <article> body
            article = soup.find("article")
            if isinstance(article, Tag):
                parts = collect_paragraphs(article)
                if parts:
                    return "\n\n".join(parts)

            # 2) Common schema markup container
            article_body = soup.find(attrs={"itemprop": "articleBody"})
            if isinstance(article_body, Tag):
                parts = collect_paragraphs(article_body)
                if parts:
                    return "\n\n".join(parts)

            # 3) JSON-LD articleBody
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or "")
                    objs = data if isinstance(data, list) else [data]
                    for obj in objs:
                        if isinstance(obj, dict) and obj.get("@type") in ("NewsArticle", "Article"):
                            body = obj.get("articleBody")
                            if isinstance(body, str) and len(body.strip()) > 100:
                                return body.strip()
                except Exception:
                    continue

            # 4) Fallback: all <p> tags with length filter
            parts = []
            for p in soup.find_all("p"):
                txt = p.get_text(" ", strip=True)
                if txt and len(txt) > 40:
                    parts.append(txt)
            if parts:
                return "\n\n".join(parts)

            return "Error: No text content found in the article"

        except Exception as e:
            return f"Error: {e}"

    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Scrapes all paragraph texts from the given URL.
        """
        try:
            resp = self._session.get(url, timeout=20)
            if resp.status_code != 200:
                return f"Error: Unable to fetch the page. Status code {resp.status_code}"

            soup = BeautifulSoup(resp.content, "html.parser")
            paras = []
            for p in soup.find_all("p"):
                txt = p.get_text(" ", strip=True)
                if txt:
                    paras.append(txt)
            return paras if paras else "Error: No paragraphs found"
        except Exception as e:
            return f"Error: {e}"
