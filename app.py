import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Ranking Mức Độ Am Hiểu World Cup 2026", layout="wide")
st.title("🏆 RANKING MỨC ĐỘ AM HIỂU WORLD CUP 2026")

# ================== GOOGLE SHEET ==================
SHEET_ID = "1diyCsAs02ke2731hE3sqYUotqWmwwMuc9E5MXmVxX3k"
GID = "0"

@st.cache_data(ttl=10)
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
        df = pd.read_csv(url)
        df.columns = [str(col).strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception:
        st.error("❌ Không thể đọc Google Sheet.")
        st.info("✅ Kiểm tra Sheet đã public (Anyone with the link → Viewer)")
        st.stop()

df = load_data()

non_player_cols = list(df.columns[:5])
player_cols = list(df.columns[5:])

CHART_COLORS = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', 
                '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
player_color_map = {player: CHART_COLORS[i % len(CHART_COLORS)] 
                   for i, player in enumerate(player_cols)}

# ================== REFRESH ==================
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# ====================== BẢNG XẾP HẠNG (UI NÂNG CAO) ======================

# 1. Tạo Tiêu đề Bảng nổi bật, căn giữa bằng HTML/CSS
st.markdown("""
    <style>
        .main-title {
            background: linear-gradient(90deg, #1e1e1e, #333333, #1e1e1e);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #444;
            margin-bottom: 25px;
        }
        .main-title h2 {
            color: #FFD700; /* Màu Vàng Gold */
            text-align: center;
            margin: 0;
            font-size: 28px;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-weight: 800;
        }
    </style>
    <div class="main-title">
        <h2>🏆 BẢNG XẾP HẠNG</h2>
    </div>
""", unsafe_allow_html=True)

# Xử lý dữ liệu xếp hạng
totals = df[player_cols].sum(numeric_only=True)
sorted_totals = totals.sort_values(ascending=False)
ranks = sorted_totals.rank(method='min', ascending=False).astype(int)

ranking_df = pd.DataFrame({
    'Xếp hạng': ranks.values,
    'Người chơi': sorted_totals.index,
    'Tổng điểm': sorted_totals.values
}).reset_index(drop=True)

def add_medal(row):
    r = row['Xếp hạng']
    if r == 1: return f"🥇 {row['Người chơi']}"
    elif r == 2: return f"🥈 {row['Người chơi']}"
    elif r == 3: return f"🥉 {row['Người chơi']}"
    return f"   {row['Người chơi']}"

ranking_df['Người chơi'] = ranking_df.apply(add_medal, axis=1)

# Style đổ màu nền cho Top 3
def highlight_rows(row):
    r = row['Xếp hạng']
    if r == 1: 
        return ['background-color: rgba(255, 193, 7, 0.12); color: #FFC107; font-weight: bold;'] * len(row)
    elif r == 2: 
        return ['background-color: rgba(144, 164, 174, 0.12); color: #90A4AE; font-weight: bold;'] * len(row)
    elif r == 3: 
        return ['background-color: rgba(216, 118, 73, 0.12); color: #D87649; font-weight: bold;'] * len(row)
    return [''] * len(row)

styled_ranking = ranking_df.style.apply(highlight_rows, axis=1)

# Chia cột hiển thị
col_table, col_chart = st.columns([3.2, 2.8])

with col_table:
    # Sử dụng st.dataframe với cấu hình cột căn giữa toàn diện
    st.dataframe(
        styled_ranking, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Xếp hạng": st.column_config.NumberColumn(
                "Xếp hạng",
                alignment="center", # Căn giữa tiêu đề và dữ liệu
                width="small",
                help="Thứ hạng hiện tại dựa trên tổng điểm"
            ),
            "Người chơi": st.column_config.TextColumn(
                "Người chơi",
                alignment="left", # Tên người chơi nên giữ căn trái để dễ đọc hơn
                width="medium"
            ),
            "Tổng điểm": st.column_config.NumberColumn(
                "Tổng điểm",
                alignment="center", # Căn giữa tiêu đề và dữ liệu
                format="%.1f",
                width="small"
            )
        }
    )

with col_chart:
    top10 = sorted_totals.head(10)
    fig_bar = go.Figure(go.Bar(
        x=top10.index, 
        y=top10.values,
        marker=dict(
            color=[player_color_map[p] for p in top10.index],
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=[f"{x:,.1f}" for x in top10.values],
        textposition='outside',
        textfont=dict(size=13)
    ))
    fig_bar.update_layout(
        title=dict(text="Biểu đồ Top 10", font=dict(size=18), x=0.5, xanchor='center'),
        height=380,
        xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=30),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.caption(f"🔄 Cập nhật lần cuối: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.divider()

# ====================== BIỂU ĐỒ TIẾN TRIỂN ======================
st.subheader("📈 Tiến Triển Điểm Số Qua Từng Trận")

# Lấy data gốc (chưa fillna) để nhận diện được ô trống
valid_data = df[player_cols]

# Tính điểm cộng dồn (những ô trống ở giữa trận mặc định tính là 0 điểm)
cumulative = valid_data.fillna(0).cumsum()
cumulative.index = range(1, len(cumulative) + 1)
cumulative.index.name = 'Trận'

# Xếp hạng dựa trên tổng điểm thực tế
final_scores = valid_data.fillna(0).sum()
line_ranks = final_scores.rank(method='min', ascending=False).astype(int)

fig = go.Figure()

# Dictionary lưu trữ các điểm cuối để xử lý xếp chồng text
end_points = {}
max_last_x = 1  # Biến lưu trữ trận xa nhất có dữ liệu để giới hạn trục X

for player in player_cols:
    color = player_color_map[player]
    
    # Tìm index hợp lệ cuối cùng của người chơi này
    last_valid_orig_idx = valid_data[player].last_valid_index()
    
    if last_valid_orig_idx is not None:
        last_x = last_valid_orig_idx + 1 # +1 vì index biểu đồ bắt đầu từ 1
        max_last_x = max(max_last_x, last_x) # Cập nhật trận lớn nhất có dữ liệu
        
        # Cắt chuỗi dữ liệu: Chỉ lấy data đến trận có điểm cuối cùng
        x_data = cumulative.index[:last_x]
        y_data = cumulative[player].iloc[:last_x]
        last_y = y_data.iloc[-1]
        
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name=player,
            line=dict(color=color, width=3),
            marker=dict(size=5),
            cliponaxis=False  # Giữ cho chấm marker không bị lẹm khi giới hạn sát rìa trục X
        ))
        
        # Gom các label có chung điểm kết thúc
        end_points.setdefault((last_x, last_y), []).append((player, line_ranks[player], color))

# Vòng lặp thêm text (Hạng + Tên) vào cuối đường biểu đồ
for (x, y), players_info in end_points.items():
    n = len(players_info)
    # Sắp xếp ưu tiên hiển thị hạng cao lên trên
    players_info.sort(key=lambda item: item[1]) 
    
    for i, (player, rank, color) in enumerate(players_info):
        yshift = (n - 1 - 2 * i) * 9 
        
        fig.add_annotation(
            x=x,
            y=y,
            text=f"<b>#{rank} {player}</b>",
            showarrow=False,
            xanchor='left',
            yanchor='middle',
            xshift=10,  
            yshift=yshift,
            font=dict(color=color, size=14)
        )

# Đảm bảo khung biểu đồ có tối thiểu 2 mốc nếu mới chỉ đá 1 trận
x_range_end = max_last_x if max_last_x > 1 else 2

fig.update_layout(
    height=580,
    margin=dict(r=180), # Lề phải rộng để chứa nhãn tên
    xaxis=dict(
        title="Trận", 
        tickmode='linear', 
        dtick=1,
        range=[1, x_range_end] # Ép trục X dừng đúng tại trận cuối, ngắt các đường gridline ngang đâm vào chữ
    ),
    yaxis=dict(title="Điểm tích lũy"),
    hovermode="x unified",
    showlegend=False, 
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ====================== BẢNG CHI TIẾT ======================
st.subheader("📋 Bảng Dự Đoán Chi Tiết")
st.dataframe(df, use_container_width=True, height=700)

st.markdown("**Hướng dẫn:** Chỉnh sửa trên Google Sheet → Nhấn **Refresh Data** để cập nhật.")