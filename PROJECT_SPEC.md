🚀 Antigravity AI Newsroom 프로젝트 명세서
본 프로젝트는 RSS 피드를 기반으로 IT 뉴스를 수집하고, Google Gemini API를 활용하여 날짜별 핵심 이슈를 분석/요약해주는 1인 맞춤형 AI 뉴스룸입니다. 데이터베이스 대신 GitHub 리포지토리의 JSON 파일을 저장소로 활용하며, Streamlit Cloud를 통해 배포됩니다.
1. 📌 프로젝트 개요
서비스명: Antigravity AI Newsroom
개발 환경: Python, Streamlit
핵심 기술: Google Gemini API (AI 분석), PyGithub (JSON 스토리지), Feedparser (RSS 수집)
배포 환경: Streamlit Cloud
2. ✨ 주요 기능 요구사항
2.1 메인 화면 (Newsroom)
최신 뉴스 우선: 페이지 접속 시 가장 최근에 분석된 날짜의 리포트를 메인에 출력.
날짜별 네비게이션: 사이드바의 라디오 버튼이나 셀렉트 박스를 통해 과거 날짜의 리포트를 즉시 조회 가능.
1장 보고서: Gemini AI가 생성한 마크다운 형식의 보고서를 가독성 있게 렌더링.
2.2 관리자 대시보드 (Admin Dashboard)
접근 제한: 관리자 비밀번호를 입력해야 메뉴 활성화.
RSS 관리: 분석에 사용할 RSS 피드 URL을 추가하거나 삭제 (JSON 저장).
수집 및 분석 실행:
등록된 피드들로부터 최근 3일 이내의 뉴스만 필터링하여 수집.
Gemini API를 통해 토픽별 그룹화 및 분석 수행.
분석된 결과는 news_data.json에 날짜별로 누적 저장.
접속 통계: stats.json을 활용하여 누적 방문자 수 확인.
3. 🛠 기술 스택 및 데이터 흐름
3.1 기술 스택
UI: Streamlit
AI: Google Generative AI (Gemini 1.5 Pro/Flash)
Storage: GitHub Repository (JSON files)
Libraries: feedparser, PyGithub, google-generativeai
3.2 데이터 스토리지 구조 (GitHub 내 JSON)
data/feeds.json: 구독 중인 RSS URL 리스트.
예: ["https://zdnet.co.kr/rss/all.xml", "..."]
data/news_data.json: 날짜별 AI 분석 리포트 전문.
구조: {"YYYY-MM-DD": "Markdown Content", ...}
data/stats.json: 단순 방문자 카운트.
구조: {"views": 123}
4. 🧠 AI 분석 및 리포트 가이드라인
4.1 수집 규칙
각 RSS 피드에서 항목의 날짜를 확인하여 현재 시간 기준 72시간(3일) 이내 데이터만 추출.
뉴스 제목, 본문 요약, 기사 원문 URL을 한 세트로 묶어 Gemini에게 전달.
4.2 Gemini 프롬프트 전략
역할: IT 전문 시니어 저널리스트
출력 형식:
오늘의 요약: 전체 뉴스를 아우르는 핵심 인사이트 (3줄).
토픽별 분석: 유사한 주제끼리 묶어 3~5개의 섹션으로 분류.
출처 표기: 각 뉴스 요약 끝에 [출처: 뉴스제목](URL) 링크 포함.
톤앤매너: 전문적이며 명확한 마크다운 문법 준수.
5. 📂 프로젝트 폴더 구조
my-newsroom/
├── .streamlit/
│   └── secrets.toml      # API 키 및 보안 설정 (로컬용)
├── data/                 # GitHub 저장소 내 데이터 폴더
│   ├── feeds.json
│   ├── news_data.json
│   └── stats.json
├── app.py                # 메인 UI 및 네비게이션 로직
├── utils.py              # GitHub API, RSS 파싱, Gemini 분석 로직
└── requirements.txt      # 의존성 라이브러리 목록
6. 🔐 환경 설정 (Streamlit Secrets)
배포 시 Streamlit Cloud 설정에서 아래 변수들을 반드시 입력해야 합니다.
Key	Description
GITHUB_TOKEN	GitHub Personal Access Token (repo 권한 필요)
REPO_NAME	저장소 경로 (예: username/my-newsroom-data)
GEMINI_KEY	Google AI Studio API Key
ADMIN_PASSWORD	관리자 대시보드 접속 비밀번호
7. 🚀 배포 가이드
GitHub 리포지토리에 상기 구조로 코드를 Push합니다.
data/ 폴더 내에 빈 JSON 파일들([] 또는 {})을 초기 생성하여 올립니다.
Streamlit Cloud에서 해당 리포지토리를 연결합니다.
Settings > Secrets 메뉴에서 6번 항목의 변수들을 설정합니다.
관리자 화면에서 RSS 피드를 등록하고 '수집 및 분석 시작' 버튼을 클릭하여 첫 리포트를 생성합니다.
