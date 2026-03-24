# 🌍 Global Literacy & Education Trends

## 📖 Overview
The **Global Literacy & Education Trends** project is an end-to-end data analytics pipeline designed to explore the historical and contemporary trends in global literacy, demographic education, and their socioeconomic correlations (such as GDP per capita). The project demonstrates a complete lifecycle from raw data sourcing to interactive dashboard deployment.

## 🗂️ Project Structure

- **`data/`**: Contains the raw and processed datasets (CSV files) utilized throughout the analytical phases.
- **`notebooks/`**: The core data science workspace.
  - `Data_sourcing.ipynb` & `Data_cleaning.ipynb`: Initial extraction, transformation, and cleaning of historical data.
  - `feature_engineering.ipynb`: Generates specialized aggregated metrics (e.g., 'GDP per Schooling Year', 'Education Index', 'Literacy Growth Rate', 'Gender Gap').
  - `eda_analysis.ipynb`: Conducts comprehensive Univariate and Bivariate analysis, complete with documented insights.
  - `sql.ipynb` / `sql.md`: Database schema modeling, connection establishment, and exploratory SQL queries.
- **`src/`**: Contains the production-level code.
  - `app.py`: An interactive **Streamlit** dashboard that seamlessly connects to the MySQL backend to visualize demographic and economic disparities.
- **`global_literacy_education_trends.pbix`**: A **Power BI** dashboard offering an alternative, highly interactive business intelligence perspective on the data.
- **`requirements.txt`**: Standard Python project dependencies.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL Server (running locally or remotely)
- Power BI Desktop (optional, for viewing the `.pbix` dashboard)

### Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Global_Literacy_Education_Trends
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Primary packages include: `pandas`, `streamlit`, `sqlalchemy`, `pymysql`, `plotly`, `jupyter`)*

3. **Database Configuration:**
   - Ensure your MySQL server is active. By default, the Streamlit app looks for a database named `global_literacy_education_trends` on `localhost:3306`.
   - Execute the Jupyter Notebooks sequentially to process the raw data and load it into your local MySQL instance.

## 📊 Running the Visualizations

### Streamlit Dashboard
To launch the interactive Python dashboard, open your terminal and run:
```bash
cd src
python -m streamlit run app.py
```
The Streamlit app features deep-dive insights including:
- **Global Literacy Maps** (Continental Patterns)
- **Literacy vs. Economic Indicators** (GDP per capita)
- **Trend Comparisons** (Historical Literacy vs. Illiteracy)
- **Gender Disparity Analysis**
- **Dynamic SQL Query Executor** mapped to 13 specific analytical business questions.

## 🛠️ Built With
- **Python Data Stack:** Pandas, Jupyter
- **Database:** MySQL, SQLAlchemy, PyMySQL
- **Visualization:** Streamlit, Plotly