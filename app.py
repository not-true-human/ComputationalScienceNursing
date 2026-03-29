import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
import io

# Configure page
st.set_page_config(
    page_title="STI Knowledge Research Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

#background image
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main {{
            background-color: rgba(248, 249, 250, 0.85);
        }}
        </style>
    """, unsafe_allow_html=True)
set_background("Background.jpg")

# Add custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    section[data-testid="stSidebar"] {
    background-color: rgba(0, 0, 0, 0.65) !important;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .header-title {
        color: #1f4788;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .header-subtitle {
        color: #666;
        font-size: 14px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA GATHERED
# ============================================================================

@st.dialog("📂 Upload Your Data File")
def upload_dialog():
    st.markdown("""
    ### Instructions
    **Your file must have these exact column names:**
    
    | Column | Description | Example |
    |---|---|---|
    | `Age` | Age in years | 22 |
    | `Gender` | Male or Female | Female |
    | `Knowledge_Score` | Score 0-100 | 75.5 |
    | `Knowledge_Level` | Have / Moderate / Least Knowledge | Have Knowledge |
    | `Information_Source` | Source of info | Social Media |
    
    **Accepted formats:** `.csv` or `.xlsx`
    """)
    
    uploaded_file = st.file_uploader(
        "Choose your file",
        type=["csv", "xlsx", "xls"]
    )
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        df.insert(0, 'Respondent_ID', [f"{i:04d}" for i in range(1, len(df) + 1)])
        st.session_state['data'] = df
        st.success(f"✅ Successfully loaded {len(df)} records!")
        st.rerun()

# Sidebar upload button
st.sidebar.markdown("### 📂 Data Source")
if st.sidebar.button("📤 Upload Data File"):
    upload_dialog()

# Load data from session or show warning
if 'data' in st.session_state:
    df = st.session_state['data']
else:
    st.warning("⬆️ Please upload a data file using the button in the sidebar to begin.")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="header-title">🏥 STI Knowledge Research Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown(
        '<div class="header-subtitle">Gender Disparities in Knowledge of STIs among Out-of-School Youth | '
        'Mabini Colleges, Inc. - College of Computer Studies</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

st.divider()

# ============================================================================
# INTERACTIVE FILTERS
# ============================================================================

st.markdown("### 🔍 Interactive Filters")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    selected_gender = st.multiselect(
        "Select Gender",
        options=df['Gender'].unique(),
        default=df['Gender'].unique(),
        key="gender_filter"
    )

with filter_col2:
    selected_age_group = st.multiselect(
        "Select Age Group",
        options=['17-20', '21-25'],
        default=['17-20', '21-25'],
        key="age_filter"
    )


with filter_col3:
    selected_knowledge = st.multiselect(
        "Select Knowledge Level",
        options=df['Knowledge_Level'].unique(),
        default=df['Knowledge_Level'].unique(),
        key="knowledge_filter"
    )

with filter_col4:
    selected_info_source = st.multiselect(
        "Select Information Source",
        options=df['Information_Source'].unique(),
        default=df['Information_Source'].unique(),
        key="source_filter"
    )

df['Age_Group'] = pd.cut(df['Age'],
                        bins=[16, 20, 25],
                        labels=['17-20', '21-25'])
# Apply filters
filtered_df = df[
    (df['Gender'].isin(selected_gender)) &
    (df['Age_Group'].isin(selected_age_group)) &
    (df['Knowledge_Level'].isin(selected_knowledge)) &
    (df['Information_Source'].isin(selected_info_source))
]

# Display filter info
filter_info_col1, filter_info_col2, filter_info_col3 = st.columns([2, 1, 1])
with filter_info_col1:
    st.info(f"📊 Showing {len(filtered_df)} of {len(df)} respondents")

st.divider()

# ============================================================================
# SIDEBAR - RESPONDENT LIST
# ============================================================================

st.sidebar.markdown("### 📋 Respondent List")
st.sidebar.markdown(f"**Total: {len(filtered_df)} respondents**")
st.sidebar.divider()

# Create display-friendly dataframe
display_df = filtered_df.copy()
display_df['Knowledge_Score'] = display_df['Knowledge_Score'].round(1)
display_df = display_df.sort_values('Respondent_ID')

# Rename columns for better display
display_df_renamed = display_df.rename(columns={
    'Respondent_ID': 'ID',
    'Age': 'Age',
    'Gender': 'Gender',
    'Knowledge_Score': 'Score',
    'Knowledge_Level': 'Knowledge',
    'Information_Source': 'Info Source'
})

# Create a compact table view in the sidebar
st.sidebar.dataframe(
    display_df_renamed[['ID', 'Age', 'Gender', 'Score']],
    height=500,
    column_config={
        'ID': st.column_config.TextColumn(width='small'),
        'Age': st.column_config.NumberColumn(width='small'),
        'Gender': st.column_config.TextColumn(width='small'),
        'Score': st.column_config.NumberColumn(width='small'),
    },
    hide_index=True
)

st.sidebar.divider()

# ============================================================================
# SIDEBAR - DOWNLOAD REPORT
# ============================================================================

st.sidebar.markdown("### 📥 Download Report")

# Build summary report data
male_avg = filtered_df[filtered_df['Gender'] == 'Male']['Knowledge_Score'].mean()
female_avg = filtered_df[filtered_df['Gender'] == 'Female']['Knowledge_Score'].mean()
highest_gender = 'Male' if male_avg > female_avg else 'Female'
lowest_gender = 'Female' if male_avg > female_avg else 'Male'

age_group_counts = filtered_df['Age_Group'].value_counts()
majority_age = age_group_counts.idxmax() if len(age_group_counts) > 0 else 'N/A'

knowledge_dist = filtered_df['Knowledge_Level'].value_counts()

summary_data = {
    'Report Item': [
        '--- GENERAL ---',
        'Total Respondents',
        'Majority Age Group',
        'Average Age',
        '',
        '--- KNOWLEDGE SCORE ---',
        'Overall Average Score',
        'Standard Deviation',
        'Highest Score',
        'Lowest Score',
        '',
        '--- KNOWLEDGE LEVEL ---',
        'Have Knowledge',
        'Moderate Knowledge',
        'Least Knowledge',
        '',
        '--- GENDER ANALYSIS ---',
        'Male Average Score',
        'Female Average Score',
        'Highest Knowledge Gender',
        'Lowest Knowledge Gender',
        '',
        '--- INFORMATION SOURCE ---',
    ],
    'Value': [
        '',
        len(filtered_df),
        str(majority_age),
        round(filtered_df['Age'].mean(), 1),
        '',
        '',
        round(filtered_df['Knowledge_Score'].mean(), 1),
        round(filtered_df['Knowledge_Score'].std(), 2),
        round(filtered_df['Knowledge_Score'].max(), 1),
        round(filtered_df['Knowledge_Score'].min(), 1),
        '',
        '',
        knowledge_dist.get('Have Knowledge', 0),
        knowledge_dist.get('Moderate Knowledge', 0),
        knowledge_dist.get('Least Knowledge', 0),
        '',
        '',
        round(male_avg, 1) if not pd.isna(male_avg) else 'N/A',
        round(female_avg, 1) if not pd.isna(female_avg) else 'N/A',
        highest_gender,
        lowest_gender,
        '',
        '',
    ]
}

# Add information sources dynamically
source_dist = filtered_df['Information_Source'].value_counts()
for source, count in source_dist.items():
    pct = round((count / len(filtered_df) * 100), 1)
    summary_data['Report Item'].append(source)
    summary_data['Value'].append(f"{count} ({pct}%)")

report_df = pd.DataFrame(summary_data)

# CSV download
csv_report = report_df.to_csv(index=False)
st.sidebar.download_button(
    label="📥 Download Report (CSV)",
    data=csv_report,
    file_name=f"STI_Summary_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv"
)

# Excel download
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    report_df.to_excel(writer, sheet_name='Summary Report', index=False)

st.sidebar.download_button(
    label="📊 Download Report (Excel)",
    data=excel_buffer.getvalue(),
    file_name=f"STI_Summary_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
########################################
# ============================================================================
# MAIN LAYOUT - VISUALIZATIONS & STATISTICS
# ============================================================================

viz_col, stats_col = st.columns([3.5, 3])

# ========================================================================
# VISUALIZATIONS COLUMN (MIDDLE)
# ========================================================================

with viz_col:
    st.markdown("### 📈 Visualization Analysis")
    
    # Row 1: Knowledge Distribution Charts
    viz1_col, viz2_col = st.columns(2)
    
    with viz1_col:
        st.markdown("#### Knowledge Level Distribution")
        knowledge_counts = filtered_df['Knowledge_Level'].value_counts()
        colors_knowledge = ['#2ecc71', '#f39c12', '#e74c3c']
        
        fig_knowledge = go.Figure(data=[go.Bar(
            x=knowledge_counts.index,
            y=knowledge_counts.values,
            marker=dict(color=colors_knowledge, line=dict(color='white', width=2)),
            text=knowledge_counts.values,
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
        fig_knowledge.update_layout(
            height=350,
            title_font_size=14,
            xaxis_title="Knowledge Level",
            yaxis_title="Number of Respondents",
            template="plotly_white",
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False
        )
        st.plotly_chart(fig_knowledge, width='stretch')
    
    with viz2_col:
        st.markdown("#### Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts()
        colors_gender = ['#3498db', '#e91e63']
        
        fig_gender = go.Figure(data=[go.Pie(
            labels=gender_counts.index,
            values=gender_counts.values,
            hole=0.4,
            marker=dict(colors=colors_gender, line=dict(color='white', width=2)),
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig_gender.update_layout(
            height=350,
            title_font_size=14,
            template="plotly_white",
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_gender, width='stretch')
    
    # Row 2: Gender vs Knowledge Level
    st.markdown("#### Gender Comparison across Knowledge Levels")
    
    gender_knowledge = pd.crosstab(filtered_df['Knowledge_Level'], filtered_df['Gender'])
    
    fig_grouped = go.Figure()
    
    for gender in gender_knowledge.columns:
        fig_grouped.add_trace(go.Bar(
            x=gender_knowledge.index,
            y=gender_knowledge[gender],
            name=gender,
            marker=dict(color='#3498db' if gender == 'Male' else '#e91e63'),
            text=gender_knowledge[gender],
            textposition='outside',
            hovertemplate=f'<b>{gender}</b><br>%{{x}}<br>Count: %{{y}}<extra></extra>'
        ))
    
    fig_grouped.update_layout(
        height=350,
        barmode='group',
        xaxis_title="Knowledge Level",
        yaxis_title="Number of Respondents",
        template="plotly_white",
        hovermode='x unified',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_grouped, width='stretch')
    
    # Row 3: Information Source Impact
    st.markdown("#### Information Source Distribution")
    
    source_counts = filtered_df['Information_Source'].value_counts()
    colors_source = ['#9b59b6', '#1abc9c', '#f39c12', '#e67e22', '#34495e']
    
    fig_source = go.Figure(data=[go.Bar(
        y=source_counts.index,
        x=source_counts.values,
        orientation='h',
        marker=dict(color=colors_source[:len(source_counts)], line=dict(color='white', width=2)),
        text=source_counts.values,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    )])
    fig_source.update_layout(
        height=300,
        xaxis_title="Number of Respondents",
        yaxis_title="Information Source",
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False
    )
    st.plotly_chart(fig_source, width='stretch')
    
    # Row 4: Age vs Knowledge Score Scatter
    st.markdown("#### Age vs Knowledge Score (Trend Analysis)")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='Age',
        y='Knowledge_Score',
        color='Gender',
        size='Knowledge_Score',
        hover_data={'Age': True, 'Knowledge_Score': ':.1f', 'Gender': True},
        color_discrete_map={'Male': '#3498db', 'Female': '#e91e63'}
    )
    fig_scatter.update_layout(
        height=350,
        xaxis_title="Age (Years)",
        yaxis_title="Knowledge Score (0-100)",
        template="plotly_white",
        hovermode='closest',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_scatter, width='stretch')

# ========================================================================
# STATISTICS COLUMN (RIGHT)
# ========================================================================

with stats_col:
    st.markdown("### 📊 Statistical Computations")
    
    # Overall Statistics
    st.markdown("#### Overall Statistics")
    
    total_respondents = len(filtered_df)
    avg_age = filtered_df['Age'].mean()
    avg_score = filtered_df['Knowledge_Score'].mean()
    std_score = filtered_df['Knowledge_Score'].std()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Respondents", total_respondents, delta=None)
    col2.metric("Average Age", f"{avg_age:.1f}", delta=None)
    
    col1.metric("Avg Score", f"{avg_score:.1f}", delta=None)
    col2.metric("Std Deviation", f"{std_score:.2f}", delta=None)
    
    # Show computation
    with st.expander("📐 How are these calculated?", expanded=False):
        st.markdown("""
**Total Respondents:**
```
Count of all records matching filters
```

**Average Age:**
```
Sum of all ages / Total count
= {} / {}
= {:.1f}
```

**Average Knowledge Score:**
```
Sum of all scores / Total count
= {} / {}
= {:.1f}
```

**Standard Deviation:**
```
√(Σ(x - mean)² / n)
= {:.2f}
```
        """.format(
            int(filtered_df['Age'].sum()),
            total_respondents,
            avg_age,
            filtered_df['Knowledge_Score'].sum(),
            total_respondents,
            avg_score,
            std_score
        ))
    
    st.divider()
    
    # Gender Statistics
    st.markdown("#### Gender Analysis")
    gender_stats = filtered_df.groupby('Gender').agg({
        'Knowledge_Score': ['mean', 'count']
    }).round(2)
    
    gender_stats.columns = ['Avg Score', 'Count']
    
    for gender in gender_stats.index:
        score = gender_stats.loc[gender, 'Avg Score']
        count = int(gender_stats.loc[gender, 'Count'])
        pct = (count / total_respondents * 100) if total_respondents > 0 else 0
        
        st.metric(
            f"👤 {gender}",
            f"{score:.1f}",
            f"{count} ({pct:.1f}%)"
        )
    
    with st.expander("📐 Calculation", expanded=False):
        st.markdown("""
**Gender-wise Average Score:**
```
Male: Sum of Male scores / Male count
Female: Sum of Female scores / Female count
```
        """)
    
    st.divider()
    
    # Knowledge Level Breakdown
    st.markdown("#### Knowledge Level Distribution")
    knowledge_dist = filtered_df['Knowledge_Level'].value_counts()
    
    for level in ['Have Knowledge', 'Moderate Knowledge', 'Least Knowledge']:
        if level in knowledge_dist.index:
            count = knowledge_dist[level]
            pct = (count / total_respondents * 100) if total_respondents > 0 else 0
            st.metric(level, count, f"{pct:.1f}%")
    
    st.divider()
    
    # Age Group Analysis
    st.markdown("#### By Age Group")
    age_means = filtered_df.groupby('Age_Group', observed=True)['Knowledge_Score'].mean().round(1)
    for age_group, score in age_means.items():
        st.metric(f"Age {age_group}", f"{score:.1f}", delta=None)
    
    st.divider()
    
    # Source Distribution
    st.markdown("#### Primary Information Sources")
    source_dist = filtered_df['Information_Source'].value_counts()
    
    for source, count in source_dist.head(4).items():
        pct = (count / total_respondents * 100) if total_respondents > 0 else 0
        st.write(f"**{source}:** {count} ({pct:.1f}%)")
# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Research Project Information**
- **Project Title:** Gender Disparities in Knowledge of STIs among Out-of-School Youth
- **Department Advisor:** Dr. Caridad D. Garcia
- **Partner Department:** College of Nursing (CON)
- **Institution:** Mabini Colleges, Inc., Daet, Camarines Norte

*This dashboard is an interactive visualization tool for data analysis and presentation.*
""")
