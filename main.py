import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from news_fetcher import fetch_and_ocr_news
from agent import summarize_and_analyze
import urllib.parse
from datetime import datetime

# --- Helper Function for Email Body ---
def compile_email_body_plain(email_articles):
    """
    Compile a plain-text email body containing the title, summary, sentiment, and "Read More" link for each article.
    """
    body = ""
    for item in email_articles:
        body += f"Title: {item['title']}\n"
        body += f"Summary: {item['summary']}\n"
        body += f"Sentiment: {item['sentiment']}\n"
        body += f"Read More: {item['url']}\n"
        body += "---------------------------\n"
    return body

# --- Main App Code ---

# Set page config first
st.set_page_config(page_title="📰 News Extractor", layout="wide")

# Load authentication configuration
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Initialize session state if not already set
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

# If not authenticated, show the login form
if st.session_state["authentication_status"] is not True:
    st.title("🔒 Login to Access News Extractor")
    login_result = authenticator.login('main', fields={'Form name': 'custom_form_name'})
    if login_result is not None:
        name, authentication_status, username = login_result
        if authentication_status:
            st.session_state["authentication_status"] = True
            st.session_state["name"] = name
            st.session_state["username"] = username
        elif authentication_status is False:
            st.error("Username or password is incorrect")
        else:
            st.warning("Please enter your credentials to continue.")
    if st.session_state["authentication_status"] is not True:
        st.stop()

# Once authenticated, render the main app
if st.session_state["authentication_status"]:
    # Sidebar logout button
    with st.sidebar:
        st.success(f"Welcome, {st.session_state.get('name', 'User')}!")
        if st.sidebar.button("Logout"):
            authenticator.logout("Logout", "sidebar")
            if hasattr(authenticator, "cookie_controller"):
                authenticator.cookie_controller.delete_cookie()
            st.session_state["authentication_status"] = None
            st.rerun()

    st.title("📰 AI-Powered News Extractor and Sentiment Analysis")
    st.write("Enter a keyword to fetch the latest news. Each article’s content will be summarized and its sentiment analyzed using an AI agent.")

    # Sidebar for search options
    with st.sidebar:
        st.header("Options")
        keyword = st.text_input("Search Keyword", value="", placeholder="Enter Key Word")
        max_results = st.slider("Number of Articles", 1, 10, 5)
        fetch_news = st.button("Fetch News")

    email_articles = []  # List to store article details for the email

    # Fetch and display articles when the button is clicked
    if fetch_news:
        with st.spinner("Fetching articles..."):
            articles = fetch_and_ocr_news(keyword, max_results)

        if articles:
            for idx, article in enumerate(articles, start=1):
                # Prepare state for analysis
                state = {
                    "content": article["content"] + " title = " + article["title"],
                    "summary": "",
                    "keyword": keyword,
                    "sentiment": "",
                }
                analysis = summarize_and_analyze(state)
                summary = analysis.get("summary", "No summary available.")
                sentiment = analysis.get("sentiment", "Neutral")
                
                # Save key info for the email
                email_articles.append({
                    "title": article["title"],
                    "summary": summary,
                    "sentiment": sentiment,
                    "url": article.get("url", "#")
                })
                
                st.markdown(f"### Article {idx}: {article['title']}")
                st.markdown(f"[Read More]({article['url']})")
                st.markdown(
                    f"**Source:** {article.get('source', 'Unknown')}  |  "
                    f"**Published:** {article.get('published', 'N/A')}  |  "
                    f"**Method:** {article.get('method', 'UNKNOWN')}"
                )
                st.markdown(f"**Scraped At:** {article.get('scraped_at', 'Not scraped')}")
                st.markdown(f"**Sentiment:** {sentiment}")

                with st.expander("Show Summary"):
                    st.write(summary)

                with st.expander("Show Original Content"):
                    st.write(article["content"])

                if article.get("method") == "OCR" and article.get("screenshot"):
                    with st.expander("Show OCR Screenshot"):
                        st.image(article["screenshot"], use_column_width=True)
                        with open(article["screenshot"], "rb") as file:
                            st.download_button(
                                label="Download Screenshot",
                                data=file,
                                file_name=article["screenshot"],
                                mime="image/png",
                            )
                st.markdown("---")
        else:
            st.error("No articles found. Try another keyword.")

    # If articles have been fetched, add a "Send News via Gmail" button in the sidebar
    if email_articles:
        now = datetime.now()
        subject = f"Scraped News from News Extractor - {now.strftime('%Y-%m-%d %H:%M:%S')}"
        body_plain = compile_email_body_plain(email_articles)
        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body_plain)
        # Gmail compose URL
        gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&tf=1&su={encoded_subject}&body={encoded_body}"
        # Display the button in the sidebar as HTML
        st.sidebar.markdown(
            f'<a href="{gmail_link}" target="_blank"><button style="padding:10px; background-color:#4CAF50; border:none; color:white; font-size:16px; cursor:pointer;">Send News via Gmail</button></a>',
            unsafe_allow_html=True
        )
