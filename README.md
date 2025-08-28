# University Prices vs Rankings Analysis

A comprehensive analysis of university tuition costs versus academic rankings for US and UK institutions, using **real data** from official sources, with sweet spot identification for value-conscious students.

## 🎯 Key Findings (Real Data)

**Sweet Spot Universities (Best Value - Real Data):**
- **University of Chicago** - Rank 9, $14,338 (Score: 93.8)
- **University of Wisconsin - Madison** - Rank 25, $11,205 (Score: 91.2)
- **University of North Carolina at Chapel Hill** - Rank 32, $8,989 (Score: 90.7)
- **California Institute of Technology** - Rank 8, $20,515 (Score: 89.8)

**Elite Bargains (Top Rankings + Reasonable Price):**
- **California Institute of Technology** - ARWU Rank 8, $20,515
- **University of Chicago** - ARWU Rank 9, $14,338

**Price-Ranking Correlations (Real Data):**
- Overall: r = -0.256 (weak correlation, p = 0.144)
- US: r = -0.321 (moderate, but not significant p = 0.226)
- UK: r = -0.569 (strong significant correlation, p = 0.014)

## 📊 Dataset (Real Data)

- **Total**: 34 universities with complete data (16 US, 18 UK)
- **US Price Range**: $8,989 - $65,805 (mean: $41,464)
- **UK International Fees**: $29,718 - $48,133 (mean: $34,295)
- **Data Sources**: 
  - **Rankings**: ARWU 2023 (Academic Ranking of World Universities)
  - **US Tuition**: College Scorecard API (US Department of Education)
  - **UK Fees**: Official university rates + international student fees

## 🚀 Quick Start (Real Data Pipeline)

```bash
# Create and activate project virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set your College Scorecard API key (get free key from api.data.gov)
export COLLEGE_SCORECARD_API_KEY="your_key_here"

# Collect real university data (ARWU + College Scorecard)
python collect_real_data.py

# Analyze real data with correlations and statistics
python analyze_real_data.py

# Find sweet spot universities with real data
python real_sweet_spot_analysis.py

# Alternative: Use sample data (no API key required)
python collect_us_data_v2.py  # Sample US data
python collect_uk_data.py     # Sample UK data
python plot_analysis.py       # Sample data analysis
```

## 📈 Generated Visualizations

### Real Data Analysis
1. **real_data_scatter_plot.png** - ARWU rankings vs College Scorecard tuition costs
2. **real_data_analysis_summary.png** - Comprehensive statistical summary
3. **real_sweet_spot_analysis.png** - Value quadrants and sweet spot identification

### Sample Data Analysis (for comparison)
4. **university_price_vs_ranking_scatter.png** - Sample data correlation plot
5. **university_distributions_boxplot.png** - Sample price/ranking distributions  
6. **university_density_plots.png** - Sample density distributions
7. **university_sweet_spot_analysis.png** - Sample value analysis

## 🗂️ Files Overview

### Real Data Collection
- `collect_real_data.py` - **Main data pipeline** using ARWU + College Scorecard API
- `analyze_real_data.py` - Statistical analysis of real university data
- `real_sweet_spot_analysis.py` - Sweet spot identification with real data

### Sample Data Collection (for comparison)
- `collect_us_data_v2.py` - US university sample data collection
- `collect_uk_data.py` - UK university sample data collection
- `plot_analysis.py` - Sample data analysis and visualization
- `find_sweet_spot.py` - Sample data sweet spot analysis

### Data Files (Real Data)
- `real_university_data.csv` - **Main dataset** (34 universities with complete data)
- `real_value_analysis.csv` - Real data value scores and rankings

### Data Files (Sample Data)
- `us_universities_sample.csv` - US sample dataset (41 institutions)
- `uk_universities_sample.csv` - UK sample dataset (40 institutions)  
- `combined_university_data.csv` - Combined sample dataset

### Configuration
- `CLAUDE.md` - Project instructions and methodology
- `requirements.txt` - Python dependencies

## 🔬 Methodology

**Value Score Calculation:**
- 60% ranking weight (lower rank = better)
- 40% price weight (lower price = better) 
- Normalized to percentiles within each metric
- Separate country-specific value scores

**Data Quality Tests:**
- File existence verification
- Data completeness validation
- Statistical validity checks
- Plot generation confirmation

## 📋 Requirements

```
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
requests>=2.28.0
scikit-learn>=1.1.0
scipy>=1.9.0
```

## 🎓 Key Insights

- **Public universities** generally offer superior value
- **UC system** dominates value rankings for quality + affordability
- **UK universities** provide better international value than equivalent US private institutions
- **Scottish universities** offer exceptional value due to lower fee structure
- Strong correlation between higher rankings and higher prices in both countries

## 📞 Usage Notes

This analysis uses sample data for demonstration. For production use:
1. Obtain College Scorecard API key for real-time US data
2. Implement web scraping for current UK university fees
3. Add additional ranking systems (Times Higher Education, QS)
4. Include cost-of-living adjustments for regional analysis

## 📄 License

This project is for educational and research purposes.