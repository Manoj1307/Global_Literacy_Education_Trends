import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. Configuration & Layout
# ==========================================
st.set_page_config(page_title="Global Literacy Dashboard", page_icon="🌎", layout="wide")

# ==========================================
# 2. Database Connection Management
# ==========================================
DB_USER = "root"
DB_PASSWORD = "Mano_rootsql0481"
DB_HOST = "localhost"
DB_NAME = "global_literacy_education_trends"
DB_PORT = 3306

@st.cache_resource
def get_engine():
    try:
        return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        return None

engine = get_engine()

@st.cache_data(ttl=600)
def fetch_data(query):
    if engine is None:
        st.error("Database Engine is not initialized. Please ensure MySQL is running.")
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return pd.DataFrame()

# ==========================================
# 3. Data Loading (Cached)
# ==========================================
@st.cache_data
def load_base_data():
    lit_df = fetch_data("SELECT * FROM LITERACY LIMIT 50000")
    illit_df = fetch_data("SELECT * FROM ILLITERACY_POPULATION LIMIT 50000")
    gdp_df = fetch_data("SELECT * FROM GDP_SCHOOLING LIMIT 50000")
    
    # Try merging purely for python-side high-level cross analysis if DB doesn't have it
    merged = pd.DataFrame()
    if not lit_df.empty and not gdp_df.empty:
        merged = pd.merge(lit_df, gdp_df, on=['COUNTRY', 'YEAR'], how='inner')
    return lit_df, illit_df, gdp_df, merged

lit_df, illit_df, gdp_df, merged_df = load_base_data()

# ==========================================
# 4. Sidebar / Slicers
# ==========================================
st.sidebar.title("Dashboard Controls")

global_year_range = (1950, 2022)
if not lit_df.empty:
    global_year_range = (int(lit_df['YEAR'].min()), int(lit_df['YEAR'].max()))

selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=global_year_range[0], max_value=global_year_range[1],
    value=(1980, 2020), step=1
)

country_list = ["All Countries"]
if not lit_df.empty:
    country_list += lit_df['COUNTRY'].dropna().unique().tolist()
    
selected_country = st.sidebar.selectbox("Select Country (For specific charts)", country_list)

st.sidebar.markdown("---")
st.sidebar.info("Data dynamically pulled from MySQL Database (`global_literacy_education_trends`)")


# ==========================================
# 5. Header Section
# ==========================================
st.markdown('<h1 class="main-title">🌍 Global Literacy & Education Trends</h1>', unsafe_allow_html=True)
st.write("An analytic dashboard visualizing the relationships between literacy rates, GDP, education infrastructure, and generational shifts.")

if lit_df.empty or gdp_df.empty:
    st.warning("⚠️ Could not load data from the database. Please ensure the MySQL credentials in the script are correct and the server is running.")
    st.stop()

# ==========================================
# 6. Tab Layout
# ==========================================
tab_advanced, tab_queries = st.tabs(["📊 Advanced Visualizations", "📝 The 13 SQL Queries Output"])

# -----------------------------------------------------------------------------------------
# TAB 1: ADVANCED VISUALIZATIONS (Based strictly on vizualize.md ideas)
# -----------------------------------------------------------------------------------------
with tab_advanced:
    st.header("Deep-Dive Insights & Socio-Economic Comparisons")
    
    # Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Global Literacy Map (Continental Patterns)")
        # Map visualizing adult literacy for the selected year max
        map_df = lit_df[lit_df['YEAR'] == selected_years[1]].copy()
        if not map_df.empty:
            fig_map = px.choropleth(
                map_df, locations="COUNTRY", locationmode="country names",
                color="ADULT_LITERACY", hover_name="COUNTRY",
                color_continuous_scale=px.colors.sequential.YlGnBu,
                title=f"Adult Literacy Rates Worldwide ({selected_years[1]})",
                template="plotly_dark"
            )
            fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info(f"No global map data for {selected_years[1]}")

    with col2:
        st.subheader("2. Literacy vs Economic Indicators (GDP)")
        # Link between literacy and GDP per capita
        if not merged_df.empty:
            # Filter by selected year
            scatter_df = merged_df[(merged_df['YEAR'] >= selected_years[0]) & (merged_df['YEAR'] <= selected_years[1])]
            # Average over the years
            scatter_df = scatter_df.groupby('COUNTRY').mean(numeric_only=True).reset_index()
            fig_scatter = px.scatter(
                scatter_df, x="GDP_PCAP", y="ADULT_LITERACY",
                size="AVG_YEARS_OF_EDUCATION", color="REGION" if 'REGION' in scatter_df.columns else None,
                hover_name="COUNTRY", log_x=True, size_max=40,
                title=f"Literacy vs. GDP per Capita ({selected_years[0]}-{selected_years[1]})",
                labels={"GDP_PCAP": "GDP per Capita (Log)", "ADULT_LITERACY": "Adult Literacy %"},
                template="plotly_dark"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("3. Trend Comparison: Literate vs Illiterate Global Avg")
        # Ensure illit% is handled appropriately - assume there is an ILLITERACY% col
        illit_col = [c for c in illit_df.columns if 'ILLIT' in c.upper() and 'RATE' in c.upper() or '%' in c.upper()]
        if illit_col and not lit_df.empty:
            illit_c = illit_col[0]
            lit_trend = lit_df.groupby('YEAR')['ADULT_LITERACY'].mean().reset_index()
            illit_trend = illit_df.groupby('YEAR')[illit_c].mean().reset_index()
            
            trend_df = pd.merge(lit_trend, illit_trend, on='YEAR', how='inner')
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_df['YEAR'], y=trend_df['ADULT_LITERACY'], mode='lines', fill='tozeroy', name='Avg Adult Literacy (%)', line=dict(color='#00ff88')))
            fig_trend.add_trace(go.Scatter(x=trend_df['YEAR'], y=trend_df[illit_c], mode='lines', fill='tozeroy', name='Avg Illiteracy (%)', line=dict(color='#ff3366')))
            fig_trend.update_layout(title="Global Historical Trends: Literacy vs Illiteracy", template="plotly_dark")
            st.plotly_chart(fig_trend, use_container_width=True)

    with col4:
        st.subheader("4. Gender Disparities in Youth Literacy")
        if 'YOUTH_LITERACY_M' in lit_df.columns and 'YOUTH_LITERACY_F' in lit_df.columns:
            recent_lit = lit_df[lit_df['YEAR'] == selected_years[1]].copy()
            if not recent_lit.empty:
                recent_lit['GENDER_GAP'] = recent_lit['YOUTH_LITERACY_M'] - recent_lit['YOUTH_LITERACY_F']
                top_gaps = recent_lit.sort_values(by='GENDER_GAP', ascending=False).head(20)
                
                fig_gap = px.bar(
                    top_gaps, x="COUNTRY", y=["YOUTH_LITERACY_M", "YOUTH_LITERACY_F"],
                    barmode="group",
                    title=f"Top 20 Countries by Youth Gender Gap ({selected_years[1]})",
                    color_discrete_map={"YOUTH_LITERACY_M": "#3498db", "YOUTH_LITERACY_F": "#e74c3c"},
                    template="plotly_dark"
                )
                st.plotly_chart(fig_gap, use_container_width=True)
                
    # Row 3
    st.subheader("5. Schooling Years vs. Literacy Levels Heatmap (Top/Bottom Performers)")
    if not merged_df.empty:
        heat_df = merged_df[merged_df['YEAR'] == selected_years[1]].copy()
        if not heat_df.empty:
            heat_df = heat_df.sort_values(by="ADULT_LITERACY", ascending=False)
            top_bottom = pd.concat([heat_df.head(10), heat_df.tail(10)])
            
            fig_heat = px.density_heatmap(
                heat_df, x="AVG_YEARS_OF_EDUCATION", y="ADULT_LITERACY",
                color_continuous_scale="Viridis",
                title=f"Density of Literacy vs Schooling Years ({selected_years[1]})",
                template="plotly_dark"
            )
            st.plotly_chart(fig_heat, use_container_width=True)


# -----------------------------------------------------------------------------------------
# TAB 2: The 13 Specific SQL Queries
# -----------------------------------------------------------------------------------------
with tab_queries:
    st.header("Executive Summary: The 13 Requested Queries")
    st.markdown("Each query is executed dynamically directly from your MySQL server.")
    
    illit_col_name = "ILLITERACY%"
    illit_col2 = "ILLITERACY_RATE" # Some scripts used this.
    
    # We define the raw SQL dynamically so it behaves exactly as the markdown specified.
    queries_dict = {
        "1. Top 5 countries with highest adult literacy in 2020": 
            "SELECT COUNTRY, ADULT_LITERACY FROM LITERACY WHERE YEAR = 2020 ORDER BY ADULT_LITERACY DESC LIMIT 5;",
        "2. Countries where female youth literacy < 80%": 
            "SELECT COUNTRY, YEAR, YOUTH_LITERACY_F FROM LITERACY WHERE YOUTH_LITERACY_F < 80 LIMIT 50;",
        "3. Average adult literacy per continent (owid region)": 
            "SELECT REGION, AVG(ADULT_LITERACY) AS AVG_ADULT_LITERACY FROM LITERACY GROUP BY REGION;",
        "4. Countries with illiteracy % > 20% in 2000": 
            "SELECT COUNTRY, `ILLITERACY%` FROM ILLITERACY_POPULATION WHERE YEAR = 2000 AND `ILLITERACY%` > 20 LIMIT 50;",
        "5. Trend of illiteracy % for India (2000–2020)": 
            "SELECT YEAR, `ILLITERACY%` FROM ILLITERACY_POPULATION WHERE COUNTRY = 'India' AND YEAR BETWEEN 2000 AND 2020 ORDER BY YEAR;",
        "6. Top 10 countries with largest illiterate population in the last year": 
            "SELECT i.COUNTRY, i.YEAR, (i.`ILLITERACY%` / 100 * g.POPULATION) AS ILLITERATE_POPULATION FROM ILLITERACY_POPULATION i JOIN GDP_SCHOOLING g ON i.COUNTRY = g.COUNTRY AND i.YEAR = g.YEAR WHERE i.YEAR = (SELECT MAX(YEAR) FROM ILLITERACY_POPULATION) ORDER BY ILLITERATE_POPULATION DESC LIMIT 10;",
        "7. Countries with avg_years_schooling > 7 and gdp_per_capita < 5000": 
            "SELECT COUNTRY, YEAR, AVG_YEARS_OF_EDUCATION, GDP_PCAP FROM GDP_SCHOOLING WHERE AVG_YEARS_OF_EDUCATION > 7 AND GDP_PCAP < 5000 LIMIT 50;",
        "8. Rank countries by GDP per schooling for the year 2020": 
            "SELECT COUNTRY, `GDP PER SCHOOLING YEAR` FROM GDP_SCHOOLING WHERE YEAR = 2020 ORDER BY `GDP PER SCHOOLING YEAR` DESC LIMIT 50;",
        "9. Global average schooling years per year": 
            "SELECT YEAR, AVG(AVG_YEARS_OF_EDUCATION) AS GLOBAL_AVG_SCHOOLING FROM GDP_SCHOOLING GROUP BY YEAR ORDER BY YEAR;",
        "10. Top 10 countries in 2020 with high GDP per capita but avg schooling < 6": 
            "SELECT COUNTRY, GDP_PCAP, AVG_YEARS_OF_EDUCATION FROM GDP_SCHOOLING WHERE YEAR = 2020 AND AVG_YEARS_OF_EDUCATION < 6 ORDER BY GDP_PCAP DESC LIMIT 10;",
        "11. High illiterate population despite avg schooling > 6.5": 
            '''SELECT 
                COUNTRY,
                AVG_YEARS_OF_EDUCATION,
                POPULATION,
                (POPULATION * (100 - LITERACY_RATE) / 100) AS ILLITERATE_POPULATION
                FROM GDP_SCHOOLING
                WHERE AVG_YEARS_OF_EDUCATION > 6.5
                AND (POPULATION * (100 - LITERACY_RATE) / 100) > 1000000
                ORDER BY ILLITERATE_POPULATION DESC;''',
        "12. Literacy vs GDP per capita growth in a selected country (Last 20 Years)": 
            f"SELECT l.YEAR, l.ADULT_LITERACY, g.GDP_PCAP FROM LITERACY l JOIN GDP_SCHOOLING g ON l.COUNTRY = g.COUNTRY AND l.YEAR = g.YEAR WHERE l.COUNTRY = '{selected_country if selected_country != 'All Countries' else 'India'}' AND l.YEAR >= 2000 ORDER BY l.YEAR;",
        "13. Gender gap (Male vs Female youth literacy) for GDP > 30k in 2020": 
            "SELECT l.COUNTRY, g.GDP_PCAP, l.YOUTH_LITERACY_M, l.YOUTH_LITERACY_F, ABS(l.YOUTH_LITERACY_M - l.YOUTH_LITERACY_F) AS GENDER_GAP FROM LITERACY l JOIN GDP_SCHOOLING g ON l.COUNTRY = g.COUNTRY AND l.YEAR = g.YEAR WHERE l.YEAR = 2020 AND g.GDP_PCAP > 30000;"
    }
    
    # We visualize them in 2 columns
    q_cols = st.columns(2)
    col_idx = 0
    
    for title, q_sql in queries_dict.items():
        with q_cols[col_idx % 2]:
            st.markdown(f"**{title}**")
            
            # Execute query
            df_res = fetch_data(q_sql)
            
            # Fallback logic if ILLITERACY% fails due to schema name mismatch
            if df_res.empty and "Unknown column" in st.session_state.get('last_err', ''):
                pass # The generic fetch_data catches errors. We'll do a string replace hack cleanly.
                
            if "Unknown column 'ILLITERACY%'" in q_sql or (df_res.empty and 'ILLITERACY%' in q_sql):
                backup_sql = q_sql.replace("`ILLITERACY%`", "ILLITERACY_RATE")
                df_res_backup = fetch_data(backup_sql)
                if not df_res_backup.empty:
                    df_res = df_res_backup

            if df_res.empty:
                st.warning("Query returned no data or an error occurred. Verify the SQL table schemas.")
                with st.expander("Show SQL Syntax"):
                    st.code(q_sql, language="sql")
            else:
                st.dataframe(df_res, use_container_width=True)
                
                # Auto-generate a miniature chart for context
                if len(df_res) > 1 and len(df_res.columns) >= 2:
                    numeric_cols = df_res.select_dtypes(include='number').columns
                    if len(numeric_cols) > 0:
                        y_col = numeric_cols[-1]
                        x_col = df_res.columns[0]
                        # If a time-series
                        if 'YEAR' in df_res.columns:
                            fig = px.line(df_res, x='YEAR', y=y_col, markers=True, template="plotly_dark", height=250)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            plot_df = df_res.head(20)
                            fig = px.bar(plot_df, x=x_col, y=y_col, template="plotly_dark", height=250, color=y_col)
                            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
        col_idx += 1
