import json
import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Union, Dict
from .scraper import NewsScraper

class YahooNewsScraper(NewsScraper):
    def __init__(self, rss_url: str = "https://news.yahoo.com/rss/"):
        self.rss_url = rss_url
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        """
        Scrapes Yahoo News RSS and returns headlines with their links.
        Returns a list of dicts with 'title' and 'link'.
        """
        try:
            resp = self._session.get(self.rss_url, timeout=20)
            if resp.status_code != 200:
                return f"Error: Unable to fetch RSS. Status code {resp.status_code}"

            soup = BeautifulSoup(resp.content, "xml")

            results: List[Dict[str, str]] = []
            for item in soup.find_all("item"):
                title = (item.title.get_text(strip=True) if item.title else "").strip()
                link = (item.link.get_text(strip=True) if item.link else "").strip()

                if title and link:
                    results.append({
                        "title": title,
                        "link": link
                    })

            return results

        except Exception as e:
            return f"Error: {e}"


    def ScrapeFullText(self, url: str) -> str:
        """
        Scrapes full article text from a Yahoo News article URL.
        Heuristics:
            1) Yahoo CAAS layout: div.caas-body p
            2) JSON-LD Article object -> articleBody
            3) <article> p fallback
            4) All <p> (filtered)
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

            # 1) Yahoo CAAS body
            caas = soup.select_one("div.caas-body") or soup.select_one('article div.caas-body')
            if isinstance(caas, Tag):
                parts = collect_paragraphs(caas)
                if parts:
                    return "\n\n".join(parts)

            # 2) JSON-LD Article with articleBody
            # Yahoo often includes structured data; try to extract a long articleBody if present.
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or "")
                    # Could be a list or a single dict
                    objs = data if isinstance(data, list) else [data]
                    for obj in objs:
                        if isinstance(obj, dict) and obj.get("@type") in ("NewsArticle", "Article"):
                            body = obj.get("articleBody")
                            if isinstance(body, str) and len(body.strip()) > 100:
                                return body.strip()
                except Exception:
                    continue

            # 3) Generic <article> p
            article = soup.find("article")
            if isinstance(article, Tag):
                parts = collect_paragraphs(article)
                if parts:
                    return "\n\n".join(parts)

            # 4) Last-resort: all <p>, filter very short/junk
            parts: List[str] = []
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
        Simple special: return all non-empty paragraph texts from the URL.
        """
        try:
            resp = self._session.get(url, timeout=20)
            if resp.status_code != 200:
                return f"Error: Unable to fetch the page. Status code {resp.status_code}"

            soup = BeautifulSoup(resp.content, "html.parser")
            out: List[str] = []
            for p in soup.find_all("p"):
                txt = p.get_text(" ", strip=True)
                if txt:
                    out.append(txt)
            return out if out else "Error: No paragraphs found"
        except Exception as e:
            return f"Error: {e}"
