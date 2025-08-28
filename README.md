# University Prices vs Rankings Analysis

A comprehensive analysis of university tuition costs versus academic quality for US universities, using **real data** from official US Department of Education sources. This project analyzes 1,206 universities with complete tuition and quality metrics data.

## 🎯 Key Findings (1,206 Real Universities)

**Strong Quality-Price Correlation:**
- **Pearson correlation**: r = -0.741 (p < 0.001) - **Highly Significant**
- **Interpretation**: Higher quality universities charge significantly more tuition
- **1,206 universities** analyzed with complete real data

**Top Quality Universities:**
- **Massachusetts Institute of Technology** - Quality Score: 85.7, Price: $60,156
- **California Institute of Technology** - Quality Score: 83.7, Price: $63,255  
- **Hillsdale College** - Quality Score: 83.3, Price: $32,092
- **University of Pennsylvania** - Quality Score: 81.6, Price: $66,104
- **University of Notre Dame** - Quality Score: 80.7, Price: $62,693

**Sweet Spot Universities (High Quality + Reasonable Price ≤ $30,297):**
- **Grove City College (PA)** - Quality Rank: 50, Price: $20,890
- **Binghamton University (NY)** - Quality Rank: 89, Price: $29,453
- **University of Florida (FL)** - Quality Rank: 98, Price: $28,659
- **University of Georgia (GA)** - Quality Rank: 121, Price: $30,220
- **Brigham Young University (UT)** - Quality Rank: 293, Price: $6,496

**Best Value Universities (Quality per Dollar):**
- **Hillsdale College (MI)** - Value Score: 75.6
- **Grove City College (PA)** - Value Score: 74.1
- **Georgia Institute of Technology (GA)** - Value Score: 67.0
- **Florida State University (FL)** - Value Score: 67.0
- **Brigham Young University (UT)** - Value Score: 66.6

## 📊 Dataset (Real College Scorecard Data)

- **Total**: 1,206 US universities with complete data
- **Price Range**: $4,656 - $69,330 (median: $30,297)
- **Quality Metrics**: 9 comprehensive indicators from College Scorecard API
- **Data Sources**: 
  - **Tuition Data**: College Scorecard API (US Department of Education)
  - **Quality Rankings**: Custom system using College Scorecard academic metrics
  - **No external ranking dependencies**: All data from official US government API

## 🚀 Quick Start (Real Data Pipeline)

```bash
# Create and activate project virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Get your free College Scorecard API key from api.data.gov
# API key is hardcoded in scripts for demonstration

# METHOD 1: Run complete analysis with quality rankings (RECOMMENDED)
python implement_scorecard_ranking_system.py  # Collect 1,206 universities with quality metrics
python final_analysis_scorecard_rankings.py   # Comprehensive analysis and visualizations

# METHOD 2: Test quality metrics investigation
python investigate_scorecard_quality_metrics.py  # Explore available quality indicators

# METHOD 3: Bulk data collection only
python get_bulk_scorecard_data.py  # Get 1,200+ universities with tuition data only
```

## 📈 Generated Visualizations

### College Scorecard Analysis (1,206 Universities)
1. **comprehensive_scorecard_analysis.png** - Complete 6-panel analysis:
   - Main scatter plot: Quality ranking vs tuition price (r = -0.741)
   - Price distribution histogram 
   - Quality score distribution
   - Top 10 states by university count
   - Price vs quality score correlation
   - Color-coded by quality scores

### Generated Data Files
- **scorecard_universities_with_quality_rankings.csv** - Complete dataset (1,206 universities)
- **sweet_spot_universities_scorecard.csv** - High quality + reasonable price universities
- **best_value_universities_scorecard.csv** - Best value rankings (quality per dollar)
- **complete_analysis_scorecard.csv** - Full analysis results

## 🗂️ Files Overview

### Main Analysis Pipeline (1,206 Universities)
- `implement_scorecard_ranking_system.py` - **Primary pipeline**: Collect universities with quality metrics
- `final_analysis_scorecard_rankings.py` - **Main analysis**: Comprehensive statistics and visualizations
- `investigate_scorecard_quality_metrics.py` - Quality metrics exploration and validation

### Data Collection Scripts
- `get_bulk_scorecard_data.py` - Bulk tuition data collection (1,200+ universities)
- `get_arwu_rankings_working.py` - ARWU rankings from ShanghaiRanking API
- `get_complete_arwu_2023.py` - Complete ARWU dataset collection

### Quality Assurance
- `verify_real_data.py` - Data authenticity verification
- `test_data_quality.py` - Data quality testing suite

### Legacy/Alternative Approaches
- `collect_real_data.py` - Early ARWU + College Scorecard combination approach
- `get_rankings_wikipedia.py` - Wikipedia ranking scraping (deprecated - 403 errors)

### Main Dataset Files
- `scorecard_universities_with_quality_rankings.csv` - **Primary dataset** (1,206 universities)
- `sweet_spot_universities_scorecard.csv` - Sweet spot universities
- `best_value_universities_scorecard.csv` - Best value universities
- `complete_analysis_scorecard.csv` - Full analysis results

### Configuration
- `CLAUDE.md` - Project instructions and working agreement
- `requirements.txt` - Python dependencies

## 🔬 Methodology

**Quality Ranking System (College Scorecard Metrics):**
- **Academic Selectivity (30%)**: SAT scores, ACT scores, admission rates
- **Student Outcomes (40%)**: 4-year completion rates, median earnings, retention rates
- **Student Quality (20%)**: Part-time share, Pell grant rates
- **Financial Health (10%)**: Loan repayment rates

**Value Score Calculation:**
- 70% quality score weight (College Scorecard derived quality ranking)
- 30% price affordability weight (normalized price score)
- All metrics normalized to 0-100 scale for fair comparison

**Data Validation:**
- Real data only - no approximations or synthetic data
- Quality metrics require ≥5 of 9 indicators per university
- Statistical significance testing (p < 0.001 achieved)
- Cross-validation with official Department of Education sources

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

- **Strong quality-price correlation**: r = -0.741 (higher quality = higher price)
- **Public universities dominate value rankings**: Florida State, Georgia Tech, BYU lead
- **Elite private institutions** justify premium pricing with superior quality scores
- **Regional patterns**: Florida and New York universities offer exceptional value
- **Sweet spot strategy**: Target quality rank ≤300 with price ≤$30,297 median

## 📞 Usage Notes

This analysis uses **real College Scorecard data** for 1,206 universities. The system:
1. Eliminates dependency on external ranking APIs (QS, Times, etc.)
2. Uses comprehensive US Department of Education quality metrics  
3. Provides reproducible analysis with publicly available data
4. Achieves statistical significance with large sample size (p < 0.001)

## 📄 License

This project is for educational and research purposes.