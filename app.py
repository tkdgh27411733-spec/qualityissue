import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

# Page Configuration
st.set_page_config(
    page_title="스마트 종합 품질관리 시스템 (Smart QMS)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Styling
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stAlert {
        border-radius: 10px;
    }
    .badge-pass {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }
    .badge-fail {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Session State Initialization (Data Persistence)
# ----------------------------------------------------
if 'iqc_list' not in st.session_state:
    st.session_state.iqc_list = [
        {"id": "IQC-2026-001", "supplier": "(주)한국알루미늄", "itemName": "AL6061 압출재", "qty": 5000, "coaValid": True, "status": "합격", "erpStatus": "승인"},
        {"id": "IQC-2026-002", "supplier": "대성정밀", "itemName": "베어링 하우징", "qty": 1200, "coaValid": False, "status": "부적합", "erpStatus": "동결"},
        {"id": "IQC-2026-003", "supplier": "글로벌칩스", "itemName": "MCU 칩셋 (IC)", "qty": 10000, "coaValid": True, "status": "검사대기", "erpStatus": "대기"}
    ]

if 'pqc_logs' not in st.session_state:
    st.session_state.pqc_logs = [
        {"id": 1, "time": "11:20:05", "line": "Line-2 Assembly A", "type": "중물", "val": 50.02, "pass": True},
        {"id": 2, "time": "11:05:12", "line": "Line-1 SMT Main", "type": "초물", "val": 49.98, "pass": True},
        {"id": 3, "time": "10:42:30", "line": "Line-2 Assembly A", "type": "중물", "val": 50.14, "pass": False}
    ]

if 'customer_claims' not in st.session_state:
    st.session_state.customer_claims = [
        {"id": "VOC-2026-001", "customer": "현대모빌리티", "itemName": "전동 스티어링 모듈", "lotNo": "LOT-20260729-001", "defectType": "조립 유격 미세 초과", "summary": "라인 장착 시 하우징 핏팅 이격 감지", "status": "CAPA 진행중", "capaId": "CAPA-2026-012"},
        {"id": "VOC-2026-002", "customer": "삼성글로벌", "itemName": "배터리 케이싱 A급", "lotNo": "LOT-20260729-002", "defectType": "표면 스크래치", "summary": "운송 용기 보호 필름 박리 현상", "status": "조치 완료", "capaId": "-"},
        {"id": "VOC-2026-003", "customer": "LG에너지", "itemName": "제어용 센서 커버", "lotNo": "LOT-20260729-003", "defectType": "신호 통신 오작동", "summary": "고객사 수신검사 중 커넥터 핀 휨 불량 접수", "status": "RMA 입고분석", "capaId": "-"}
    ]

if 'capa_list' not in st.session_state:
    st.session_state.capa_list = [
        {
            "id": "CAPA-2026-012",
            "title": "Line-2 모터 하우징 치수 이탈 건",
            "status": "조치 중",
            "description": "생산 공정 중 CNC 가공 치수가 LSL 미만으로 이탈하는 현상 지속 발생",
            "rootCause": "1차 원인: 바이트 금형 마모 -> 2차 원인: 절삭유 온도 상승 -> 근본원인: 교체 주기 미준수",
            "assignee": "이보람 과장 (생산기술)",
            "createdDate": "2026-07-28",
            "dueDate": "2026-08-04"
        }
    ]

if 'ai_logs' not in st.session_state:
    st.session_state.ai_logs = [
        {"id": 1, "time": "15:28:10", "line": "Line-2 Assembly A", "item": "모터 하우징", "anomalyType": "외경 치수 상한선(USL) 표류", "cause": "바이트 마모 및 절삭유 온도 상승", "causeRatio": 64, "risk": "고위험"},
        {"id": 2, "time": "14:10:05", "line": "Line-1 SMT Main", "item": "PCB 메인모듈", "anomalyType": "납땜 가공 영역 미세 브릿지", "cause": "리플로우 솔더링 노즐 오염", "causeRatio": 48, "risk": "주의"},
        {"id": 3, "time": "11:45:22", "line": "Line-3 Packaging", "item": "전동 모듈 완제품", "anomalyType": "외관 케이싱 유격 미세 감지", "cause": "조립 治具(Jig) 체결 톨러런스 변화", "causeRatio": 35, "risk": "주의"}
    ]

# ----------------------------------------------------
# Sidebar Navigation
# ----------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield--v1.png", width=50)
    st.title("SMART QMS")
    st.caption("Enterprise v5.0 | ERP/MES Live")
    st.divider()

    selected_menu = st.radio(
        "품질 모듈 메뉴",
        [
            "📊 통합 대시보드",
            "📦 IQC (수입/입고 검사)",
            "🔬 PQC (공정 품질)",
            "🎧 고객 품질 (VOC/RMA)",
            "📈 SPC (통계적 공정관리)",
            "🔄 CAPA (8D 개선 조치)",
            "🧠 AI 품질 진단 & 분석",
            "🔍 종합 이력 추적성"
        ]
    )

    st.divider()
    st.success("🟢 MES / ERP 연동 정상")
    st.info("👤 담당자: 김품질 팀장")


# ====================================================
# 1. 통합 대시보드
# ====================================================
if selected_menu == "📊 통합 대시보드":
    st.title("📊 통합 품질 모니터링 대시보드")
    st.caption("실시간 KPI 현황 및 라인별 종합 품질 분석")

    # KPI Top Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="공정 불량률 (PPM)", value="342 PPM", delta="-12.4% (전월 대비)")
    with col2:
        st.metric(label="IQC 수입검사 합격률", value="98.2 %", delta="목표치 98.0% 달성")
    with col3:
        st.metric(label="고객 품질 클레임", value=f"{len(st.session_state.customer_claims)} 건", delta="CAPA 진행중")
    with col4:
        st.metric(label="CAPA 적기 조치율", value="96.5 %", delta="+2.1% (전주 대비)")

    st.divider()

    # Chart & Alerts
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📈 월별 품질 PPM 추이 분석")
        months = ['2월', '3월', '4월', '5월', '6월', '7월']
        ppm_values = [680, 590, 520, 480, 390, 342]
        target_ppm = [500] * 6

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=ppm_values, mode='lines+markers', name='실제 PPM', line=dict(color='#4f46e5', width=3)))
        fig.add_trace(go.Scatter(x=months, y=target_ppm, mode='lines', name='목표선 (500 PPM)', line=dict(color='#ef4444', dash='dash')))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("⚠️ 실시간 라인 이상 감지")
        st.error("🚨 **Line-2 Assembly A**: 외경 치수 50.14mm (USL 50.10mm 초과)")
        st.warning("⚠️ **Line-1 SMT Main**: 납땜 가공 영역 솔더 불량 2건 연속 발생")
        
        if st.button("🚨 해당건 즉시 CAPA 8D 발행"):
            st.toast("CAPA 프로세스가 성공적으로 생성되었습니다!", icon="✅")

    # Process Status Table
    st.subheader("📋 검사 구획별 품질 종합 현황")
    summary_df = pd.DataFrame([
        {"검사 구획": "IQC (원자재 수입검사)", "총 검사 수량": f"{len(st.session_state.iqc_list)} 건", "합격": "2 건", "부적합": "1 건", "합격률": "97.8%", "상태": "정상"},
        {"검사 구획": "PQC (생산 공정품질)", "총 검사 수량": f"{len(st.session_state.pqc_logs)} 건", "합격": "2 건", "부적합": "1 건", "합격률": "97.6%", "상태": "주의 (Line-2)"},
        {"검사 구획": "고객 품질 (VOC / RMA)", "총 검사 수량": f"{len(st.session_state.customer_claims)} 건", "합격": "1 건", "부적합": "2 건", "합격률": "80.0%", "상태": "정상 접수"}
    ])
    st.dataframe(summary_df, use_container_width=True)


# ====================================================
# 2. IQC (수입/입고 검사)
# ====================================================
elif selected_menu == "📦 IQC (수입/입고 검사)":
    st.title("📦 IQC 수입/입고 품질 관리")
    st.caption("MIL-STD-105E 샘플링 수량 자동 계산 및 원자재 검사 대장")

    col_calc, col_list = st.columns([1, 2])

    with col_calc:
        st.subheader("🧮 MIL-STD-105E 샘플링 계산기")
        lot_size = st.number_input("입고 로트 크기 (Lot Size)", value=5000, step=100)
        aql = st.selectbox("합격품질수준 (AQL)", ["AQL 0.65 (중결함)", "AQL 1.0 (보통검사)", "AQL 2.5 (경결함)"])
        
        if lot_size > 3000:
            sample_n, ac, re = 200, 5, 6
        elif lot_size > 1000:
            sample_n, ac, re = 125, 3, 4
        else:
            sample_n, ac, re = 80, 2, 3

        st.info(f"""
        **추천 검사 시편 수**: `{sample_n} EA`  
        **판정 기준**: 합격(Ac) `{ac}` 이하 | 불합격(Re) `{re}` 이상
        """)

    with col_list:
        st.subheader("📋 수입 검사 대장 및 ERP 연동")
        
        # Add new item modal/expander
        with st.expander("➕ 신규 수입검사 등록"):
            with st.form("iqc_form"):
                supplier = st.text_input("공급업체")
                item_name = st.text_input("품목명")
                qty = st.number_input("입고수량", value=1000)
                coa_valid = st.checkbox("CoA 성적서 검증 완료", value=True)
                status = st.selectbox("판정", ["합격", "부적합", "검사대기"])
                
                if st.form_submit_button("등록 저장"):
                    new_id = f"IQC-2026-00{len(st.session_state.iqc_list)+1}"
                    st.session_state.iqc_list.append({
                        "id": new_id, "supplier": supplier, "itemName": item_name,
                        "qty": qty, "coaValid": coa_valid, "status": status, "erpStatus": "승인" if status == "합격" else "동결"
                    })
                    st.success("신규 IQC 항목이 추가되었습니다.")
                    st.rerun()

        df_iqc = pd.DataFrame(st.session_state.iqc_list)
        st.dataframe(df_iqc, use_container_width=True)


# ====================================================
# 3. PQC (공정 품질)
# ====================================================
elif selected_menu == "🔬 PQC (공정 품질)":
    st.title("🔬 PQC 공정 품질 관리")
    st.caption("IoT 디지매틱 계측 데이터 실시간 수집 및 공정 초/중/종물 검사")

    col_iot, col_log = st.columns([1, 2])

    with col_iot:
        st.subheader("📡 Bluetooth IoT 측정 연동")
        line = st.selectbox("생산 라인", ["Line-1 (SMT Main)", "Line-2 (Assembly A)", "Line-3 (Packaging)"])
        test_type = st.radio("검사 구분", ["초물 검사", "중물 자주검사", "종물 검사"], horizontal=True)
        
        if st.button("🔌 IoT 측정 값 가져오기"):
            st.session_state.iot_val = round(random.uniform(49.92, 50.15), 2)
            st.toast(f"IoT 데이터 수신 완료: {st.session_state.iot_val} mm")

        meas_val = st.number_input("측정 치수 (mm) [규격: 50.00 ± 0.10]", value=st.session_state.get('iot_val', 50.00), format="%.2f")

        if st.button("저장 및 자동 판정"):
            is_pass = 49.90 <= meas_val <= 50.10
            now_str = datetime.now().strftime("%H:%M:%S")
            st.session_state.pqc_logs.insert(0, {
                "id": len(st.session_state.pqc_logs) + 1,
                "time": now_str,
                "line": line,
                "type": test_type,
                "val": meas_val,
                "pass": is_pass
            })
            if is_pass:
                st.success("✅ 규격 내 합격 (OK)")
            else:
                st.error("🚨 OOS 규격 이탈 (NG)")
            st.rerun()

    with col_log:
        st.subheader("📜 실시간 PQC 검사 이력 로그")
        df_pqc = pd.DataFrame(st.session_state.pqc_logs)
        st.dataframe(df_pqc, use_container_width=True)


# ====================================================
# 4. 고객 품질 (VOC / RMA)
# ====================================================
elif selected_menu == "🎧 고객 품질 (VOC/RMA)":
    st.title("🎧 고객 품질 관리 (VOC / RMA)")
    st.caption("고객 불만 접수, 반품 분석 및 CAPA 연계 관리")

    col1, col2, col3 = st.columns(3)
    col1.metric("당월 접수 VOC", f"{len(st.session_state.customer_claims)} 건")
    col2.metric("RMA 반품 입고/분석", "1 건 (진행중)")
    col3.metric("고객 만족도 점수", "94.5 / 100점")

    st.divider()

    with st.expander("➕ 신규 VOC / 고객 클레임 접수"):
        with st.form("voc_form"):
            cust = st.text_input("고객사명")
            item = st.text_input("대상 품목")
            lot = st.text_input("Lot No.")
            defect = st.text_input("불량 유형")
            summary = st.text_area("불량 요약")
            
            if st.form_submit_button("클레임 접수"):
                st.session_state.customer_claims.append({
                    "id": f"VOC-2026-00{len(st.session_state.customer_claims)+1}",
                    "customer": cust, "itemName": item, "lotNo": lot,
                    "defectType": defect, "summary": summary, "status": "접수 완료", "capaId": "-"
                })
                st.success("VOC 접수 등록 완료")
                st.rerun()

    df_claims = pd.DataFrame(st.session_state.customer_claims)
    st.dataframe(df_claims, use_container_width=True)


# ====================================================
# 5. SPC (통계적 공정관리)
# ====================================================
elif selected_menu == "📈 SPC (통계적 공정관리)":
    st.title("📈 SPC 통계적 공정 관리")
    st.caption("X-bar R 관리도 및 Cp/Cpk 공정능력지수 실시간 측정")

    col_cpk, col_chart = st.columns([1, 2])

    with col_cpk:
        st.subheader("📐 공정능력지수 (Process Capability)")
        st.metric(label="Cp (치수 산포)", value="1.48", delta="우수 (≥1.33)")
        st.metric(label="Cpk (편향 반영)", value="1.35", delta="적합 (≥1.33)")
        
        st.warning("⚠️ **Nelson Rules 알림**: Rule 2 감지 - 연속 9개 데이터가 중심선(CL) 한쪽에 위치하여 편향 징후 발생")

    with col_chart:
        st.subheader("📉 X-bar R 관리도")
        sample_no = [f"#{i}" for i in range(1, 11)]
        measurements = [50.01, 50.03, 49.98, 50.02, 50.05, 50.04, 50.06, 50.02, 49.99, 50.01]

        fig_spc = go.Figure()
        fig_spc.add_trace(go.Scatter(x=sample_no, y=measurements, mode='lines+markers', name='측정치 (mm)', line=dict(color='#06b6d4', width=2)))
        fig_spc.add_trace(go.Scatter(x=sample_no, y=[50.10]*10, mode='lines', name='UCL (50.10)', line=dict(color='#ef4444', dash='dash')))
        fig_spc.add_trace(go.Scatter(x=sample_no, y=[50.00]*10, mode='lines', name='CL (50.00)', line=dict(color='#10b981')))
        fig_spc.add_trace(go.Scatter(x=sample_no, y=[49.90]*10, mode='lines', name='LSL (49.90)', line=dict(color='#ef4444', dash='dash')))
        fig_spc.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_spc, use_container_width=True)


# ====================================================
# 6. CAPA (8D 개선 조치)
# ====================================================
elif selected_menu == "🔄 CAPA (8D 개선 조치)":
    st.title("🔄 CAPA 시정 및 예방 조치 (8D Report)")
    st.caption("근본 원인 분석(5-Why) 및 시정/예방 조치 유효성 검증")

    if st.button("➕ 신규 CAPA 8D 발행"):
        st.session_state.capa_list.append({
            "id": f"CAPA-2026-01{len(st.session_state.capa_list)+3}",
            "title": "Line-1 SMT 납땜 미세 브릿지 개선건",
            "status": "조치 중",
            "description": "리플로우 솔더링 후 잔여 플럭스 오염으로 인한 미세 쇼트 발생",
            "rootCause": "노즐 세척 주기 지연 및 노후화",
            "assignee": "김기술 과장",
            "createdDate": datetime.now().strftime("%Y-%m-%d"),
            "dueDate": "2026-08-10"
        })
        st.success("신규 CAPA 발행 완료")
        st.rerun()

    for capa in st.session_state.capa_list:
        with st.container():
            st.markdown(f"### 📌 [{capa['id']}] {capa['title']} (`{capa['status']}`)")
            st.write(f"**담당자:** {capa['assignee']} | **완료 예정일:** {capa['dueDate']}")
            st.info(f"**문제 요약:** {capa['description']}\n\n**근본 원인 (Root Cause):** {capa['rootCause']}")
            st.divider()


# ====================================================
# 7. AI 품질 진단 & 분석
# ====================================================
elif selected_menu == "🧠 AI 품질 진단 & 분석":
    st.title("🧠 AI 실시간 불량 예지 및 근본 원인(Root Cause) 진단")
    st.caption("XGBoost 및 SHAP 변수 기여도 분석 기반 AI 이상징후 탐지")

    if st.button("✨ AI 이상징후 심층 진단 실행"):
        with st.spinner("AI 엔진이 센서 데이터 및 비전 영상 요인을 분석 중입니다..."):
            import time
            time.sleep(1)
            st.success("진단 완료: 위험지수 84.2% 감지됨")

    col_chart, col_vision = st.columns([2, 1])

    with col_chart:
        st.subheader("📊 AI 원인 인자별 기여도 (SHAP Value)")
        factors = ['CNC 바이트 마모', '절삭유 온도변화', '공구 진동', '원자재 경도 차이', '작업자 교대 이격']
        scores = [64, 22, 18, 12, 5]

        fig_ai = px.bar(x=scores, y=factors, orientation='h', labels={'x': '기여도 (%)', 'y': '공정 인자'},
                        color=scores, color_continuous_scale='Reds')
        fig_ai.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_ai, use_container_width=True)

    with col_vision:
        st.subheader("📷 AI 비전 검사 이미지 분석")
        st.image("https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=500&auto=format&fit=crop&q=60", caption="Line-2 모터 하우징 AI 스캔 - Defect 94% 감지")

    st.subheader("📋 AI 진단 로그")
    st.dataframe(pd.DataFrame(st.session_state.ai_logs), use_container_width=True)


# ====================================================
# 8. 종합 이력 추적성 (Traceability)
# ====================================================
elif selected_menu == "🔍 종합 이력 추적성":
    st.title("🔍 종합 이력 추적성 (Traceability)")
    st.caption("원자재 Lot부터 공정 검사, 출하 완제품 및 VOC 이력 단 10초 추적")

    search_lot = st.text_input("추적할 완제품 Lot No. 또는 Serial 번호 입력", value="LOT-20260729-001")

    if search_lot:
        st.subheader(f"🚩 추적 결과: `{search_lot}`")

        with st.status("종합 이력 추적 완료", expanded=True):
            st.write("📦 **1단계 [원자재 IQC]**: AL6061 압출재 (Lot: MAT-2026-088) | 공급사: (주)한국알루미늄 | **합격**")
            st.write("⚙️ **2단계 [생산 PQC]**: Line-2 Assembly A 모터 하우징 가공 | 측정치: 50.02mm (정상) | 작업자: 박기술 선임")
            st.write("🚚 **3단계 [고객 VOC/출하]**: 현대모빌리티 인천공장 납품 | 성적서: COA-2026-0789")
