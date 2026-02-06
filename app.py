import streamlit as st
import datetime
import utils
from markdown_it import MarkdownIt

# --- Page Config ---
st.set_page_config(
    page_title="Antigravity AI Newsroom",
    page_icon="📰",
    layout="wide"
)

# --- Load Secrets ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["REPO_NAME"]
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except Exception as e:
    st.error(f"Secret 설정이 누락되었습니다: {e}")
    st.stop()

# --- Initialization ---
g = utils.init_github(GITHUB_TOKEN)
repo = utils.get_repo(g, REPO_NAME)
model = utils.init_gemini(GEMINI_KEY)

if not repo:
    st.stop()

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* Ensure Streamlit widgets don't get messed up */
    .stSelectbox div[data-baseweb="select"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    .news-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e1e1e;
        margin-bottom: 0.5rem;
    }
    
    .date-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .summary-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar & Navigation ---
st.sidebar.title("AI Newsroom 📰")
page = st.sidebar.radio("메뉴", ["오늘의 뉴스", "지난 뉴스", "관리자 대시보드"])

# Load Data
news_data = utils.fetch_json_from_github(repo, "data/news_data.json") or {}
stats_data = utils.fetch_json_from_github(repo, "data/stats.json") or {"views": 0}

# Update Stats (Simple View Counter) - Only on main view
if page == "오늘의 뉴스":
    stats_data['views'] = stats_data.get('views', 0) + 1
    # Note: Calling update on every refresh might be too much for GitHub API limit. 
    # In a real app, optimize this (e.g., update daily or locally first).
    # utils.update_file_in_github(repo, "data/stats.json", stats_data, "Update view count") 
    # For now, we visualize it but maybe don't write back every single time to avoid rate limits in this demo.
    pass

# --- 1. 오늘의 뉴스 (Latest) ---
if page == "오늘의 뉴스":
    # Header Section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">AI Daily News</div>', unsafe_allow_html=True)
        st.caption("매일 아침 배달되는 인공지능 트렌드 브리핑")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2965/2965879.png", width=60) # Simple icon
    
    # Get latest date
    sorted_dates = sorted(news_data.keys(), reverse=True)
    
    if sorted_dates:
        latest_date = sorted_dates[0]
        
        # Content Display
        # Render Markdown to HTML to put it inside the styled div
        md = MarkdownIt()
        html_content = md.render(news_data[latest_date])
        
        full_html = f"""
        <div class="news-card">
            <div style="text-align:right; margin-bottom:10px;">
                <span class="date-badge">📅 {latest_date}</span>
            </div>
            {html_content}
        </div>"""
        st.markdown(full_html, unsafe_allow_html=True)
            
    else:
        st.info("아직 분석된 뉴스 리포트가 없습니다. 관리자 대시보드에서 분석을 시작해주세요.")

# --- 2. 지난 뉴스 (History) ---
elif page == "지난 뉴스":
    st.title("🗄️ 지난 뉴스 아카이브")
    
    sorted_dates = sorted(news_data.keys(), reverse=True)
    if sorted_dates:
        selected_date = st.selectbox("날짜 선택", sorted_dates)
        if selected_date:
            with st.container():
                # Render Markdown to HTML to put it inside the styled div
                md = MarkdownIt()
                html_content = md.render(news_data[selected_date])
                
                # Combine into one HTML block to prevent Streamlit from closing div early
                full_html = f"""
                <div class="news-card">
                    <div style="text-align:right; margin-bottom:10px;">
                        <span class="date-badge">📅 {selected_date}</span>
                    </div>
                    {html_content}
                </div>"""
                st.markdown(full_html, unsafe_allow_html=True)
    else:
        st.info("저장된 뉴스 리포트가 없습니다.")

# --- 3. 관리자 대시보드 (Admin) ---
elif page == "관리자 대시보드":
    st.title("⚙️ 관리자 대시보드")
    
    password = st.text_input("비밀번호", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("접속 성공")
        
        # 1. RSS Feed Management
        st.subheader("📡 RSS 피드 관리")
        feeds = utils.fetch_json_from_github(repo, "data/feeds.json")
        if feeds is None: feeds = []
        
        # Add new feed
        new_feed = st.text_input("새 RSS URL 추가")
        if st.button("추가"):
            if new_feed and new_feed not in feeds:
                feeds.append(new_feed)
                utils.update_file_in_github(repo, "data/feeds.json", feeds, "Add new RSS feed")
                st.rerun()
                
        # List feeds
        st.write("등록된 피드 목록:")
        for f in feeds:
            st.code(f)
            
        st.markdown("---")
        
        # 2. Manual Trigger
        st.subheader("🤖 AI 뉴스 분석 실행")
        if st.button("지금 분석 시작 (Start Analysis)"):
            with st.spinner("뉴스 수집 및 AI 분석 중... (약 1~2분 소요)"):
                # 1. Get Articles
                articles = utils.get_rss_feeds(feeds)
                st.write(f"수집된 최근 뉴스: {len(articles)}건")
                
                # 2. Analyze
                if articles:
                    report = utils.analyze_news(model, articles)
                    
                    # 3. Save to GitHub
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    news_data[today_str] = report
                    
                    success = utils.update_file_in_github(repo, "data/news_data.json", news_data, f"Update report for {today_str}")
                    
                    if success:
                        st.success(f"{today_str} 리포트 생성 및 저장 완료!")
                    else:
                        st.error("저장 실패")
                else:
                    st.warning("최근 3일 이내의 뉴스가 없습니다.")
                    
        st.markdown("---")
        st.subheader("📊 접속 통계")
        st.metric("총 방문자 수", stats_data.get('views', 0))
        
    elif password:
        st.error("비밀번호가 일치하지 않습니다.")
