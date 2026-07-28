import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os

# Page Configuration
st.set_page_config(
    page_title="스마트 품질관리 시스템 (QMS)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "qms_defects_data.csv"

def get_initial_sample_data():
    today = date.today()
    return pd.DataFrame([
        {
            "관리번호": "Q2026-001",
            "발생일자": today - timedelta(days=1),
            "불량구분": "공정불량",
            "품목명": "메인 PCB 어셈블리",
            "LotNo": "LOT-260727-A1",
            "불량현상": "납땜 불량/미납",
            "불량수량": 24,
            "담당부서": "SMT 공정1팀",
            "심각도": "상",
            "손실비용": 45,
            "품질담당자": "김철수",
            "진행상태": "원인분석",
            "상세내용": "납땜 웨이브 솔더 온도 불균일로 인한 패턴 미납 발생",
            "근본원인": "솔더링 오븐 3번 챔버 히터 출력 저하",
            "재발방지대책": "히터 센서 교체 및 일일 온도 프로파일 전수 점검",
            "조치담당자": "이기술",
            "완료예정일": today + timedelta(days=2)
        },
        {
            "관리번호": "Q2026-002",
            "발생일자": today - timedelta(days=2),
            "불량구분": "입고불량",
            "품목명": "알루미늄 케이스 커버",
            "LotNo": "LOT-260725-C",
            "불량현상": "외관 스크래치/찍힘",
            "불량수량": 120,
            "담당부서": "협력사 (성진공업)",
            "심각도": "중",
            "손실비용": 30,
            "품질담당자": "박영희",
            "진행상태": "개선조치",
            "상세내용": "운송 패키징 적재 과정에서 치구 상호 간섭으로 스크래치 다량 발생",
            "근본원인": "포장 완충재 재질 부적합 및 트레이 유격",
            "재발방지대책": "EVA 폼 전용 트레이 변경 및 포장 사양서 개정",
            "조치담당자": "박영희",
            "완료예정일": today + timedelta(days=1)
        },
        {
            "관리번호": "Q2026-003",
            "발생일자": today - timedelta(days=4),
            "불량구분": "고객불량",
            "품목명": "전원 공급 모듈 500W",
            "LotNo": "LOT-260720-P",
            "불량현상": "전원 작동 불량",
            "불량수량": 5,
            "담당부서": "품질보증팀",
            "심각도": "상",
            "손실비용": 150,
            "품질담당자": "정민우",
            "진행상태": "효과검증",
            "상세내용": "고객사 라인 투입 중 초기 전원 On 시 FET 소자 파손 보고",
            "근본원인": "서지 압력 방지 다이오드 스펙 오적용",
            "재발방지대책": "부품 스펙 변경 승인 및 반품품 전수 재작업 진행",
            "조치담당자": "정민우",
            "완료예정일": today - timedelta(days=1)
        },
        {
            "관리번호": "Q2026-004",
            "발생일자": today - timedelta(days=6),
            "불량구분": "공정불량",
            "품목명": "커넥터 하우징",
            "LotNo": "LOT-260721-H",
            "불량현상": "치수 오차 초과",
            "불량수량": 85,
            "담당부서": "사출 3팀",
            "심각도": "중",
            "손실비용": 18,
            "품질담당자": "김철수",
            "진행상태": "조치완료",
            "상세내용": "금형 수축률 계산 오류로 내경 치수 +0.12mm 초과",
            "근본원인": "금형 냉각수 유량 감소로 성형 온도 상승",
            "재발방지대책": "금형 세척 및 냉각 라인 밸브 교체 완료",
            "조치담당자": "최설비",
            "완료예정일": today - timedelta(days=2)
        },
        {
            "관리번호": "Q2026-005",
            "발생일자": today - timedelta(days=8),
            "불량구분": "입고불량",
            "품목명": "칩 저항 10k ohm",
            "LotNo": "LOT-260718-R",
            "불량현상": "부품 누락/오실장",
            "불량수량": 500,
            "담당부서": "협력사 (전산전자)",
            "심각도": "하",
            "손실비용": 10,
            "품질담당자": "박영희",
            "진행상태": "대책수립",
            "상세내용": "릴 포장 라벨 표시 값과 실제 부품 저항값 상이",
            "근본원인": "공급사 출하 검사 시 라벨링 바코드 혼용",
            "재발방지대책": "공급사 수입검사 강화 및 수입검사 샘플링 수율 증대",
            "조치담당자": "박영희",
            "완료예정일": today + timedelta(days=3)
        },
        {
            "관리번호": "Q2026-006",
            "발생일자": today,
            "불량구분": "공정불량",
            "품목명": "스마트 센서 모듈",
            "LotNo": "LOT-260728-S",
            "불량현상": "전원 작동 불량",
            "불량수량": 12,
            "담당부서": "조립 2팀",
            "심각도": "상",
            "손실비용": 60,
            "품질담당자": "강동원",
            "진행상태": "접수",
            "상세내용": "최종 핑거 테스트 중 통신 응답 없음 현상 발생",
            "근본원인": "",
            "재발방지대책": "",
            "조치담당자": "강동원",
            "완료예정일": today + timedelta(days=5)
        }
    ])

def load_data():
    if "defects_df" in st.session_state:
        return st.session_state["defects_df"]
    
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['발생일자'] = pd.to_datetime(df['발생일자']).dt.date
            if '완료예정일' in df.columns:
                df['완료예정일'] = pd.to_datetime(df['완료예정일']).dt.date
            st.session_state["defects_df"] = df
            return df
        except Exception as e:
            st.error(f"데이터 파일 로드 중 오류 발생: {e}")

    df = get_initial_sample_data()
    st.session_state["defects_df"] = df
    save_data(df)
    return df

def save_data(df):
    st.session_state["defects_df"] = df
    try:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    except Exception as e:
        st.warning(f"로컬 파일 저장 실패 (세션 데이터는 유지됩니다): {e}")

def render_sidebar(df):
    st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.sidebar.title("스마트 품질관리 System")
    st.sidebar.caption("Quality Management System")
    st.sidebar.markdown("---")

    # Main Navigation Menu
    menu = st.sidebar.radio(
        "📌 메인 메뉴",
        ["종합 대시보드", "불량 등록 및 대장", "개선 진행상황 (CAPA)"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 통합 조건 필터")

    # Date Range Filter
    today = date.today()
    default_start = today - timedelta(days=30)
    
    # Preset date buttons
    col_preset1, col_preset2 = st.sidebar.columns(2)
    with col_preset1:
        if st.button("📅 이번달", use_container_width=True):
            st.session_state['start_date_val'] = date(today.year, today.month, 1)
            st.session_state['end_date_val'] = today
    with col_preset2:
        if st.button("📅 전체기간", use_container_width=True):
            st.session_state['start_date_val'] = date(2025, 1, 1)
            st.session_state['end_date_val'] = today + timedelta(days=365)

    start_date_default = st.session_state.get('start_date_val', default_start)
    end_date_default = st.session_state.get('end_date_val', today)

    start_date = st.sidebar.date_input("시작일자", start_date_default)
    end_date = st.sidebar.date_input("종료일자", end_date_default)

    # Defect Type Filter
    defect_types = ["전체", "입고불량", "공정불량", "고객불량"]
    selected_type = st.sidebar.selectbox("불량 구분 선택", defect_types, index=0)

    # Apply Filters
    filtered_df = df.copy()
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['발생일자'] >= start_date) & (filtered_df['발생일자'] <= end_date)]
    if selected_type != "전체":
        filtered_df = filtered_df[filtered_df['불량구분'] == selected_type]

    st.sidebar.markdown("---")
    # Quick Badges Stats
    st.sidebar.caption("📊 유형별 누적 건수")
    st.sidebar.text(f"• 입고불량 (IQC): {len(df[df['불량구분']=='입고불량'])} 건")
    st.sidebar.text(f"• 공정불량 (IPQC): {len(df[df['불량구분']=='공정불량'])} 건")
    st.sidebar.text(f"• 고객불량 (CQA): {len(df[df['불량구분']=='고객불량'])} 건")

    if st.sidebar.button("🔄 샘플 데이터 초기화", help="초기 데이터로 복원합니다."):
        df = get_initial_sample_data()
        save_data(df)
        st.sidebar.success("데이터가 초기화되었습니다.")
        st.rerun()

    return menu, filtered_df

def render_dashboard(df):
    st.title("📊 품질 종합 대시보드")
    st.caption("선택된 기간 및 불량 유형 조건에 따른 주요 품질 지표 및 진행 현황입니다.")

    # KPI Metrics
    total_count = len(df)
    total_qty = df['불량수량'].sum() if total_count > 0 else 0
    closed_count = len(df[df['진행상태'] == '조치완료'])
    in_progress_count = total_count - closed_count
    completion_rate = round((closed_count / total_count * 100), 1) if total_count > 0 else 0.0
    total_cost = df['손실비용'].sum() if total_count > 0 else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("전체 불량 건수", f"{total_count:,} 건")
    kpi2.metric("총 불량 수량", f"{total_qty:,} EA")
    kpi3.metric("개선 완료율", f"{completion_rate}%", delta=f"{closed_count}건 완료")
    kpi4.metric("조치 진행 중", f"{in_progress_count:,} 건")
    kpi5.metric("추정 손실 금액", f"{total_cost:,} 만원")

    st.markdown("---")

    # Charts Row 1
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("📈 일자별 불량 발생 추이")
        if not df.empty:
            daily_df = df.groupby('발생일자').size().reset_index(name='건수')
            daily_df['발생일자'] = pd.to_datetime(daily_df['발생일자'])
            fig_daily = px.line(
                daily_df, x='발생일자', y='건수',
                markers=True, text='건수',
                title="일자별 발생 건수",
                color_discrete_sequence=['#2563eb']
            )
            fig_daily.update_traces(textposition="top center")
            fig_daily.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("조회 조건에 맞는 데이터가 없습니다.")

    with col_chart2:
        st.subheader("🍩 불량 유형별 비중")
        if not df.empty:
            type_df = df.groupby('불량구분').size().reset_index(name='건수')
            fig_type = px.pie(
                type_df, values='건수', names='불량구분',
                hole=0.5,
                color='불량구분',
                color_discrete_map={'입고불량':'#10b981', '공정불량':'#f59e0b', '고객불량':'#f43f5e'}
            )
            fig_type.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig_type, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # Charts Row 2
    col_chart3, col_chart4 = st.columns([1, 2])

    with col_chart3:
        st.subheader("📊 CAPA 진행 단계별 현황")
        stages = ['접수', '원인분석', '대책수립', '개선조치', '효과검증', '조치완료']
        stage_counts = [len(df[df['진행상태'] == s]) for s in stages]
        stage_df = pd.DataFrame({'단계': stages, '건수': stage_counts})

        fig_stage = px.bar(
            stage_df, x='단계', y='건수', text='건수',
            color='단계',
            color_discrete_sequence=['#64748b', '#6366f1', '#3b82f6', '#f59e0b', '#a855f7', '#10b981']
        )
        fig_stage.update_traces(textposition='outside')
        fig_stage.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10), height=300)
        st.plotly_chart(fig_stage, use_container_width=True)

    with col_chart4:
        st.subheader("⚠️ 주요 불량 현상 TOP 5")
        if not df.empty:
            cause_df = df['불량현상'].value_counts().head(5).reset_index()
            cause_df.columns = ['불량현상', '건수']
            fig_cause = px.bar(
                cause_df, y='불량현상', x='건수', text='건수',
                orientation='h',
                color_discrete_sequence=['#1e293b']
            )
            fig_cause.update_traces(textposition='outside')
            fig_cause.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=30, b=10), height=300)
            st.plotly_chart(fig_cause, use_container_width=True)

    # Recent Unresolved Items Table
    st.markdown("---")
    st.subheader("🚨 주요 미완료 개선 필요 항목")
    unresolved_df = df[df['진행상태'] != '조치완료']
    if not unresolved_df.empty:
        st.dataframe(
            unresolved_df[['관리번호', '발생일자', '불량구분', '품목명', '불량현상', '불량수량', '심각도', '진행상태', '품질담당자']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 현재 미완료된 불량 항목이 없습니다!")

def render_defect_list(df, full_df):
    st.title("📝 불량 등록 및 대장")
    st.caption("신규 불량을 등록하거나 기존 등록 내역을 조회/수정/삭제합니다.")

    # Expander for Defect Registration Form
    with st.expander("➕ 신규 불량 등록 Form 열기", expanded=False):
        with st.form("add_defect_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_date = st.date_input("발생일자 *", date.today())
                f_type = st.selectbox("불량구분 *", ["공정불량", "입고불량", "고객불량"])
                f_item = st.text_input("품목명 *", placeholder="예: 메인 PCB 어셈블리")
            with c2:
                f_lot = st.text_input("Lot 번호", placeholder="예: LOT-20260728-01")
                f_phenomenon = st.selectbox("불량현상 *", [
                    "납땜 불량/미납", "치수 오차 초과", "외관 스크래치/찍힘",
                    "전원 작동 불량", "부품 누락/오실장", "기타 품질 문제"
                ])
                f_qty = st.number_input("불량수량 (EA) *", min_value=1, value=1)
            with c3:
                f_dept = st.text_input("담당/원인 부서", placeholder="예: SMT 1팀 / A부품사")
                f_severity = st.selectbox("심각도", ["상", "중", "하"], index=1)
                f_cost = st.number_input("추정 손실비용 (만원)", min_value=0, value=10)

            c4, c5 = st.columns(2)
            with c4:
                f_owner = st.text_input("품질 담당자", value="김품질")
            with c5:
                f_desc = st.text_area("상세 불량 내용", placeholder="발생 경위 및 초기 관찰 상태", height=68)

            submit_btn = st.form_submit_button("💾 불량 신규 등록하기", use_container_width=True)

            if submit_btn:
                if not f_item:
                    st.error("품목명을 입력해 주세요.")
                else:
                    new_id = f"Q{date.today().year}-{len(full_df)+1:03d}"
                    new_row = {
                        "관리번호": new_id,
                        "발생일자": f_date,
                        "불량구분": f_type,
                        "품목명": f_item,
                        "LotNo": f_lot,
                        "불량현상": f_phenomenon,
                        "불량수량": f_qty,
                        "담당부서": f_dept,
                        "심각도": f_severity,
                        "손실비용": f_cost,
                        "품질담당자": f_owner,
                        "진행상태": "접수",
                        "상세내용": f_desc,
                        "근본원인": "",
                        "재발방지대책": "",
                        "조치담당자": f_owner,
                        "완료예정일": f_date + timedelta(days=7)
                    }
                    updated_df = pd.concat([pd.DataFrame([new_row]), full_df], ignore_index=True)
                    save_data(updated_df)
                    st.success(f"신규 불량건[{new_id}]이 성공적으로 등록되었습니다!")
                    st.rerun()

    st.markdown("---")

    # Search & Filter
    search_term = st.text_input("🔎 대장 검색 (품목명, 관리번호, 불량현상, 담당자 키워드 검색)", "")
    
    display_df = df.copy()
    if search_term:
        mask = (
            display_df['품목명'].str.contains(search_term, case=False, na=False) |
            display_df['관리번호'].str.contains(search_term, case=False, na=False) |
            display_df['불량현상'].str.contains(search_term, case=False, na=False) |
            display_df['품질담당자'].str.contains(search_term, case=False, na=False)
        )
        display_df = display_df[mask]

    st.subheader(f"📋 불량 발생 대장 (총 {len(display_df)} 건)")
    st.dataframe(
        display_df[['관리번호', '발생일자', '불량구분', '품목명', 'LotNo', '불량현상', '불량수량', '담당부서', '심각도', '손실비용', '진행상태', '품질담당자']],
        use_container_width=True,
        hide_index=True
    )

    # Export & Row Delete
    col_dl, col_del = st.columns([3, 1])
    with col_dl:
        csv_data = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 현재 목록 CSV 다운로드",
            data=csv_data,
            file_name=f"QMS_Defect_List_{date.today()}.csv",
            mime="text/csv"
        )
    with col_del:
        delete_id = st.selectbox("삭제할 관리번호", ["선택"] + list(full_df['관리번호']))
        if st.button("🗑️ 항목 삭제", type="secondary"):
            if delete_id != "선택":
                updated_df = full_df[full_df['관리번호'] != delete_id]
                save_data(updated_df)
                st.success(f"항목 {delete_id} 삭제 완료.")
                st.rerun()

def render_improvement_capa(df, full_df):
    st.title("🔄 개선 진행상황 (CAPA / Kanban)")
    st.caption("원인분석부터 조치완료까지 품질 개선활동을 단계별로 업데이트합니다.")

    stages = ['접수', '원인분석', '대책수립', '개선조치', '효과검증', '조치완료']

    # Kanban Summary Columns
    cols = st.columns(6)
    for idx, stage in enumerate(stages):
        count = len(df[df['진행상태'] == stage])
        cols[idx].metric(f"{idx+1}. {stage}", f"{count} 건")

    st.markdown("---")

    # Item Selector for CAPA Detail Update
    st.subheader("✍️ 불량건별 CAPA 상세 조치 및 단계 업데이트")
    
    selected_id = st.selectbox(
        "개선 관리할 불량 관리번호를 선택하세요",
        options=full_df['관리번호'] + " | " + full_df['품목명'] + " (" + full_df['진행상태'] + ")"
    )

    if selected_id:
        target_id = selected_id.split(" | ")[0]
        row = full_df[full_df['관리번호'] == target_id].iloc[0]

        with st.container():
            st.info(f"**[선택 항목]** 관리번호: **{row['관리번호']}** | 품목: **{row['품목명']}** | 불량현상: **{row['불량현상']}** ({row['불량수량']} EA)")

            with st.form("update_capa_form"):
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    curr_stage_idx = stages.index(row['진행상태']) if row['진행상태'] in stages else 0
                    u_status = st.selectbox("진행 단계 변경", stages, index=curr_stage_idx)
                    u_assignee = st.text_input("조치 담당자", value=str(row['조치담당자']) if pd.notnull(row['조치담당자']) else str(row['품질담당자']))
                with u_col2:
                    default_target_date = row['완료예정일'] if pd.notnull(row['완료예정일']) and isinstance(row['완료예정일'], date) else date.today()
                    u_target_date = st.date_input("완료 (예정) 일자", default_target_date)

                u_cause = st.text_area("근본 원인 분석 (Root Cause)", value=str(row['근본원인']) if pd.notnull(row['근본원인']) else "", placeholder="문제의 근본 원인을 입력하세요 (예: 히터 온도 차이, 작업 오류 등)")
                u_action = st.text_area("재발방지 대책 및 개선조치 사항", value=str(row['재발방지대책']) if pd.notnull(row['재발방지대책']) else "", placeholder="실행된 재발방지 대책을 적어주세요")

                update_btn = st.form_submit_button("💾 CAPA 개선 이력 저장 및 업데이트", use_container_width=True)

                if update_btn:
                    idx = full_df[full_df['관리번호'] == target_id].index[0]
                    full_df.at[idx, '진행상태'] = u_status
                    full_df.at[idx, '근본원인'] = u_cause
                    full_df.at[idx, '재발방지대책'] = u_action
                    full_df.at[idx, '조치담당자'] = u_assignee
                    full_df.at[idx, '완료예정일'] = u_target_date

                    save_data(full_df)
                    st.success(f"관리번호 {target_id}의 CAPA 정보가 업데이트되었습니다!")
                    st.rerun()

    # Detailed CAPA Status Table
    st.markdown("---")
    st.subheader("📖 전사 CAPA 개선활동 현황표")
    st.dataframe(
        df[['관리번호', '발생일자', '불량구분', '품목명', '불량현상', '진행상태', '근본원인', '재발방지대책', '조치담당자', '완료예정일']],
        use_container_width=True,
        hide_index=True
    )

def main():
    df = load_data()
    menu, filtered_df = render_sidebar(df)

    if menu == "종합 대시보드":
        render_dashboard(filtered_df)
    elif menu == "불량 등록 및 대장":
        render_defect_list(filtered_df, df)
    elif menu == "개선 진행상황 (CAPA)":
        render_improvement_capa(filtered_df, df)

if __name__ == "__main__":
    main()
