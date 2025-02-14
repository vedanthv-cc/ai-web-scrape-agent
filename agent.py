from dotenv import load_dotenv
import os
from typing import TypedDict

# Load environment variables from the .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Import required modules from LangChain and (optionally) LangGraph-style constructs.
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Initialize your LLM with the API key.
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",
    openai_api_key=openai_api_key
)

# Create a summarization prompt and chain.
# Note: create_stuff_documents_chain expects a list of Document objects.
summarization_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following content concisely:\n\n{context}")
])
summarization_chain = create_stuff_documents_chain(llm, summarization_prompt)

# Create an overall sentiment prompt.
overall_sentiment_prompt = ChatPromptTemplate.from_messages([
    ("system", "Analyze the overall sentiment of the following content. Output exactly one word: positive, negative, or neutral.\n\nContent:\n{context}")
])
overall_sentiment_chain = overall_sentiment_prompt | llm

# Create a relation sentiment prompt.
relation_sentiment_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Analyze how well the following content relates to the keyword '{keyword}'. "
        "If the keyword is a central theme in the content, output 'positive'. "
        "If the keyword is mentioned but not central, output 'neutral'. "
        "If the content does not focus on the keyword, output 'negative'.\n\n"
        "Content:\n{context}. note:ignore any content not related to title"
    )
])
relation_sentiment_chain = relation_sentiment_prompt | llm

# Define a state schema using TypedDict.
class State(TypedDict):
    content: str
    summary: str
    keyword: str
    sentiment: str

# Helper function: extract plain text output.
def extract_sentiment(result) -> str:
    if hasattr(result, "content"):
        return result.content.strip()
    return str(result).strip()

# Define the node function that performs summarization and sentiment analysis.
def summarize_and_analyze(state: State) -> State:
    content = state["content"]
    keyword = state["keyword"]
    
    # Wrap the content string in a Document object for the summarization chain.
    from langchain.schema import Document
    doc = Document(page_content=content, metadata={})
    summary_result = summarization_chain.invoke({"context": [doc]})
    
    # Compute overall sentiment.
    overall_result = overall_sentiment_chain.invoke({"context": content})
    overall_sent = extract_sentiment(overall_result)
    
    # Compute relation sentiment with respect to the keyword.
    relation_result = relation_sentiment_chain.invoke({"context": content, "keyword": keyword})
    relation_sent = extract_sentiment(relation_result)
    
    # Combine the two sentiment values into a single output.
    combined_sent = f"overall: {overall_sent}, relation: {relation_sent}"
    
    return {
        "content": content,
        "summary": summary_result,
        "keyword": keyword,
        "sentiment": combined_sent
    }
