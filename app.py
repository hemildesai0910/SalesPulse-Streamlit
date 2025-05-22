import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from datetime import datetime

# set page config FIRST, only once
dark_mode = 'theme' in st.session_state and st.session_state['theme'] == 'dark'
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# custom css for card style and theme
st.markdown('''
    <style>
    .metric-card {
        background: var(--secondary-background-color);
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(80,0,120,0.08);
        padding: 1.2rem 1rem 1rem 1rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-label {
        color: #a259ff;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-top: 0.2rem;
    }
    .st-emotion-cache-1v0mbdj {background: #18122B !important;}
    .st-emotion-cache-1r4qj8v {background: #18122B !important;}
    </style>
''', unsafe_allow_html=True)

# theme toggle
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

def toggle_theme():
    st.session_state['theme'] = 'dark' if st.session_state['theme'] == 'light' else 'light'

# set theme colors
if st.session_state['theme'] == 'dark':
    primary_bg = "#18122B"
    secondary_bg = "#22223B"
    accent = "#a259ff"
    text = "#fff"
else:
    primary_bg = "#fff"
    secondary_bg = "#f7f7fa"
    accent = "#a259ff"
    text = "#22223B"

# theme toggle button
st.sidebar.button(
    "🌙 dark mode" if st.session_state['theme'] == 'light' else "☀️ light mode",
    on_click=toggle_theme,
    use_container_width=True
)

# load data
@st.cache_data
def load_data():
    df = pd.read_csv("data_query/superstore.csv")
    # convert date columns to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['ship_date'] = pd.to_datetime(df['ship_date'])
    return df

# load the data
df = load_data()

# sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Sales", "Trends", "Category", "Product", "Location", "Shipping"],
        icons=["house", "bar-chart", "activity", "layers", "box", "map", "truck"],
        default_index=0,
        styles={
            "container": {"background-color": secondary_bg},
            "icon": {"color": accent, "font-size": "20px"},
            "nav-link": {"color": text, "font-size": "16px", "text-align": "left", "margin":"0.2rem 0"},
            "nav-link-selected": {"background-color": accent, "color": "#fff"},
        }
    )

# filter widgets (top bar)
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,2])
with col1:
    region = st.selectbox("Select Region", ["All"] + sorted(df['region'].unique().tolist()))
with col2:
    state = st.selectbox("Select State", ["All"] + sorted(df['state'].unique().tolist()))
with col3:
    city = st.selectbox("Pick the City", ["All"] + sorted(df['city'].unique().tolist()))
with col4:
    min_date = df['order_date'].min()
    max_date = df['order_date'].max()
    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
with col5:
    end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

# filter data
df_filtered = df.copy()
if region != "All":
    df_filtered = df_filtered[df_filtered['region'] == region]
if state != "All":
    df_filtered = df_filtered[df_filtered['state'] == state]
if city != "All":
    df_filtered = df_filtered[df_filtered['city'] == city]
df_filtered = df_filtered[(df_filtered['order_date'] >= pd.to_datetime(start_date)) & (df_filtered['order_date'] <= pd.to_datetime(end_date))]

# summary metrics (top cards)
metric_cols = st.columns(6)
metrics = [
    ("Total Sales", f"${df_filtered['sales'].sum():,.0f}", "📈"),
    ("Qty Sold", f"{df_filtered['quantity'].sum():,}", "🛒"),
    ("Total Profit", f"${df_filtered['profit'].sum():,.0f}", "💰"),
    ("Top Category", df_filtered.groupby('category')['sales'].sum().idxmax() if not df_filtered.empty else "-", "🏆"),
    ("Top City", df_filtered.groupby('city')['sales'].sum().idxmax() if not df_filtered.empty else "-", "🏙️"),
    ("Orders", f"{df_filtered['order_id'].nunique():,}", "📦"),
]
for i, (label, value, icon) in enumerate(metrics):
    with metric_cols[i]:
        st.markdown(f'<div class="metric-card"><span class="metric-label">{icon} {label}</span><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

# main content by page
if selected == "Home":
    st.title("SUPERSTORE SALES DASHBOARD")
    st.write("""
    This project aims to provide an easy-to-use interactive interface for users to gain insights into sales trends, product performance, and customer behavior.
    """)
    st.info("Navigate from side panel and filter from above according to your needs.")
    st.image("https://avatars.githubusercontent.com/u/9919?s=200&v=4", width=120)

elif selected == "Sales":
    st.header("Sales by Category & Region")
    c1, c2 = st.columns(2)
    with c1:
        cat_sales = df_filtered.groupby('category')['sales'].sum().reset_index()
        fig = px.bar(cat_sales, x='category', y='sales', color='category', color_discrete_sequence=[accent]*3)
        fig.update_layout(
            title='Sales by Category',
            title_font=dict(color=text, size=22, family='sans-serif'),
            font_color=text,
            xaxis=dict(
                color=text,
                title='Category',
                title_font=dict(color=text, size=16),
                gridcolor=secondary_bg
            ),
            yaxis=dict(
                color=text,
                title='Sales',
                title_font=dict(color=text, size=16),
                gridcolor=secondary_bg
            ),
            legend=dict(
                font=dict(color=text, size=14)
            ),
            plot_bgcolor=secondary_bg,
            paper_bgcolor=secondary_bg,
        )
        fig.update_traces(
            texttemplate='%{y:,}',
            textfont=dict(color=text, size=14),
            textposition='auto'
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        reg_sales = df_filtered.groupby('region')['sales'].sum().reset_index()
        fig = px.pie(reg_sales, values='sales', names='region', color_discrete_sequence=[accent, '#6c47b6', '#c3a6ff', '#e0d6f7'])
        fig.update_layout(
            title='Sales by Region',
            title_font=dict(color=text, size=22, family='sans-serif'),
            font_color=text,
            xaxis=dict(color=text),
            yaxis=dict(color=text),
            legend=dict(
                font=dict(color=text, size=14)
            ),
            plot_bgcolor=secondary_bg,
            paper_bgcolor=secondary_bg,
        )
        fig.update_traces(
            texttemplate='%{percent}',
            textfont=dict(color=text, size=14),
            textposition='inside'
        )
        st.plotly_chart(fig, use_container_width=True)

elif selected == "Trends":
    st.header("Sales By Time")
    trend = df_filtered.groupby(df_filtered['order_date'].dt.to_period('M'))['sales'].sum().reset_index()
    trend['order_date'] = trend['order_date'].astype(str)
    fig = px.line(trend, x='order_date', y='sales', markers=True, color_discrete_sequence=[accent])
    fig.update_layout(
        title='Sales Over Time',
        title_font=dict(color=text, size=22, family='sans-serif'),
        font_color=text,
        xaxis=dict(
            color=text,
            title='Time',
            title_font=dict(color=text, size=16),
            gridcolor=secondary_bg
        ),
        yaxis=dict(
            color=text,
            title='Sales',
            title_font=dict(color=text, size=16),
            gridcolor=secondary_bg
        ),
        legend=dict(
            font=dict(color=text, size=14)
        ),
        plot_bgcolor=secondary_bg,
        paper_bgcolor=secondary_bg,
    )
    fig.update_traces(line_width=3)
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Category":
    st.header("Category Analysis")
    cat = st.selectbox("Choose Category", ["All"] + sorted(df_filtered['category'].unique().tolist()))
    data = df_filtered if cat == "All" else df_filtered[df_filtered['category'] == cat]
    subcat_sales = data.groupby('sub_category')['sales'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(subcat_sales, x='sub_category', y='sales', color='sub_category', color_discrete_sequence=px.colors.sequential.Purples)
    fig.update_layout(
        title='Sales by Subcategory',
        title_font=dict(color=text, size=22, family='sans-serif'),
        font_color=text,
        xaxis=dict(
            color=text,
            title='Subcategory',
            title_font=dict(color=text, size=16),
            gridcolor=secondary_bg
        ),
        yaxis=dict(
            color=text,
            title='Sales',
            title_font=dict(color=text, size=16),
            gridcolor=secondary_bg
        ),
        legend=dict(
            font=dict(color=text, size=14)
        ),
        plot_bgcolor=secondary_bg,
        paper_bgcolor=secondary_bg,
    )
    fig.update_traces(
        texttemplate='%{y:,}',
        textfont=dict(color=text, size=14),
        textposition='auto'
    )
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Product":
    st.header("Product Performance")
    top_products = df_filtered.groupby('product_name')['sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(top_products, x='product_name', y='sales', color='sales', color_continuous_scale=px.colors.sequential.Purples)
    fig.update_layout(
        title='Top Products by Sales',
        title_font=dict(color=text, size=22, family='sans-serif'),
        font_color=text,
        xaxis=dict(
            color=text,
            title='Product',
            title_font=dict(color=text, size=16),
            gridcolor=secondary_bg
        ),
        yaxis=dict(
            color=text,
            title='Sales',
            title_font=dict(color=text, size=16),
            gridcolor=secondary_bg
        ),
        legend=dict(
            font=dict(color=text, size=14)
        ),
        plot_bgcolor=secondary_bg,
        paper_bgcolor=secondary_bg,
    )
    fig.update_traces(
        texttemplate='%{y:,}',
        textfont=dict(color=text, size=14),
        textposition='auto'
    )
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Location":
    st.header("Sales by State & City")
    c1, c2 = st.columns(2)
    with c1:
        state_sales = df_filtered.groupby('state')['sales'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(state_sales, x='state', y='sales', color='sales', color_continuous_scale=px.colors.sequential.Purples)
        fig.update_layout(
            title='Sales by State',
            title_font=dict(color=text, size=22, family='sans-serif'),
            font_color=text,
            xaxis=dict(
                color=text,
                title='State',
                title_font=dict(color=text, size=16),
                gridcolor=secondary_bg
            ),
            yaxis=dict(
                color=text,
                title='Sales',
                title_font=dict(color=text, size=16),
                gridcolor=secondary_bg
            ),
            legend=dict(
                font=dict(color=text, size=14)
            ),
            plot_bgcolor=secondary_bg,
            paper_bgcolor=secondary_bg,
        )
        fig.update_traces(
            texttemplate='%{y:,}',
            textfont=dict(color=text, size=14),
            textposition='auto'
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        city_sales = df_filtered.groupby('city')['sales'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(city_sales, x='city', y='sales', color='sales', color_continuous_scale=px.colors.sequential.Purples)
        fig.update_layout(
            title='Sales by City',
            title_font=dict(color=text, size=22, family='sans-serif'),
            font_color=text,
            xaxis=dict(
                color=text,
                title='City',
                title_font=dict(color=text, size=16),
                gridcolor=secondary_bg
            ),
            yaxis=dict(
                color=text,
                title='Sales',
                title_font=dict(color=text, size=16),
                gridcolor=secondary_bg
            ),
            legend=dict(
                font=dict(color=text, size=14)
            ),
            plot_bgcolor=secondary_bg,
            paper_bgcolor=secondary_bg,
        )
        fig.update_traces(
            texttemplate='%{y:,}',
            textfont=dict(color=text, size=14),
            textposition='auto'
        )
        st.plotly_chart(fig, use_container_width=True)

elif selected == "Shipping":
    st.header("Shipping Analysis")
    ship_mode = df_filtered.groupby('ship_mode')['sales'].sum().reset_index()
    fig = px.pie(ship_mode, values='sales', names='ship_mode', color_discrete_sequence=[accent, '#6c47b6', '#c3a6ff', '#e0d6f7'])
    fig.update_layout(
        title='Shipping Mode Distribution',
        title_font=dict(color=text, size=22, family='sans-serif'),
        font_color=text,
        xaxis=dict(color=text),
        yaxis=dict(color=text),
        legend=dict(
            font=dict(color=text, size=14)
        ),
        plot_bgcolor=secondary_bg,
        paper_bgcolor=secondary_bg,
    )
    fig.update_traces(
        texttemplate='%{percent}',
        textfont=dict(color=text, size=14),
        textposition='inside'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("Average Shipping Time:")
    avg_ship = (df_filtered['ship_date'] - df_filtered['order_date']).dt.days.mean()
    st.metric("Avg. Shipping Days", f"{avg_ship:.1f} days" if not pd.isna(avg_ship) else "-") 