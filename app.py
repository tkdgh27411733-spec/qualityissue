import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import requests
import json

# ====================================================
# DB 연결 설정 (Google Apps Script Web App URL)
# ====================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbxEq6hv3Z4pZcUS_NtD_TYsICOtRTJVQrL_0b-OYVFeu3NqzhyU6iOThrhViTkZkKVUcw/exec"

# 페이지 기본 설정
st.set_page_config(page_title="스마트 종합 품질관리 시스템 (Smart QMS)", page_icon="🛡️", layout="wide")

# CSS
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# DB 연동 및 Session State 초기화 함수 (오류 방지 핵심)
# ----------------------------------------------------
def init_data(sheet_name, default_data):
    """DB에서 데이터를 가져오되, 실패시 로컬(세션) 데이터를 유지하는 함수"""
    if sheet_name not in st.session_state:
        st.session_state[sheet_name] = default_data

    # GAS_URL이 제대로 입력된 경우에만 통신 시도
    if GAS_URL.startswith("http"):
        try:
            response = requests.get(f"{GAS_URL}?sheet={sheet_name}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data: # 데이터가 있으면 덮어쓰기
                    st.session_state[sheet_name] = data
        except Exception as e:
            st.sidebar.warning(f"{sheet_name} DB 연결 실패. 로컬 모드로 작동합니다.")

def append_data(sheet_name, data_dict):
    """로컬 세션에 먼저 저장하여 UI를 즉시 갱신하고 백그라운드로 DB에 전송"""
    # 1. 로컬 세션에 즉시 반영 (앱이 멈추지 않고 무조건 기능하도록 함)
    st.session_state[sheet_name].append(data_dict)
    
    # 2. 구글 시트로 POST 전송
    if GAS_URL.startswith("http"):
        try:
            payload = {"sheet": sheet_name, "data": data_dict}
            response = requests.post(GAS_URL, json=payload, timeout=3)
            if response.status_code == 200 and response.json().get("status") == "success":
                st.toast(f"{sheet_name} DB 저장 완료!", icon="✅")
                return True
            else:
                st.error("DB 연동 오류: 권한 설정(모든 사용자)을 확인하세요.")
        except Exception as e:
            st.error(f"서버 통신 실패: {e}")
    return False

# 기본 Mockup 데이터 설정 (DB가 텅 비어있을 때 앱이 고장나는 것 방지)
init_data("IQC", [{"id": "IQC-001", "supplier": "샘플업체", "itemName": "샘플품목", "qty": 100, "status": "합격"}])
init_data("PQC", [{"id": 1, "time": "12:00", "line": "Line-1", "type": "초물", "val": 50.0, "pass": True}])
init_data("VOC", [{"id": "VOC-001", "customer": "샘플고객", "itemName": "제품A", "defectType": "스크래치", "status": "접수"}])
init_data("CAPA", [{"id": "CAPA-001", "title": "샘플 불량 개선", "status": "조치 중", "assignee": "홍길동", "dueDate": "2026-08-01"}])


# ----------------------------------------------------
# Sidebar Navigation
# ----------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield--v1.png", width=50)
    st.title("SMART QMS")
    selected_menu = st.radio("품질 모듈 메뉴", ["📊 통합 대시보드", "📦 IQC (수입/입고 검사)", "🔬 PQC (공정 품질)", "🎧 고객 품질 (VOC/RMA)", "📈 SPC (통계적 공정관리)", "🔄 CAPA (8D 개선 조치)"])
    st.divider()
    if GAS_URL.startswith("http"):
        st.success("🟢 클라우드 DB 연동 활성화")
    else:
        st.warning("🟡 로컬 메모리 모드 (DB 미설정)")

# ====================================================
# 각 메뉴 화면
# ====================================================
if selected_menu == "📊 통합 대시보드":
    st.title("📊 통합 품질 모니터링 대시보드")
    col1, col2, col3 = st.columns(3)
    col1.metric("IQC 누적 검사", f"{len(st.session_state['IQC'])} 건")
    col2.metric("PQC 실시간 공정", f"{len(st.session_state['PQC'])} 건")
    col3.metric("고객 품질 클레임", f"{len(st.session_state['VOC'])} 건")
    
    st.subheader("📋 검사 구획별 전체 데이터 미리보기")
    st.write("IQC 데이터")
    st.dataframe(pd.DataFrame(st.session_state["IQC"]), use_container_width=True)

elif selected_menu == "📦 IQC (수입/입고 검사)":
    st.title("📦 IQC 수입/입고 품질 관리")
    
    with st.expander("➕ 신규 수입검사 등록 (여기를 열어 추가하세요)", expanded=True):
        with st.form("iqc_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            supplier = col1.text_input("공급업체", placeholder="(주)한국알루미늄")
            item_name = col2.text_input("품목명", placeholder="AL6061 압출재")
            qty = col1.number_input("입고수량", value=1000)
            status = col2.selectbox("판정 결과", ["합격", "부적합", "검사대기"])
            
            if st.form_submit_button("신규 등록 저장"):
                if supplier and item_name:
                    new_id = f"IQC-{datetime.now().strftime('%y%m')}-{len(st.session_state['IQC'])+1:03d}"
                    new_data = {"id": new_id, "supplier": supplier, "itemName": item_name, "qty": qty, "status": status}
                    append_data("IQC", new_data)
                    st.rerun()
                else:
                    st.warning("공급업체와 품목명을 입력해주세요.")

    st.subheader("📋 수입 검사 리스트")
    st.dataframe(pd.DataFrame(st.session_state["IQC"]), use_container_width=True)

elif selected_menu == "🔬 PQC (공정 품질)":
    st.title("🔬 PQC 공정 품질 관리")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📡 측정 값 입력")
        line = st.selectbox("생산 라인", ["Line-1", "Line-2", "Line-3"])
        test_type = st.radio("검사 구분", ["초물", "중물", "종물"], horizontal=True)
        meas_val = st.number_input("측정 치수 (mm) [규격: 50.00 ± 0.10]", value=50.00, format="%.2f")

        if st.button("측정값 저장"):
            is_pass = 49.90 <= meas_val <= 50.10
            new_data = {
                "id": len(st.session_state["PQC"]) + 1,
                "time": datetime.now().strftime("%H:%M:%S"),
                "line": line,
                "type": test_type,
                "val": meas_val,
                "pass": is_pass
            }
            append_data("PQC", new_data)
            st.rerun()

    with col2:
        st.subheader("📜 실시간 검사 로그")
        st.dataframe(pd.DataFrame(st.session_state["PQC"]), use_container_width=True)

elif selected_menu == "🎧 고객 품질 (VOC/RMA)":
    st.title("🎧 고객 품질 관리 (VOC / RMA)")
    
    with st.expander("➕ 고객 클레임 접수", expanded=True):
        with st.form("voc_form", clear_on_submit=True):
            cust = st.text_input("고객사명")
            item = st.text_input("대상 품목")
            defect = st.text_input("불량 유형")
            if st.form_submit_button("클레임 등록"):
                new_data = {
                    "id": f"VOC-{datetime.now().strftime('%y%m')}-{len(st.session_state['VOC'])+1:03d}",
                    "customer": cust, "itemName": item, "defectType": defect, "status": "접수 완료"
                }
                append_data("VOC", new_data)
                st.rerun()

    st.dataframe(pd.DataFrame(st.session_state["VOC"]), use_container_width=True)

elif selected_menu == "🔄 CAPA (8D 개선 조치)":
    st.title("🔄 CAPA 시정 및 예방 조치")
    
    if st.button("➕ 신규 CAPA 발행"):
        new_data = {
            "id": f"CAPA-{datetime.now().strftime('%y%m')}-{len(st.session_state['CAPA'])+1:03d}",
            "title": "공정 불량 개선 조치",
            "status": "조치 중",
            "assignee": "담당자 미정",
            "dueDate": datetime.now().strftime("%Y-%m-%d")
        }
        append_data("CAPA", new_data)
        st.rerun()

    st.dataframe(pd.DataFrame(st.session_state["CAPA"]), use_container_width=True)
    
elif selected_menu == "📈 SPC (통계적 공정관리)":
    st.title("📈 SPC 통계적 공정 관리")
    sample_no = [f"#{i}" for i in range(1, 11)]
    measurements = [50.01, 50.03, 49.98, 50.02, 50.05, 50.04, 50.06, 50.02, 49.99, 50.01]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sample_no, y=measurements, mode='lines+markers', name='측정치'))
    fig.add_trace(go.Scatter(x=sample_no, y=[50.10]*10, mode='lines', line=dict(dash='dash', color='red'), name='UCL (50.10)'))
    fig.add_trace(go.Scatter(x=sample_no, y=[49.90]*10, mode='lines', line=dict(dash='dash', color='red'), name='LSL (49.90)'))
    st.plotly_chart(fig, use_container_width=True)
