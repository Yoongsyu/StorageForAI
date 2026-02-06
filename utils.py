import os
import streamlit as st
from github import Github, Auth
import google.generativeai as genai
import feedparser
from datetime import datetime
import json
import time

# --- Gemini API Setup ---
def init_gemini(api_key):
    """Initializes the Gemini API."""
    if not api_key:
        st.error("Gemini API Key가 설정되지 않았습니다.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-flash-latest')

# --- GitHub Integration ---
def init_github(token):
    """Initializes the GitHub instance."""
    if not token:
        st.error("GitHub Token이 설정되지 않았습니다.")
        return None
    auth = Auth.Token(token)
    return Github(auth=auth)

def get_repo(g, repo_name):
    """Retrieves the repository object."""
    try:
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"리포지토리를 찾을 수 없습니다: {e}")
        return None

def fetch_json_from_github(repo, file_path):
    """Fetches and parses a JSON file from the GitHub repository."""
    try:
        contents = repo.get_contents(file_path)
        return json.loads(contents.decoded_content.decode())
    except Exception as e:
        # If file doesn't exist or empty, return empty structure based on type
        if "news_data.json" in file_path:
            return {}
        elif "feeds.json" in file_path:
            return [] # List of feed URLs
        elif "stats.json" in file_path:
            return {"views": 0}
        return None

def update_file_in_github(repo, file_path, content, message):
    """Updates a file in the GitHub repository."""
    try:
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, message, json.dumps(content, indent=4, ensure_ascii=False), contents.sha)
        return True
    except Exception as e:
        # If file doesn't exist, create it (simplified for this context, ideally check existence first)
        try:
             repo.create_file(file_path, message, json.dumps(content, indent=4, ensure_ascii=False))
             return True
        except Exception as create_error:
            st.error(f"GitHub 파일 업데이트 실패: {create_error}")
            return False

# --- RSS & Analysis Data Flow ---
def get_rss_feeds(feed_urls):
    """Fetches articles from RSS feeds."""
    articles = []
    # 3 days ago timestamp
    three_days_ago = time.time() - (3 * 24 * 60 * 60)

    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Check date (published_parsed or updated_parsed)
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    published_ts = time.mktime(published)
                    if published_ts > three_days_ago:
                        articles.append({
                            'title': entry.get('title', 'No Title'),
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', '') or entry.get('description', ''),
                            'published': time.strftime('%Y-%m-%d', published)
                        })
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")
            continue
    return articles

def analyze_news(model, articles):
    """Analyzes articles using Gemini."""
    if not articles:
        return "분석할 최신 뉴스가 없습니다."

    # Prepare prompt
    prompt = """
    당신은 IT 전문 시니어 저널리스트입니다.
    아래 제공된 뉴스 기사 목록을 바탕으로 '오늘의 IT 뉴스 브리핑'을 작성해주세요.

    **작성 규칙:**
    1. **🔍 오늘의 3줄 요약**: 뉴스 전체를 관통하는 핵심 트렌드를 3가지 포인트로 요약하세요. (각 줄은 '•'로 시작)
    2. **📂 토픽별 심층 분석**: 뉴스들을 유사한 주제로 묶어 3~5개의 섹션으로 분류하세요. 
       - 각 섹션 제목은 적절한 이모지와 함께 굵게 표시하세요. (예: **🤖 생성형 AI**)
    3. **🔗 출처 표기**: 각 뉴스 내용 끝에 `[기사보기](URL)` 형식으로 링크를 거세요.
    4. **톤앤매너**: 전문적이면서도 읽기 편한 매거진 스타일의 마크다운 형식을 사용하세요. 
    5. **가독성**: 중요한 키워드는 **굵게** 표시하여 강조하세요.

    **뉴스 목록:**
    """
    for idx, article in enumerate(articles[:30]): # Sending max 30 articles to avoid token limits equivalent
        prompt += f"\n{idx+1}. 제목: {article['title']}\n   링크: {article['link']}\n   요약: {article['summary'][:200]}\n"

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini 분석 중 오류 발생: {e}"
