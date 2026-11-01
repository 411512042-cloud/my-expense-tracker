import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 設定網頁標題與寬度
st.set_page_config(
    page_title="個人記帳與消費分析儀表板",
    page_icon="💰",
    layout="wide",
)

# 自訂類別顏色對應表 (Color Map)
CATEGORY_COLORS = {
    "飲食": "#FF7043",  # 橘色
    "娛樂": "#AB47BC",  # 粉紫色
    "交通": "#29B6F6",  # 藍色
    "日常": "#FFA726",  # 黃色
    "其他": "#78909C",  # 灰色
}

# --- 🎨 注入 CSS 樣式：奶綠色主題 + 圓角按鈕浮動 + 背景動畫 ---
st.markdown(
    """
    <style>
    /* 1. 主背景：奶綠色溫柔漸層與字體 */
    .stApp {
        background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 50%, #DCEDC8 100%);
        font-family: "Helvetica Neue", Arial, sans-serif;
    }

    /* 2. 背景浮動笑笑羊動畫 */
    @keyframes sheepFloat {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .floating-sheep {
        position: fixed;
        bottom: 20px;
        right: 25px;
        font-size: 65px;
        z-index: 999;
        animation: sheepFloat 4s ease-in-out infinite;
        user-select: none;
        pointer-events: none;
        filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.15));
    }

    /* 3. 方圓按鈕與微浮出動畫 (Hover / Active) */
    div.stButton > button {
        background-color: #81C784 !important;
        color: #1B5E20 !important;
        border-radius: 18px !important;
        border: 2px solid #66BB6A !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.25s ease-in-out !important;
    }
    
    /* 按鈕懸停/準備點擊時微浮起 */
    div.stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0px 8px 15px rgba(76, 175, 80, 0.3) !important;
        background-color: #A5D6A7 !important;
        border-color: #4CAF50 !important;
    }
    
    /* 點擊時按壓反饋 */
    div.stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    /* 4. 圓角卡片與內容區塊美化 */
    [data-testid="stMetricValue"] {
        color: #2E7D32 !important;
        font-weight: bold !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="input"] {
        border-radius: 12px !important;
    }
    
    /* Tab 標籤頁美化 */
    button[data-baseweb="tab"] {
        border-radius: 12px 12px 0px 0px !important;
        font-weight: bold !important;
    }
    </style>
    
    <!-- 右下角浮動動畫笑笑羊 -->
    <div class="floating-sheep">🐑</div>
""",
    unsafe_allow_html=True,
)

# 定義資料檔案名稱
DATA_FILE = "expenses.csv"


# 載入資料的函式
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
            df = df.dropna(subset=["日期"])
        if "類型" not in df.columns:
            df["類型"] = "支出"
        return df
    else:
        return pd.DataFrame(columns=["日期", "類型", "類別", "金額", "備註"])


# 儲存資料的函式
def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# 初始化 Session State
if "df" not in st.session_state:
    st.session_state.df = load_data()

st.title("💰 個人記帳與消費分析儀表板")

# 兩欄式版面：左邊輸入，右邊圖表與分析
left_col, right_col = st.columns([1, 2])

# --- 左側：輸入與紀錄區 ---
with left_col:
    st.header("📝 新增收支紀錄")

    # 選擇是「支出」還是「收入(打工/零用錢)」
    transaction_type = st.radio(
        "選擇紀錄類型", ["支出 💸", "收入 (打工/零用錢) 💵"], horizontal=True
    )

    date_input = st.date_input("日期")

    if "支出" in transaction_type:
        category_input = st.selectbox(
            "選擇支出類別", ["飲食", "娛樂", "交通", "日常", "其他"]
        )
        amount_input = st.number_input(
            "金額 (TWD)", min_value=1, step=10, value=100
        )
        note_input = st.text_input("備註 (例如：麥當勞、看電影)")

        if st.button("➕ 新增支出紀錄", use_container_width=True):
            new_row = pd.DataFrame(
                [{
                    "日期": pd.to_datetime(date_input),
                    "類型": "支出",
                    "類別": category_input,
                    "金額": amount_input,
                    "備註": note_input,
                }]
            )
            st.session_state.df = pd.concat(
                [st.session_state.df, new_row], ignore_index=True
            )
            save_data(st.session_state.df)
            st.success("新增支出成功！")
            st.rerun()
    else:
        income_source = st.selectbox(
            "選擇收入來源", ["每月零用錢", "打工薪水", "獎金/其他收入"]
        )
        amount_input = st.number_input(
            "收入金額 (TWD)", min_value=1, step=100, value=5000
        )
        note_input = st.text_input("備註 (例如：10月便利商店打工、媽媽給的)")

        if st.button("💵 新增收入紀錄", use_container_width=True):
            new_row = pd.DataFrame(
                [{
                    "日期": pd.to_datetime(date_input),
                    "類型": "收入",
                    "類別": income_source,
                    "金額": amount_input,
                    "備註": note_input,
                }]
            )
            st.session_state.df = pd.concat(
                [st.session_state.df, new_row], ignore_index=True
            )
            save_data(st.session_state.df)
            st.success("新增收入成功！")
            st.rerun()

    st.markdown("---")

    if st.button("🗑️ 清空所有紀錄", use_container_width=True):
        st.session_state.df = pd.DataFrame(
            columns=["日期", "類型", "類別", "金額", "備註"]
        )
        save_data(st.session_state.df)
        st.warning("資料已清空！")
        st.rerun()

# --- 右側：圖表與分析區 ---
with right_col:
    st.header("📊 月度消費與預算分析儀表板")

    if st.session_state.df.empty:
        st.info("目前還沒有紀錄，請從左側新增收支！")
    else:
        df_all = st.session_state.df.copy()

        df_all["日期"] = pd.to_datetime(df_all["日期"], errors="coerce")
        df_all = df_all.dropna(subset=["日期"])

        df_all["年份"] = df_all["日期"].dt.year.astype(int)
        df_all["月份"] = df_all["日期"].dt.month.astype(int)

        available_years = sorted(df_all["年份"].unique(), reverse=True)
        selected_year = st.selectbox("📅 請選擇年份", available_years)

        available_months = sorted(
            df_all[df_all["年份"] == selected_year]["月份"].unique(),
            reverse=True,
        )
        selected_month = st.selectbox("📆 請選擇月份", available_months)

        df = df_all[
            (df_all["年份"] == selected_year)
            & (df_all["月份"] == selected_month)
        ]

        st.markdown(f"### 📌 {selected_year} 年 {selected_month} 月財務總覽")

        if df.empty:
            st.warning("這個月份目前沒有任何紀錄。")
        else:
            df_expense = df[df["類型"] == "支出"]
            df_income = df[df["類型"] == "收入"]

            total_income = df_income["金額"].sum()
            total_expense = df_expense["金額"].sum()
            remaining_budget = total_income - total_expense

            # 🎯 剩餘總預算進度條
            st.subheader("💡 當月總預算剩餘進度條")
            if total_income > 0:
                budget_ratio = max(
                    0.0, min(1.0, remaining_budget / total_income)
                )
                st.progress(
                    budget_ratio,
                    text=f"剩餘額度：${remaining_budget:,} / 總收入：${total_income:,} ({budget_ratio*100:.1f}%)",
                )

                if remaining_budget < 0:
                    st.error(
                        f"🚨 **預算透支警告**：本月支出已經超出總收入 **${abs(remaining_budget):,}** 元！"
                    )
                elif budget_ratio < 0.2:
                    st.warning(
                        "⚠️ **預算吃緊提示**：本月可用資金剩餘不到 20%，請注意接下來的花費！"
                    )
            else:
                st.info(
                    "💡 目前本月尚未設定零用錢或打工收入，請在左側新增「收入紀錄」以啟用進度條監控！"
                )

            st.markdown("---")

            # 關鍵指標 Summary
            play_spending = df_expense[df_expense["類別"] == "娛樂"][
                "金額"
            ].sum()

            play_ratio = (
                (play_spending / total_expense * 100)
                if total_expense > 0
                else 0
            )

            # 🎯 娛樂預算控管警示 (預算 2500，超過 2000 提醒)
            ENTERTAINMENT_BUDGET = 2500
            if play_spending > ENTERTAINMENT_BUDGET:
                st.error(
                    f"🚨 **{selected_month}月娛樂爆表警告**：本月娛樂已花費 **${play_spending:,}** 元，超出設定上限 (${ENTERTAINMENT_BUDGET:,} 元)！"
                )
            elif play_spending >= 2000:
                st.warning(
                    f"⚠️ **{selected_month}月娛樂花費預警**：本月娛樂已累積 **${play_spending:,}** 元（接近 $2,500 限額）！"
                )

            # 五個關鍵數據卡片 (包含每月娛樂 2500 指標)
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("當月總收入", f"${total_income:,}")
            m2.metric("當月總支出", f"${total_expense:,}")
            m3.metric("當月剩餘可用", f"${remaining_budget:,}")
            m4.metric("當月娛樂花費", f"${play_spending:,} / $2,500")
            m5.metric("娛樂花費比例", f"{play_ratio:.1f}%")

            # 圖表切換 Tab
            tab1, tab2, tab3 = st.tabs(
                ["圓餅圖分析", "每日支出趨勢", "詳細收支明細與刪除"]
            )

            with tab1:
                if not df_expense.empty:
                    fig_pie = px.pie(
                        df_expense,
                        values="金額",
                        names="類別",
                        title=f"{selected_year}/{selected_month} 各分類支出比例",
                        hole=0.4,
                        color="類別",
                        color_discrete_map=CATEGORY_COLORS,
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("當月目前尚無支出紀錄。")

            with tab2:
                if not df_expense.empty:
                    df_daily_cat = (
                        df_expense.groupby(["日期", "類別"])["金額"]
                        .sum()
                        .reset_index()
                    )
                    fig_bar = px.bar(
                        df_daily_cat,
                        x="日期",
                        y="金額",
                        color="類別",
                        title=f"{selected_year}/{selected_month} 每日支出趨勢 (依類別分色)",
                        color_discrete_map=CATEGORY_COLORS,
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("當月目前尚無支出紀錄。")

            with tab3:
                st.subheader(
                    f"📋 {selected_year}/{selected_month} 歷史收支明細列表"
                )
                df_display = df[
                    ["日期", "類型", "類別", "金額", "備註"]
                ].copy()
                df_display["日期"] = df_display["日期"].dt.strftime("%Y-%m-%d")
                st.dataframe(
                    df_display.sort_values(by="日期", ascending=False),
                    use_container_width=True,
                )

                st.markdown("---")
                st.subheader("❌ 刪除特定單筆紀錄")

                options = [
                    f"編號 {idx + 1}: [{row['類型']}] {row['日期'].strftime('%Y-%m-%d')} - {row['類別']} - ${row['金額']} ({row['備註']})"
                    for idx, row in df_all.iterrows()
                ]
                selected_to_delete = st.selectbox("請選擇要刪除的紀錄：", options)

                if st.button("🗑️ 刪除選取的這筆紀錄"):
                    delete_index = options.index(selected_to_delete)
                    st.session_state.df = (
                        st.session_state.df.drop(index=delete_index).reset_index(
                            drop=True
                        )
                    )
                    save_data(st.session_state.df)
                    st.success("已成功刪除該筆紀錄！")
                    st.rerun()