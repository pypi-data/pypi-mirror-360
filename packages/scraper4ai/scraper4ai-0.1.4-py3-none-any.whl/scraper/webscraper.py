import logging
import cloudscraper
from bs4 import BeautifulSoup
from crawl4ai import DefaultMarkdownGenerator
from urllib.parse import urljoin
from typing import List

from scraper.models import ScrapedResult, ImageData, LinkData, VideoData


class WebScraperError(Exception):
    pass

class WebScraper:
    def __init__(
        self,
        log_level: int = logging.INFO,
        tags_to_remove: list[str] = [],
        css_selectors_to_remove: list[str] = []
    ):
        self.log_level = log_level
        self.tags_to_remove = tags_to_remove
        self.css_selectors_to_remove = css_selectors_to_remove

    def fetch_content(
        self, 
        url: str, 
        timeout: int = 30,
        retries: int = 3
    ) -> str:
        if not url or not url.startswith(('http://', 'https://')):
            raise WebScraperError(f"Invalid URL: {url}")
            
        scraper = cloudscraper.create_scraper()
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',      # ブラウザを指定 (例: 'chrome' or 'firefox')
                'platform': 'windows',    # OSを指定 (例: 'windows', 'linux', 'darwin')
                'mobile': False           # モバイル版を無効にし、デスクトップ版を強制
            }
        )
        
        for attempt in range(retries):
            try:
                response = scraper.get(url, timeout=timeout)
                if response.status_code != 200:
                    if attempt == retries - 1:
                        raise WebScraperError(f"HTTP error: {response.status_code} - {url}")
                    continue
                return response.text
            except Exception as e:
                if attempt == retries - 1:
                    raise WebScraperError(f"Failed to fetch content: {e}")

    def clean_html(
        self, 
        html_content: str, 
    ) -> str:
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            default_tags = ["script", "style", "iframe", "noscript", "aside", "form", "svg", "a", "nav", "footer"]
            tags_to_process = list(set(default_tags + (self.tags_to_remove or [])))
            for tag in tags_to_process:
                for element in soup.find_all(tag):
                    element.decompose()
            if self.css_selectors_to_remove:
                for selector in self.css_selectors_to_remove:
                    for element in soup.select(selector):
                        element.decompose()
            return str(soup)
        except Exception:
            return html_content

    def html_to_markdown(
        self, 
        html_content: str, 
        base_url: str,
    ) -> str:
        try:
            markdown_generator = DefaultMarkdownGenerator()
            markdown = markdown_generator.generate_markdown(
                input_html=html_content,
                base_url=base_url,
            )
            return markdown.raw_markdown
        except Exception as e:
            raise WebScraperError(f"Failed to convert to Markdown: {e}")

    def extract_links(self, html: str, base_url: str) -> List[LinkData]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = urljoin(base_url, a_tag["href"])
            text = a_tag.get_text(strip=True) or None
            links.append(LinkData(url=href, text=text))
        return links

    def extract_images(self, html: str, base_url: str) -> List[ImageData]:
        soup = BeautifulSoup(html, "html.parser")
        images = []
        for img_tag in soup.find_all("img"):
            src = (
                img_tag.get("src") or
                img_tag.get("data-src") or
                img_tag.get("data-original") or
                img_tag.get("data-lazy")
            )

            if not src: continue

            src = src.strip()

            if src in ("", "#", "about:blank") or src.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, src)
            alt = img_tag.get("alt", None)
            images.append(ImageData(url=full_url, alt_text=alt))
        return images

    def extract_videos(self, html: str, base_url: str) -> List[VideoData]:
        soup = BeautifulSoup(html, "html.parser")
        videos = []

        for video_tag in soup.find_all("video"):
            if video_tag.has_attr("src"):
                src = urljoin(base_url, video_tag["src"])
                title = video_tag.get("title") or video_tag.get("aria-label") or video_tag.get_text(strip=True) or None
                videos.append(VideoData(url=src, title=title))

            for source_tag in video_tag.find_all("source", src=True):
                src = urljoin(base_url, source_tag["src"])
                title = video_tag.get("title") or video_tag.get("aria-label") or video_tag.get_text(strip=True) or None
                videos.append(VideoData(url=src, title=title))

        return videos

    def invoke(
        self, 
        url: str,
        timeout: int = 10,
        retries: int = 2
    ) -> ScrapedResult:
        raw_html = self.fetch_content(url, timeout, retries)
        cleaned_html = self.clean_html(raw_html)
        
        links = self.extract_links(raw_html, url)
        images = self.extract_images(cleaned_html, url)
        videos = self.extract_videos(cleaned_html, url)
        
        markdown_text = self.html_to_markdown(cleaned_html, url)

        return ScrapedResult(
            url=url,
            raw_html=raw_html,
            markdown=markdown_text,
            links=links,
            image_links=images,
            video_links=videos
        )

if __name__ == "__main__":
    scraper = WebScraper()
    content = scraper.invoke(url="https://news.yahoo.co.jp/articles/9668f5b01185c8da19db837abd7b5db930736e08/comments?page=3")
    print(content.markdown)