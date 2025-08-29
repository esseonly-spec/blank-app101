#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>
/* 페이지 여백 */
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* ===== Metric 카드를 화이트로 (배경/테두리/그림자) ===== */
[data-testid="stMetric"]{
    background-color: #ffffff !important;  /* 흰 배경 */
    text-align: center;
    padding: 15px 0;
    border: 1px solid #e9e9e9;
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,.05);
}

/* Metric 라벨/값 텍스트 컬러 */
[data-testid="stMetricLabel"], 
[data-testid="stMetricValue"] {
    color: #111111 !important;
}
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 600;
  opacity: .9;
}

/* 델타 아이콘 위치 보정 */
[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}
</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기

#######################
# Sidebar
with st.sidebar:
    # ======================
    # Sidebar: Controls
    # ======================
    st.header("Titanic Dashboard")
    st.caption("필터를 선택해 데이터를 탐색하세요.")
    st.markdown("---")

    # 기본 정보
    st.metric("총 승객 수", f"{len(df_reshaped):,}")

    # 선택 옵션 준비
    pclass_options = sorted(df_reshaped["Pclass"].dropna().unique().tolist())
    sex_options = df_reshaped["Sex"].dropna().unique().tolist()
    embarked_options = df_reshaped["Embarked"].dropna().unique().tolist()

    # 필터 위젯
    selected_pclass = st.multiselect("탑승 클래스 (Pclass)", pclass_options, default=pclass_options)
    selected_sex = st.multiselect("성별 (Sex)", sex_options, default=sex_options)
    selected_embarked = st.multiselect("승선 항구 (Embarked)", embarked_options, default=embarked_options)

    age_min = int(df_reshaped["Age"].dropna().min())
    age_max = int(df_reshaped["Age"].dropna().max())
    selected_age = st.slider("연령대 (Age)", min_value=age_min, max_value=age_max, value=(age_min, age_max))

    fare_min = float(df_reshaped["Fare"].dropna().min())
    fare_max = float(df_reshaped["Fare"].dropna().max())
    selected_fare = st.slider("요금 범위 (Fare)", min_value=float(fare_min), max_value=float(fare_max), value=(float(fare_min), float(fare_max)))

    # 가족 인원수(본인 제외) = 형제/배우자 + 부모/자녀
    df_reshaped["_FamilySize"] = (df_reshaped["SibSp"].fillna(0) + df_reshaped["Parch"].fillna(0)).astype(int)
    fam_min = int(df_reshaped["_FamilySize"].min())
    fam_max = int(df_reshaped["_FamilySize"].max())
    selected_family = st.slider("가족 동반 인원수 (SibSp + Parch)", min_value=fam_min, max_value=fam_max, value=(fam_min, fam_max))

    # 결측치 처리 옵션
    drop_na_age = st.checkbox("나이 결측치 제외", value=False)
    drop_na_embarked = st.checkbox("승선 항구 결측치 제외", value=False)

    st.markdown("---")
    st.caption("필터 결과는 st.session_state['filtered_df'] 에 저장됩니다.")

    # ======================
    # Apply filters
    # ======================
    _df = df_reshaped.copy()

    # 범주형 필터
    if selected_pclass:
        _df = _df[_df["Pclass"].isin(selected_pclass)]
    if selected_sex:
        _df = _df[_df["Sex"].isin(selected_sex)]
    if selected_embarked:
        _df = _df[_df["Embarked"].isin(selected_embarked)]

    # 수치형 필터
    _df = _df[_df["Age"].between(selected_age[0], selected_age[1], inclusive="both") | _df["Age"].isna()]
    _df = _df[_df["Fare"].between(selected_fare[0], selected_fare[1], inclusive="both") | _df["Fare"].isna()]
    _df = _df[_df["_FamilySize"].between(selected_family[0], selected_family[1], inclusive="both")]

    # 결측치 옵션 반영
    if drop_na_age:
        _df = _df.dropna(subset=["Age"])
    if drop_na_embarked:
        _df = _df.dropna(subset=["Embarked"])

    # 세션에 저장 (메인 패널/플롯에서 사용)
    st.session_state["filtered_df"] = _df

    # 요약 표시
    st.success(f"필터 적용 후 행 수: {len(_df):,}")

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.subheader("📊 요약 지표")

    # 데이터 가져오기
    df = st.session_state["filtered_df"]

    total_passengers = len(df)
    survived_count = int(df["Survived"].sum())
    dead_count = total_passengers - survived_count

    # KPI 카드 스타일 지표
    st.metric(label="총 승객 수", value=f"{total_passengers:,}")
    st.metric(label="생존자 수", value=f"{survived_count:,}", delta=f"{(survived_count/total_passengers*100):.1f}%")
    st.metric(label="사망자 수", value=f"{dead_count:,}", delta=f"{(dead_count/total_passengers*100):.1f}%")

    st.markdown("---")

    # 성별 생존율
    st.markdown("**성별 생존율 (%)**")
    sex_survival = (
        df.groupby("Sex")["Survived"]
        .mean()
        .mul(100)
        .round(1)
        .to_frame()
        .reset_index()
    )
    sex_chart = alt.Chart(sex_survival).mark_bar().encode(
        x=alt.X("Sex:N", title="성별"),
        y=alt.Y("Survived:Q", title="생존율 (%)"),
        color="Sex:N",
        tooltip=["Sex", "Survived"]
    )
    st.altair_chart(sex_chart, use_container_width=True)

    st.markdown("---")

    # Pclass별 생존율
    st.markdown("**객실 등급별 생존율 (%)**")
    pclass_survival = (
        df.groupby("Pclass")["Survived"]
        .mean()
        .mul(100)
        .round(1)
        .to_frame()
        .reset_index()
    )
    pclass_chart = alt.Chart(pclass_survival).mark_bar().encode(
        x=alt.X("Pclass:N", title="Pclass"),
        y=alt.Y("Survived:Q", title="생존율 (%)"),
        color="Pclass:N",
        tooltip=["Pclass", "Survived"]
    )
    st.altair_chart(pclass_chart, use_container_width=True)

with col[1]:
    st.subheader("🗺️ 분포 & 히트맵 시각화")

    df = st.session_state["filtered_df"].copy()

    # 1) 연령대 × Pclass 생존율 히트맵
    st.markdown("**연령대 × 객실등급 생존율(%) 히트맵**")

    age_bins = list(range(0, 90, 10))
    age_labels = [f"{i}-{i+9}" for i in age_bins[:-1]]
    df_heat = df.dropna(subset=["Age", "Pclass", "Survived"]).copy()
    df_heat["AgeBin"] = pd.cut(df_heat["Age"], bins=age_bins, right=False, labels=age_labels)

    heat = (
        df_heat.groupby(["Pclass", "AgeBin"])["Survived"]
        .mean()
        .mul(100)
        .reset_index(name="SurvivalRate")
    )

    heatmap = (
        alt.Chart(heat)
        .mark_rect()
        .encode(
            x=alt.X("AgeBin:N", title="연령대"),
            y=alt.Y("Pclass:O", title="객실 등급 (Pclass)"),
            color=alt.Color("SurvivalRate:Q", title="생존율(%)"),
            tooltip=["Pclass", "AgeBin", alt.Tooltip("SurvivalRate:Q", format=".1f")]
        )
        .properties(height=300)
    )
    text = (
        alt.Chart(heat)
        .mark_text(baseline="middle")
        .encode(
            x="AgeBin:N",
            y="Pclass:O",
            text=alt.Text("SurvivalRate:Q", format=".0f")
        )
    )
    st.altair_chart(heatmap + text, use_container_width=True)

    st.markdown("---")

    # 2) 연령 분포 히스토그램 (생존/사망 비교)
    st.markdown("**연령 분포 히스토그램 (생존 여부별)**")
    df_age = df.dropna(subset=["Age", "Survived"]).copy()
    df_age["Survival"] = df_age["Survived"].map({0: "사망", 1: "생존"})

    hist_fig = px.histogram(
        df_age,
        x="Age",
        color="Survival",
        barmode="overlay",
        nbins=30,
        marginal="rug",
        opacity=0.7
    )
    hist_fig.update_layout(height=320, xaxis_title="나이(Age)", yaxis_title="인원 수")
    st.plotly_chart(hist_fig, use_container_width=True)

    st.markdown("---")

    # 3) 운임(Fare) 분포 (Pclass × 생존 여부)
    st.markdown("**운임(Fare) 분포 (객실등급 × 생존 여부)**")
    df_fare = df.dropna(subset=["Fare", "Pclass", "Survived"]).copy()
    df_fare["Survival"] = df_fare["Survived"].map({0: "사망", 1: "생존"})

    box_fig = px.box(
        df_fare,
        x="Pclass",
        y="Fare",
        color="Survival",
        points="outliers"
    )
    box_fig.update_layout(height=320, xaxis_title="객실 등급 (Pclass)", yaxis_title="운임(Fare)")
    st.plotly_chart(box_fig, use_container_width=True)

with col[2]:
    st.subheader("🏆 랭킹 & 세부 인사이트")

    df = st.session_state["filtered_df"].copy()

    # 1) 가족 동반 인원수 (SibSp + Parch) 상위 TOP5
    st.markdown("**가족 동반 인원수 TOP5 (SibSp + Parch)**")
    if "_FamilySize" not in df.columns:
        df["_FamilySize"] = (df["SibSp"].fillna(0) + df["Parch"].fillna(0)).astype(int)

    fam_rank = (
        df.groupby("_FamilySize")["Survived"]
        .mean()
        .mul(100)
        .reset_index(name="SurvivalRate")
        .sort_values("SurvivalRate", ascending=False)
        .head(5)
    )

    fam_chart = alt.Chart(fam_rank).mark_bar().encode(
        x=alt.X("_FamilySize:O", title="가족 동반 인원수"),
        y=alt.Y("SurvivalRate:Q", title="생존율(%)"),
        color="_FamilySize:O",
        tooltip=["_FamilySize", "SurvivalRate"]
    )
    st.altair_chart(fam_chart, use_container_width=True)

    st.markdown("---")

    # 2) 운임(Fare) 상위 10명 → 생존 여부
    st.markdown("**운임(Fare) 상위 10명 분석**")
    fare_top10 = df.nlargest(10, "Fare")[["Name", "Fare", "Survived"]].copy()
    fare_top10["Survival"] = fare_top10["Survived"].map({0: "사망", 1: "생존"})
    st.dataframe(fare_top10[["Name", "Fare", "Survival"]].reset_index(drop=True), use_container_width=True)

    st.markdown("---")

    # 3) 항구별(Embarked) 생존율
    st.markdown("**승선 항구별 생존율 (%)**")
    if "Embarked" in df.columns:
        emb = (
            df.dropna(subset=["Embarked"])
            .groupby("Embarked")["Survived"]
            .mean()
            .mul(100)
            .reset_index(name="SurvivalRate")
        )

        emb_chart = alt.Chart(emb).mark_bar().encode(
            x=alt.X("Embarked:N", title="승선 항구"),
            y=alt.Y("SurvivalRate:Q", title="생존율(%)"),
            color="Embarked:N",
            tooltip=["Embarked", "SurvivalRate"]
        )
        st.altair_chart(emb_chart, use_container_width=True)

    st.markdown("---")

    # 4) About 섹션
    st.subheader("ℹ️ About")
    st.markdown("""
    - **데이터셋**: 타이타닉 승객 생존 데이터 (Kaggle Titanic Challenge)
    - **주요 변수**
        - Pclass: 객실 등급 (1=고급, 3=저가)
        - Sex: 성별
        - Age: 나이
        - SibSp: 동승 형제/배우자 수
        - Parch: 동승 부모/자녀 수
        - Fare: 운임
        - Embarked: 승선 항구 (C, Q, S)
        - Survived: 생존 여부 (0=사망, 1=생존)
    - **대시보드 목적**: 
        - 생존율에 영향을 미친 주요 요인 탐색  
        - 연령, 성별, 객실 등급, 가족 구성, 운임, 출발 항구와의 관계 분석
    """)
