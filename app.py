import streamlit as st
import pandas as pd
import re

# 🔑 [보안 설정] 다른 선생님들과 공유할 사이트 비밀번호를 여기에 지정하세요!
SITE_PASSWORD = "가상실험"  # 원하는 비밀번호로 수정 가능합니다.

# 1. 웹 페이지 기본 레이아웃 세팅
st.set_page_config(
    page_title="가상실험 결과보고서 조회 시스템", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 🎨 라이트 테마 및 입력창 스타일 고정용 CSS
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    [data-testid="block-container"] {
        max-width: 1400px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 2rem !important;
    }
    [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-right: 1px solid #E2E8F0;
    }
    div[data-baseweb="select"] > div, input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #1E3A8A !important; 
        font-family: 'Malgun Gothic', sans-serif;
    }
    .student-card {
        background-color: #FFFFFF !important;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 5px solid #2563EB !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-top: 35px;
        margin-bottom: 12px;
    }
    .student-info {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }
    .custom-table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin-bottom: 30px !important;
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 6px !important;
        overflow: hidden;
    }
    .custom-table th:nth-child(1), .custom-table td.col-q {
        width: 20% !important;
        background-color: #EBF8FF !important;
        color: #1A365D !important;
        font-weight: bold !important;
        border: 1px solid #CBD5E1 !important;
        padding: 12px !important;
        text-align: left !important;
        white-space: normal !important;
    }
    .custom-table th:nth-child(2), .custom-table td.col-a {
        width: 80% !important;
        background-color: #FFFFFF !important;
        color: #334155 !important;
        border: 1px solid #CBD5E1 !important;
        padding: 12px 18px !important;
        text-align: left !important;
        white-space: normal !important; 
        display: table-cell !important;
        word-break: keep-all !important;
        line-height: 1.5 !important;
    }
    p, label, span, h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# 🔒 [보안 기능 주입] 비밀번호 인증 확인 로직
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown('<div class="main-title">🔒 가상실험 결과보고서 조회 시스템</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 비밀번호 입력 폼 생성 (글자가 마스킹 처리되어 보입니다)
    password_input = st.text_input("교사용 접속 비밀번호를 입력해 주세요:", type="password")
    
    if st.button("접속하기"):
        if password_input == SITE_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 일치하지 않습니다. 다시 확인해 주세요.")
    st.stop() # 비밀번호 통과 못 하면 아래 데이터 로드 및 본문 코드를 일절 실행하지 않고 차단

# --- 🔓 여기서부터는 비밀번호 인증 완료 시에만 작동하는 구역 🔓 ---

file_name = "가상 실험 취합 양식(응답).xlsx"

@st.cache_data
def load_and_clean_data():
    df = pd.read_excel(file_name)
    df.columns = df.columns.str.strip()
    
    STUDENT_ID_COL = '학번'
    NAME_COL = '이름'
    
    rows_to_add = []
    for idx, row in df.iterrows():
        sid_raw = str(row[STUDENT_ID_COL]).split('.')[0].strip()
        name_raw = str(row[NAME_COL]).strip()
        
        sids = re.findall(r'\d+', sid_raw)
        names = re.findall(r'[가-힣a-zA-Z]+', name_raw)
        
        if len(sids) >= 2 and len(sids) == len(names):
            for s, n in zip(sids, names):
                new_row = row.copy()
                new_row[STUDENT_ID_COL] = s
                new_row[NAME_COL] = n
                rows_to_add.append(new_row)
        else:
            row[STUDENT_ID_COL] = sid_raw
            row[NAME_COL] = name_raw
            rows_to_add.append(row)
            
    cleaned_df = pd.DataFrame(rows_to_add).reset_index(drop=True)
    
    def parse_grade(sid):
        digits = ''.join(filter(str.isdigit, str(sid)))
        return int(digits[0]) if len(digits) in [4, 5] else 99

    def parse_ban(sid):
        digits = ''.join(filter(str.isdigit, str(sid)))
        if len(digits) == 5: return int(digits[1:3])
        elif len(digits) == 4: return int(digits[1])
        return 99

    def parse_num(sid):
        digits = ''.join(filter(str.isdigit, str(sid)))
        if len(digits) == 5: return int(digits[3:])
        elif len(digits) == 4: return int(digits[2:])
        return 99

    cleaned_df['학년'] = cleaned_df[STUDENT_ID_COL].apply(parse_grade)
    cleaned_df['반'] = cleaned_df[STUDENT_ID_COL].apply(parse_ban)
    cleaned_df['번호'] = cleaned_df[STUDENT_ID_COL].apply(parse_num)
    
    return cleaned_df[cleaned_df['학년'] != 99]

try:
    df = load_and_clean_data()
except Exception as e:
    st.error(f"❌ 엑셀 파일을 읽어오지 못했습니다. 파일명이 '{file_name}'이 맞는지 확인해 주세요.")
    st.stop()

# 2. 상단 타이틀 구성
st.markdown('<div class="main-title">🔬 가상실험 결과보고서 온라인 조회 시스템</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #475569; margin-top:-8px; font-size:0.95rem;'>학년 및 반별 가상실험 결과 데이터를 실시간으로 조회하는 교사용 대시보드입니다.</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. 왼쪽 사이드바 구성
st.sidebar.markdown("<h2 style='color:#1E3A8A; font-size:1.4rem; font-weight:700; margin-top:0px;'>🔍 조회 대상 선택</h2>", unsafe_allow_html=True)

available_grades = sorted(df['학년'].unique())
selected_grade = st.sidebar.selectbox("1️⃣ 학년 선택", available_grades, format_func=lambda x: f"{x}학년")

available_bans = sorted(df[df['학년'] == selected_grade]['반'].unique())
selected_ban = st.sidebar.selectbox("2️⃣ 반 선택", available_bans, format_func=lambda x: f"{x}반")

# 4. 데이터 필터링 및 정렬
filtered_df = df[(df['학년'] == selected_grade) & (df['반'] == selected_ban)]
filtered_df = filtered_df.sort_values(by='번호')

# 5. 본문 결과 출력 영역
st.markdown(f"<h3 style='color:#2563EB; font-weight:700; font-size:1.4rem; margin-top:10px;'>📋 {selected_grade}학년 {selected_ban}반 가상실험 결과보고서</h3>", unsafe_allow_html=True)

exclude_cols = ['학번', '이름', '타임스탬프', 'timestamp', '학년', '반', '번호']
content_cols = [col for col in df.columns if col not in exclude_cols]

if filtered_df.empty:
    st.info("선택하신 학년/반에 일치하는 학생 데이터가 없습니다.")
else:
    search_query = st.text_input("🔍 학생 검색 (이름 또는 학번을 입력하세요):", "")
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['이름'].str.contains(search_query, case=False, na=False) | 
            filtered_df['학번'].str.contains(search_query, na=False)
        ]

    for idx, row in filtered_df.iterrows():
        st.markdown(f"""
            <div class="student-card">
                <span class="student-info">📌 [학번: {row['학번']}] {row['이름']} 학생</span>
            </div>
        """, unsafe_allow_html=True)
        
        html_table = '<table class="custom-table">'
        html_table += '<thead><tr><th>질문 문항</th><th>제출된 답변 내용</th></tr></thead>'
        html_table += '<tbody>'
        
        for col in content_cols:
            q_text = str(col)
            a_text = str(row.get(col, '-'))
            html_table += f'<tr><td class="col-q">{q_text}</td><td class="col-a">{a_text}</td></tr>'
            
        html_table += '</tbody></table>'
        st.markdown(html_table, unsafe_allow_html=True)