import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Union, Optional
from urllib.parse import urljoin
import json
from .scraper import NewsScraper


class NewYorkTimesScraper(NewsScraper):
    """
    Scraper for https://www.nytimes.com/
    - ScrapeHome(): collects home page headlines with links (and summary when available)
    - ScrapeFullText(url): pulls full text from an article page
    - ScrapeSpecial(url): quick paragraph grabber for any NYT URL
    """

    BASE = "https://www.nytimes.com/"

    def __init__(self, home_url: str = BASE):
        self.home_url = home_url
        self._session = requests.Session()
        self._session.headers.update({
            # NYTimes can be picky about UA + Accept-Language
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        })

    # ---------- helpers

    def _text(self, el: Optional[Tag]) -> str:
        return (el.get_text(" ", strip=True) if isinstance(el, Tag) else "").strip()

    # ---------- API

    def ScrapeHome(self) -> Union[List[Dict[str, str]], str]:
        """
        Returns a list of dicts: [{'title','link','summary'?}]
        Primary selector follows the provided DOM:
            - anchor: a.tpl-lbl[href]
            - title: the <p> headline inside that anchor (e.g., div[data-tpl="h"] p)
            - summary: a sibling <p> with class containing 'summary' (best-effort)
        Falls back to common NYT headline patterns (h3 > a, etc.).
        """
        try:
            r = self._session.get(self.home_url, timeout=25)
            if r.status_code != 200:
                return f"Error: Unable to fetch NYT home. Status code {r.status_code}"

            soup = BeautifulSoup(r.content, "html.parser")
            out: List[Dict[str, str]] = []

            # --- 1) Primary: your provided structure (a.tpl-lbl ... p headline)
            for a in soup.select('a.tpl-lbl[href]'):
                link = urljoin(self.BASE, a.get("href", "").strip())
                # headline p is typically inside the anchor
                title_p = a.select_one("p")
                title = self._text(title_p)
                if not title:
                    # sometimes headline is in an h3 within the anchor
                    title = self._text(a.select_one("h3"))
                if not title:
                    continue

                item: Dict[str, str] = {"title": title, "link": link}

                # try to pick up nearby summary (your screenshot flagged a 'summary-class')
                # look at parent containers for a sibling <p> that smells like a summary
                parent = a.parent
                summary = ""
                # direct sibling
                sib_p = getattr(parent, "find_next_sibling", lambda *_: None)("p")
                if isinstance(sib_p, Tag):
                    summary = self._text(sib_p)
                # class hint contains 'summary' (e.g., summary-class css-…)
                if not summary:
                    hint = parent.find("p", class_=lambda c: c and "summary" in c)
                    if isinstance(hint, Tag):
                        summary = self._text(hint)
                if summary:
                    item["summary"] = summary

                out.append(item)

            # --- 2) Fallbacks: generic home modules NYT uses frequently
            if not out:
                # h3 > a (common)
                for h3a in soup.select("h3 a[href]"):
                    title = self._text(h3a)
                    link = urljoin(self.BASE, h3a.get("href", ""))
                    if title and link:
                        out.append({"title": title, "link": link})

            if not out:
                # any <a> that looks like a story label with nested <p>
                for a in soup.select("a[href]"):
                    p = a.find("p")
                    title = self._text(p) or self._text(a)
                    if len(title) > 35:  # avoid nav links
                        link = urljoin(self.BASE, a.get("href", ""))
                        out.append({"title": title, "link": link})

            # de-dup by link
            seen = set()
            deduped = []
            for it in out:
                if it["link"] not in seen:
                    deduped.append(it)
                    seen.add(it["link"])

            return deduped[:60]  # keep it sane

        except Exception as e:
            return f"Error: {e}"

    def ScrapeFullText(self, url: str) -> str:
        """
        Extracts full article text from an NYT story.
        Heuristics (in order):
          1) section[name="articleBody"] p
          2) article p (NYT often wraps body in <article>)
          3) JSON-LD NewsArticle.articleBody (when present)
          4) Fallback: all <p> with length filter
        Note: Some content is paywalled; we still return what is in the DOM.
        """
        try:
            r = self._session.get(url, timeout=30)
            if r.status_code != 200:
                return f"Error: Unable to fetch article. Status code {r.status_code}"

            soup = BeautifulSoup(r.content, "html.parser")

            def collect_paras(container: Tag) -> List[str]:
                parts: List[str] = []
                for p in container.find_all("p"):
                    t = self._text(p)
                    if t:
                        parts.append(t)
                return parts

            # 1) Preferred NYT body container
            body = soup.select_one('section[name="articleBody"]')
            if isinstance(body, Tag):
                parts = collect_paras(body)
                if parts:
                    return "\n\n".join(parts)

            # 2) Generic <article> container
            article = soup.find("article")
            if isinstance(article, Tag):
                parts = collect_paras(article)
                if parts:
                    return "\n\n".join(parts)

            # 3) JSON-LD attempt
            for s in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(s.string or "")
                    nodes = data if isinstance(data, list) else [data]
                    for node in nodes:
                        if isinstance(node, dict) and node.get("@type") in ("NewsArticle", "Article"):
                            body_text = node.get("articleBody")
                            if isinstance(body_text, str) and len(body_text.strip()) > 120:
                                return body_text.strip()
                except Exception:
                    continue

            # 4) Fallback: all <p> with a length filter (avoids nav, captions)
            parts = []
            for p in soup.find_all("p"):
                t = self._text(p)
                if len(t) > 50:
                    parts.append(t)
            if parts:
                return "\n\n".join(parts)

            return "Error: No text content found in the article."
        except Exception as e:
            return f"Error: {e}"

    def ScrapeSpecial(self, url: str) -> Union[List[str], str]:
        """
        Simple paragraph grabber for any NYT URL.
        Returns a list of paragraph strings (or an error string).
        """
        try:
            r = self._session.get(url, timeout=25)
            if r.status_code != 200:
                return f"Error: Unable to fetch page. Status code {r.status_code}"
            soup = BeautifulSoup(r.content, "html.parser")
            paras: List[str] = []
            for p in soup.find_all("p"):
                t = self._text(p)
                if t:
                    paras.append(t)
            return paras if paras else "Error: No paragraphs found."
        except Exception as e:
            return f"Error: {e}"
