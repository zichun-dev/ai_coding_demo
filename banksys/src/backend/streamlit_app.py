"""Streamlit application for data visualization."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.models import DataLoader


@st.cache_resource
def get_data_loader() -> DataLoader:
    data_dir = Path(__file__).parent.parent.parent / "data"
    return DataLoader(data_dir=data_dir)


def main():
    st.set_page_config(
        page_title="银行营销数据展示系统",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🏦 银行营销数据展示系统")
    st.markdown("---")

    loader = get_data_loader()

    with st.sidebar:
        st.header("📊 数据筛选")

        dataset = st.radio(
            "选择数据集",
            options=["train", "test"],
            format_func=lambda x: "训练集" if x == "train" else "测试集",
        )

        st.subheader("筛选条件")

        jobs = ["全部"] + loader.get_unique_values("job")
        selected_job = st.selectbox("职业", jobs)

        marital_status = ["全部"] + loader.get_unique_values("marital")
        selected_marital = st.selectbox("婚姻状态", marital_status)

        education_levels = ["全部"] + loader.get_unique_values("education")
        selected_education = st.selectbox("教育程度", education_levels)

        age_range = st.slider(
            "年龄范围",
            min_value=17,
            max_value=100,
            value=(17, 100),
        )

        subscribe_filter = None
        if dataset == "train":
            subscribe_options = ["全部", "yes", "no"]
            subscribe_filter = st.selectbox(
                "订阅状态",
                subscribe_options,
                format_func=lambda x: {
                    "全部": "全部",
                    "yes": "已订阅",
                    "no": "未订阅",
                }.get(x, x),
            )

    summary = loader.get_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总记录数", f"{summary.total_records:,}")
    with col2:
        st.metric("训练集", f"{summary.train_records:,}")
    with col3:
        st.metric("测试集", f"{summary.test_records:,}")
    with col4:
        if summary.subscribe_distribution:
            yes_rate = (
                summary.subscribe_distribution.get("yes", 0)
                / summary.train_records
                * 100
            )
            st.metric("订阅率", f"{yes_rate:.1f}%")

    st.markdown("---")

    filtered_df = loader.get_filtered_data(
        dataset=dataset,
        job=None if selected_job == "全部" else selected_job,
        marital=None if selected_marital == "全部" else selected_marital,
        education=None if selected_education == "全部" else selected_education,
        min_age=age_range[0],
        max_age=age_range[1],
        subscribe=None if subscribe_filter == "全部" else subscribe_filter,
    )

    st.subheader(f"📋 数据预览 (共 {len(filtered_df):,} 条记录)")

    display_columns = [
        "id",
        "age",
        "job",
        "marital",
        "education",
        "housing",
        "loan",
        "contact",
    ]
    if dataset == "train":
        display_columns.append("subscribe")

    st.dataframe(
        filtered_df[display_columns].head(100),
        use_container_width=True,
        height=400,
    )

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["职业分布", "年龄分布", "婚姻状态", "教育程度"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            job_counts = filtered_df["job"].value_counts()
            fig_job = px.bar(
                x=job_counts.index,
                y=job_counts.values,
                title="职业分布柱状图",
                labels={"x": "职业", "y": "人数"},
                color=job_counts.values,
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig_job, use_container_width=True)

        with col2:
            fig_pie = px.pie(
                values=job_counts.values,
                names=job_counts.index,
                title="职业分布饼图",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            fig_hist = px.histogram(
                filtered_df,
                x="age",
                nbins=30,
                title="年龄分布直方图",
                labels={"age": "年龄", "count": "人数"},
                color_discrete_sequence=["#1f77b4"],
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            fig_box = px.box(
                filtered_df,
                y="age",
                x="job",
                title="各职业年龄箱线图",
                labels={"age": "年龄", "job": "职业"},
            )
            fig_box.update_xaxes(tickangle=45)
            st.plotly_chart(fig_box, use_container_width=True)

    with tab3:
        marital_counts = filtered_df["marital"].value_counts()
        fig_marital = px.bar(
            x=marital_counts.index,
            y=marital_counts.values,
            title="婚姻状态分布",
            labels={"x": "婚姻状态", "y": "人数"},
            color=marital_counts.values,
            color_continuous_scale="Greens",
        )
        st.plotly_chart(fig_marital, use_container_width=True)

    with tab4:
        edu_counts = filtered_df["education"].value_counts()
        fig_edu = px.bar(
            x=edu_counts.index,
            y=edu_counts.values,
            title="教育程度分布",
            labels={"x": "教育程度", "y": "人数"},
            color=edu_counts.values,
            color_continuous_scale="Oranges",
        )
        fig_edu.update_xaxes(tickangle=45)
        st.plotly_chart(fig_edu, use_container_width=True)

    if dataset == "train" and "subscribe" in filtered_df.columns:
        st.markdown("---")
        st.subheader("📈 订阅分析")

        col1, col2 = st.columns(2)

        with col1:
            subscribe_by_job = (
                filtered_df.groupby("job")["subscribe"]
                .apply(lambda x: (x == "yes").sum() / len(x) * 100)
                .sort_values(ascending=False)
            )
            fig_subscribe = px.bar(
                x=subscribe_by_job.index,
                y=subscribe_by_job.values,
                title="各职业订阅率 (%)",
                labels={"x": "职业", "y": "订阅率 (%)"},
                color=subscribe_by_job.values,
                color_continuous_scale="RdYlGn",
            )
            fig_subscribe.update_xaxes(tickangle=45)
            st.plotly_chart(fig_subscribe, use_container_width=True)

        with col2:
            age_subscribe = filtered_df.groupby(
                pd.cut(filtered_df["age"], bins=[17, 30, 40, 50, 60, 100])
            )["subscribe"].apply(lambda x: (x == "yes").sum() / len(x) * 100)

            fig_age_sub = px.bar(
                x=[str(x) for x in age_subscribe.index],
                y=age_subscribe.values,
                title="各年龄段订阅率 (%)",
                labels={"x": "年龄段", "y": "订阅率 (%)"},
                color=age_subscribe.values,
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig_age_sub, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 统计摘要")

    numeric_cols = ["age", "duration", "campaign", "pdays", "previous"]
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[numeric_cols].describe().round(2),
            use_container_width=True,
        )

    st.markdown("---")
    st.caption(
        f"数据来源: train.csv ({summary.train_records:,} 条) | "
        f"test.csv ({summary.test_records:,} 条)"
    )


if __name__ == "__main__":
    main()
