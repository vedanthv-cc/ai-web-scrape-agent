import streamlit as st
from news_fetcher import fetch_and_ocr_news
from agent import summarize_and_analyze 

# Configure the page layout and title
st.set_page_config(page_title="📰 News Extractor", layout="wide")
st.title("📰 AI-Powered News Extractor and Sentiment Analysis")
st.write("Enter a keyword to fetch the latest news. Each article’s content will be summarized and its sentiment analyzed using an AI agent.")

# Sidebar for options
with st.sidebar:
    st.header("Options")
    keyword = st.text_input("Search Keyword", value="", placeholder="Enter Key Word")
    max_results = st.slider("Number of Articles", 1, 10, 5)
    fetch_news = st.button("Fetch News")

# Main page: display fetched news articles as cards
if fetch_news:
    with st.spinner("Fetching articles..."):
        articles = fetch_and_ocr_news(keyword, max_results)
    
    if articles:
        for idx, article in enumerate(articles, start=1):
            # Prepare a state dict for the agent.
            state = {
                "content": article["content"] + "title = "+ article['title'],
                "summary": "",
                "keyword": keyword,
                "sentiment": ""
            }
            # Use the agent to summarize and analyze sentiment.
            analysis = summarize_and_analyze(state)
            summary = analysis.get("summary", "No summary available.")
            sentiment = analysis.get("sentiment", "Neutral")
            
            # Display the article card header with title and key details.
            st.markdown(f"### Article {idx}: {article['title']}")
            st.markdown(f"[Read More]({article['url']})")
            st.markdown(
                f"**Source:** {article.get('source', 'Unknown')}  |  "
                f"**Published:** {article.get('published', 'N/A')}  |  "
                f"**Method:** {article.get('method', 'UNKNOWN')}"
            )
            st.markdown(f"**Scraped At:** {article.get('scraped_at', 'Not scraped')}")
            st.markdown(f"**Sentiment:** {sentiment}")
            
            # Expander to show the summarized content.
            with st.expander("Show Summary"):
                st.write(summary)
            
            # Expander to show the original content.
            with st.expander("Show Original Content"):
                st.write(article["content"])
            
            # Expander for OCR screenshot (only if method is OCR and screenshot exists)
            if article.get("method") == "OCR" and article.get("screenshot"):
                with st.expander("Show OCR Screenshot"):
                    st.image(article["screenshot"], use_column_width=True)
                    with open(article["screenshot"], "rb") as file:
                        st.download_button(
                            label="Download Screenshot",
                            data=file,
                            file_name=article["screenshot"],
                            mime="image/png"
                        )
            st.markdown("---")
    else:
        st.error("No articles found. Try another keyword.")
