import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json

# ====================================================
# [필수] 구글 웹 앱 URL을 입력하세요
# ====================================================
GAS_URL = "여기에_웹앱_URL을_붙여넣으세요"

# 페이지 설정
st.set_page_config(page_title="스마트 종합 품질관리 시스템 (Smart QMS)", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 세션 초기화 (최우선 실행)
# ----------------------------------------------------
today_str = datetime.now().strftime("%Y-%m-%d")

if 'IQC' not in st.session_state:
    st.session_state.IQC = [
        {"id": "IQC-2026-001", "supplier": "(주)한국알루미늄", "itemName": "AL6061 압출재", "qty": 5000, "status": "합격", "inspectDate": today_str, "judgeDate": today_str}
    ]
if 'PQC' not in st.session_state:
    st.session_state.PQC = [
        {"id": 1, "time": "11:20:05", "line": "Line-2 (Assembly A)", "type": "중물", "val": 50.02, "pass": "True", "inspectDate": today_str}
    ]
if 'VOC' not in st.session_state:
    st.session_state.VOC = [
        {"id": "VOC-2026-001", "customer": "현대모빌리티", "itemName": "스티어링 모듈", "defectType": "유격 미세 초과", "status": "접수 완료", "inspectDate": today_str}
    ]
if 'CAPA' not in st.session_state:
    st.session_state.CAPA = [
        {"id": "CAPA-2026-012", "title": "모터 하우징 치수 이탈", "status": "조치 중", "assignee": "이보람 과장", "dueDate": "2026-08-04", "inspectDate": today_str}
    ]

# ----------------------------------------------------
# 데이터 로드 및 저장 함수
# ----------------------------------------------------
def load_data(sheet_name, default_fallback):
    if GAS_URL.startswith("http"):
        try:
            response = requests.get(f"{GAS_URL}?sheet={sheet_name}", timeout=3, allow_redirects=True)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return st.session_state.get(sheet_name, default_fallback)

def save_data(sheet_name, data_dict):
    if sheet_name not in st.session_state:
        st.session_state[sheet_name] = []
    st.session_state[sheet_name].append(data_dict)

    if GAS_URL.startswith("http"):
        try:
            payload = {"sheet": sheet_name, "data": data_dict}
            response = requests.post(GAS_URL, json=payload, timeout=3, allow_redirects=True)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("status") == "success":
                    st.toast(f"[{sheet_name}] 구글 시트 저장 성공!", icon="✅")
                    return True
        except Exception:
            st.toast(f"[{sheet_name}] 로컬 세션 저장 완료 (시트 통신 지연)", icon="ℹ️")
    return True

# ----------------------------------------------------
# Sidebar Navigation
# ----------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield--v1.png", width=50)
    st.title("SMART QMS")
    selected_menu = st.radio(
        "품질 모듈 메뉴",
        [
            "📊 통합 대시보드",
            "📦 IQC (수입/입고 검사)",
            "🔬 PQC (공정 품질)",
            "🎧 고객 품질 (VOC/RMA)",
            "📈 SPC (통계적 공정관리)",
            "🔄 CAPA (8D 개선 조치)"
        ]
    )
    st.divider()
    if GAS_URL.startswith("http"):
        st.success("🟢 구글 시트 DB 연결됨")
    else:
        st.error("🔴 웹 앱 URL 미설정 상태")

# ====================================================
# 각 메뉴별 화면 구현
# ====================================================
if selected_menu == "📊 통합 대시보드":
    st.title("📊 통합 품질 모니터링 대시보드")
    st.markdown("전체 품질 데이터와 주요 공정별 지표를 한눈에 확인할 수 있는 대시보드입니다.")
    
    iqc_data = st.session_state.IQC
    pqc_data = st.session_state.PQC
    voc_data = st.session_state.VOC
    capa_data = st.session_state.CAPA

    # 상단 요약 지표 (KPI Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 IQC 수입검사", f"{len(iqc_data)} 건")
    col2.metric("🔬 PQC 공정검사", f"{len(pqc_data)} 건")
    col3.metric("🎧 고객 VOC", f"{len(voc_data)} 건")
    col4.metric("🔄 CAPA 8D 조치", f"{len(capa_data)} 건")
    
    st.divider()

    # 그래프 영역 1: IQC 판정 상태 비율 & PQC 라인별 검사 현황
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.subheader("📦 IQC 수입검사 판정 분포")
        if iqc_data:
            df_iqc = pd.DataFrame(iqc_data)
            status_col = next((col for col in ["status", "Status", "STATUS"] if col in df_iqc.columns), None)
            
            if status_col:
                status_counts = df_iqc[status_col].value_counts().reset_index()
                status_counts.columns = ["status", "count"]
                fig_iqc = px.pie(status_counts, names="status", values="count", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_iqc, use_container_width=True)
            else:
                st.info("데이터에 상태(status) 정보가 없습니다.")
        else:
            st.info("표시할 IQC 데이터가 없습니다.")

    with g_col2:
        st.subheader("🔬 PQC 라인별 검사 건수")
        if pqc_data:
            df_pqc = pd.DataFrame(pqc_data)
            line_col = next((col for col in ["line", "Line", "LINE"] if col in df_pqc.columns), None)
            
            if line_col:
                line_counts = df_pqc[line_col].value_counts().reset_index()
                line_counts.columns = ["line", "count"]
                fig_pqc = px.bar(line_counts, x="line", y="count", color="line", text="count", color_discrete_sequence=px.colors.qualitative.Set2)
                fig_pqc.update_layout(showlegend=False)
                st.plotly_chart(fig_pqc, use_container_width=True)
            else:
                st.info("데이터에 라인(line) 정보가 없습니다.")
        else:
            st.info("표시할 PQC 데이터가 없습니다.")

    # 그래프 영역 2: CAPA 상태 및 VOC 클레임 현황
    g_col3, g_col4 = st.columns(2)

    with g_col3:
        st.subheader("🔄 CAPA 조치 상태 현황")
        if capa_data:
            df_capa = pd.DataFrame(capa_data)
            status_col_c = next((col for col in ["status", "Status", "STATUS"] if col in df_capa.columns), None)
            
            if status_col_c:
                capa_status = df_capa[status_col_c].value_counts().reset_index()
                capa_status.columns = ["status", "count"]
                fig_capa = px.bar(capa_status, x="status", y="count", color="status", text="count", color_discrete_sequence=px.colors.qualitative.Safe)
                fig_capa.update_layout(showlegend=False)
                st.plotly_chart(fig_capa, use_container_width=True)
            else:
                st.info("상태 필드가 없습니다.")
        else:
            st.info("표시할 CAPA 데이터가 없습니다.")

    with g_col4:
        st.subheader("🎧 VOC 고객사별 클레임 현황")
        if voc_data:
            df_voc = pd.DataFrame(voc_data)
            cust_col = next((col for col in ["customer", "Customer", "CUSTOMER"] if col in df_voc.columns), None)
            
            if cust_col:
                cust_counts = df_voc[cust_col].value_counts().reset_index()
                cust_counts.columns = ["customer", "count"]
                fig_voc = px.bar(cust_counts, x="customer", y="count", color="customer", text="count")
                fig_voc.update_layout(showlegend=False)
                st.plotly_chart(fig_voc, use_container_width=True)
            else:
                st.info("고객사 필드가 없습니다.")
        else:
            st.info("표시할 VOC 데이터가 없습니다.")

elif selected_menu == "📦 IQC (수입/입고 검사)":
    st.title("📦 IQC 수입/입고 품질 관리")
    
    with st.expander("➕ 신규 수입검사 등록", expanded=False):
        with st.form("iqc_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            supplier = col1.text_input("공급업체")
            item_name = col2.text_input("품목명")
            qty = col1.number_input("입고수량", value=1000)
            status = col2.selectbox("합불 판정", ["합격", "부적합", "검사대기"])
            inspect_date = col1.date_input("검사 일자")
            judge_date = col2.date_input("합불 판정 일자")
            
            if st.form_submit_button("등록 및 시트 저장"):
                if supplier and item_name:
                    new_id = f"IQC-2026-{len(st.session_state.IQC)+1:03d}"
                    new_data = {
                        "id": new_id, 
                        "supplier": supplier, 
                        "itemName": item_name, 
                        "qty": int(qty), 
                        "status": status,
                        "inspectDate": str(inspect_date),
                        "judgeDate": str(judge_date)
                    }
                    save_data("IQC", new_data)
                    st.success("IQC 항목이 성공적으로 추가되었습니다!")
                    st.rerun()
                else:
                    st.warning("공급업체와 품목명을 입력해주세요.")

    st.subheader("📋 수입 검사 대장")
    if st.session_state.IQC:
        iqc_ids = [item["id"] for item in st.session_state.IQC]
        del_col1, del_col2 = st.columns([3, 1])
        selected_iqc_id = del_col1.selectbox("삭제할 IQC ID 선택", iqc_ids, key="del_iqc_select")
        if del_col2.button("선택 IQC 삭제", type="primary"):
            st.session_state.IQC = [item for item in st.session_state.IQC if item["id"] != selected_iqc_id]
            st.success(f"항목 [{selected_iqc_id}]이(가) 삭제되었습니다.")
            st.rerun()
            
    st.dataframe(pd.DataFrame(st.session_state.IQC), use_container_width=True)

elif selected_menu == "🔬 PQC (공정 품질)":
    st.title("🔬 PQC 공정 품질 관리")
    
    col_iot, col_log = st.columns([1, 2])
    with col_iot:
        st.subheader("📡 측정 값 입력")
        line = st.selectbox("생산 라인", ["Line-1 (SMT Main)", "Line-2 (Assembly A)", "Line-3 (Packaging)"])
        test_type = st.radio("검사 구분", ["초물 검사", "중물 자주검사", "종물 검사"], horizontal=True)
        meas_val = st.number_input("측정 치수 (mm) [규격: 50.00 ± 0.10]", value=50.00, format="%.2f")
        inspect_date = st.date_input("검사 일자")

        if st.button("측정값 저장 및 전송"):
            is_pass = 49.90 <= meas_val <= 50.10
            new_data = {
                "id": len(st.session_state.PQC) + 1,
                "time": datetime.now().strftime("%H:%M:%S"),
                "line": line,
                "type": test_type,
                "val": float(meas_val),
                "pass": str(is_pass),
                "inspectDate": str(inspect_date)
            }
            save_data("PQC", new_data)
            st.success("PQC 측정값이 저장되었습니다!")
            st.rerun()

    with col_log:
        st.subheader("📜 실시간 PQC 로그")
        if st.session_state.PQC:
            pqc_ids = [item["id"] for item in st.session_state.PQC]
            del_col1, del_col2 = st.columns([3, 1])
            selected_pqc_id = del_col1.selectbox("삭제할 PQC 번호(ID) 선택", pqc_ids, key="del_pqc_select")
            if del_col2.button("선택 PQC 삭제", type="primary"):
                st.session_state.PQC = [item for item in st.session_state.PQC if item["id"] != selected_pqc_id]
                st.success(f"항목 [{selected_pqc_id}]이(가) 삭제되었습니다.")
                st.rerun()
                
        st.dataframe(pd.DataFrame(st.session_state.PQC), use_container_width=True)

elif selected_menu == "🎧 고객 품질 (VOC/RMA)":
    st.title("🎧 고객 품질 관리 (VOC / RMA)")
    
    with st.expander("➕ 신규 VOC / 고객 클레임 접수", expanded=False):
        with st.form("voc_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            cust = col1.text_input("고객사명")
            item = col2.text_input("대상 품목")
            defect = col1.text_input("불량 유형")
            inspect_date = col2.date_input("클레임 접수일자")
            
            if st.form_submit_button("클레임 접수 및 저장"):
                if cust and item:
                    new_data = {
                        "id": f"VOC-2026-{len(st.session_state.VOC)+1:03d}",
                        "customer": cust, 
                        "itemName": item, 
                        "defectType": defect, 
                        "status": "접수 완료",
                        "inspectDate": str(inspect_date)
                    }
                    save_data("VOC", new_data)
                    st.success("VOC 클레임이 접수되었습니다!")
                    st.rerun()
                else:
                    st.warning("고객사명과 대상 품목을 입력해주세요.")

    st.subheader("📋 VOC 클레임 대장")
    if st.session_state.VOC:
        voc_ids = [item["id"] for item in st.session_state.VOC]
        del_col1, del_col2 = st.columns([3, 1])
        selected_voc_id = del_col1.selectbox("삭제할 VOC ID 선택", voc_ids, key="del_voc_select")
        if del_col2.button("선택 VOC 삭제", type="primary"):
            st.session_state.VOC = [item for item in st.session_state.VOC if item["id"] != selected_voc_id]
            st.success(f"항목 [{selected_voc_id}]이(가) 삭제되었습니다.")
            st.rerun()
            
    st.dataframe(pd.DataFrame(st.session_state.VOC), use_container_width=True)

elif selected_menu == "🔄 CAPA (8D 개선 조치)":
    st.title("🔄 CAPA 시정 및 예방 조치 (8D Report)")
    
    with st.expander("➕ 신규 CAPA 8D 발행", expanded=False):
        with st.form("capa_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            title = col1.text_input("개선 조치 제목", placeholder="예: 사출 공정 버(Burr) 발생 개선")
            assignee = col2.text_input("담당자", placeholder="예: 홍길동 책임")
            status = col1.selectbox("조치 상태", ["조치 중", "검토 중", "완료", "보류"])
            inspect_date = col2.date_input("CAPA 발행일자")
            due_date = col1.date_input("완료 예정일")
            
            if st.form_submit_button("CAPA 발행 및 시트 저장"):
                if title and assignee:
                    new_data = {
                        "id": f"CAPA-2026-{len(st.session_state.CAPA)+1:03d}",
                        "title": title,
                        "status": status,
                        "assignee": assignee,
                        "inspectDate": str(inspect_date),
                        "dueDate": str(due_date)
                    }
                    save_data("CAPA", new_data)
                    st.success("CAPA 8D 항목이 발행되었습니다!")
                    st.rerun()
                else:
                    st.warning("제목과 담당자를 입력해주세요.")

    st.subheader("📋 CAPA 8D 관리 대장")
    if st.session_state.CAPA:
        capa_ids = [item["id"] for item in st.session_state.CAPA]
        del_col1, del_col2 = st.columns([3, 1])
        selected_capa_id = del_col1.selectbox("삭제할 CAPA ID 선택", capa_ids, key="del_capa_select")
        if del_col2.button("선택 CAPA 삭제", type="primary"):
            st.session_state.CAPA = [item for item in st.session_state.CAPA if item["id"] != selected_capa_id]
            st.success(f"항목 [{selected_capa_id}]이(가) 삭제되었습니다.")
            st.rerun()
            
    st.dataframe(pd.DataFrame(st.session_state.CAPA), use_container_width=True)

elif selected_menu == "📈 SPC (통계적 공정관리)":
    st.title("📈 SPC 통계적 공정 관리")
    sample_no = [f"#{i}" for i in range(1, 11)]
    measurements = [50.01, 50.03, 49.98, 50.02, 50.05, 50.04, 50.06, 50.02, 49.99, 50.01]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sample_no, y=measurements, mode='lines+markers', name='측정치 (mm)'))
    fig.add_trace(go.Scatter(x=sample_no, y=[50.10]*10, mode='lines', name='UCL', line=dict(dash='dash', color='red')))
    fig.add_trace(go.Scatter(x=sample_no, y=[49.90]*10, mode='lines', name='LSL', line=dict(dash='dash', color='red')))
    st.plotly_chart(fig, use_container_width=True)
