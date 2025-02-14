from duckduckgo_search import DDGS
from ocr_tool import extract_text_from_url  # Updated OCR tool
import time

def fetch_and_ocr_news(keyword, max_results=5):
    """Fetch news articles via DuckDuckGo and extract content using OCR only."""
    newsarticles = []
    with DDGS() as ddgs:
        for r in ddgs.news(keyword, max_results=max_results):
            article = {
                'title': r.get('title', 'No Title'),
                'url': r.get('url', 'No URL'),
                'source': r.get('source', 'Unknown Source'),
                'published': r.get('date', 'No Date Available')
            }
            newsarticles.append(article)

    # For each article, use OCR to extract text from a screenshot of the page.
    for article in newsarticles:
        url = article['url']
        # Create a unique filename for the screenshot
        screenshot_filename = f"screenshot_{int(time.time())}.png"
        try:
            content, screenshot_path = extract_text_from_url(url, screenshot_path=screenshot_filename)
        except Exception as e:
            print(f"Error processing OCR for {url}: {e}")
            content = ""
            screenshot_path = None
        article['content'] = content
        article['screenshot'] = screenshot_path  # Save screenshot path (if any)
        article['scraped_at'] = "OCR only"
        article['method'] = "OCR"
    return newsarticles

# if __name__ == "__main__":
#     articles = fetch_and_ocr_news("open ai", max_results=5)
#     for article in articles:
#         print(article)
