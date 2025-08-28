# University Prices vs Rankings Analysis

A comprehensive analysis of university tuition costs versus academic rankings for US and UK institutions, with sweet spot identification for value-conscious students.

## 🎯 Key Findings

**Sweet Spot Universities (Best Value):**
- **University of North Carolina Chapel Hill** - Rank 22, $7,019 (Score: 84.8)
- **UCLA** - Rank 15, $13,804 (Score: 84.6)
- **UC Berkeley** - Rank 15, $14,312 (Score: 84.3)
- **University of Florida** - Rank 28, $6,381 (Score: 82.1)

**Price-Ranking Correlations:**
- Overall: r = -0.536 (strong negative correlation)
- US: r = -0.574 (stronger price-ranking relationship)
- UK: r = -0.867 (very strong correlation)

## 📊 Dataset

- **Total**: 81 universities (41 US, 40 UK)
- **US Price Range**: $0 - $68,400 (mean: $34,815)
- **UK International Fees**: $16,446 - $48,133 (mean: $30,337)
- **Data Sources**: College Scorecard, Complete University Guide, Guardian Rankings

## 🚀 Quick Start

```bash
# Activate virtual environment
source ~/Work/venvs/.venv/bin/activate

# Collect US university data
python collect_us_data_v2.py

# Collect UK university data
python collect_uk_data.py

# Generate analysis and plots
python plot_analysis.py

# Find sweet spot universities
python find_sweet_spot.py

# Validate data quality
python test_data_quality.py
```

## 📈 Generated Visualizations

1. **university_price_vs_ranking_scatter.png** - Main correlation plot with regression lines
2. **university_distributions_boxplot.png** - Price/ranking distributions by country
3. **university_density_plots.png** - Density distributions
4. **university_sweet_spot_analysis.png** - Value quadrants and top universities

## 🗂️ Files Overview

### Data Collection
- `collect_us_data_v2.py` - US university data collection with sample dataset
- `collect_uk_data.py` - UK university data collection with sample dataset

### Analysis Scripts
- `plot_analysis.py` - Main analysis script with correlation analysis and plots
- `find_sweet_spot.py` - Value analysis and sweet spot identification
- `test_data_quality.py` - Data validation and quality testing

### Data Files
- `us_universities_sample.csv` - US university dataset (41 institutions)
- `uk_universities_sample.csv` - UK university dataset (40 institutions)  
- `combined_university_data.csv` - Combined analysis dataset
- `university_value_analysis.csv` - Sweet spot analysis results

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