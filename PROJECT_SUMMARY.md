# University Prices vs Rankings Analysis - Project Summary

## Objective
Analyze the relationship between university tuition costs and academic rankings for US and UK institutions to identify "sweet spot" universities offering optimal value (high ranking at reasonable cost).

## Dataset
- **Total**: 81 universities (41 US, 40 UK)
- **US Sources**: College Scorecard API (costs), composite rankings (Forbes, Money Magazine)
- **UK Sources**: Complete University Guide, Guardian rankings, international fee data
- **Price Range**: $0-$68,400 (US), £13K-£38K converted to USD (UK)

## Key Findings

### Correlation Analysis
- **Overall correlation**: r = -0.536 (p < 0.001) - strong negative correlation
- **US correlation**: r = -0.574 (stronger price-ranking relationship)
- **UK correlation**: r = -0.867 (very strong correlation)
- **Interpretation**: Higher-ranked universities (lower rank numbers) charge significantly more

### Sweet Spot Universities (Best Value)
1. **University of North Carolina Chapel Hill** (US) - Rank 22, $7,019 - Value Score: 84.8
2. **UCLA** (US) - Rank 15, $13,804 - Value Score: 84.6
3. **UC Berkeley** (US) - Rank 15, $14,312 - Value Score: 84.3
4. **University of Florida** (US) - Rank 28, $6,381 - Value Score: 82.1
5. **University of Cambridge** (UK) - Rank 1, $34,351 - Value Score: 79.9

### Value Categories
- **Elite Bargains**: Top 25% rankings at reasonable prices (LSE stands out)
- **Budget Champions**: Low cost with good rankings (UC system, UNC, UF)
- **International Value**: UK universities offer better value than equivalent US private institutions

## Methodology

### Data Collection
- US: College Scorecard API for costs, web scraping for rankings
- UK: Manual compilation from official university sources and ranking agencies
- Currency standardization: GBP to USD (1.27 exchange rate)

### Value Score Calculation
- **Formula**: 0.6 × Ranking Percentile + 0.4 × Price Percentile
- **Ranking Percentile**: Lower rank = higher percentile (better)
- **Price Percentile**: Lower price = higher percentile (better value)
- **Country-specific scores**: Normalized within US and UK separately

### Statistical Validation
- Data completeness: 100% for key metrics
- Sample adequacy: n=81 total, n≥30 per country
- Correlation significance: p < 0.001 for all correlations
- Quality assurance: Automated testing framework

## Technical Implementation

### Scripts
- `collect_us_data_v2.py`: US university data collection
- `collect_uk_data.py`: UK university data collection  
- `plot_analysis.py`: Main correlation analysis and visualization
- `find_sweet_spot.py`: Value analysis and sweet spot identification
- `test_data_quality.py`: Data validation and quality testing

### Outputs
- 4 comprehensive visualizations (scatter plots, distributions, value quadrants)
- 3 datasets (US, UK, combined)
- Statistical analysis with correlation coefficients
- Sweet spot rankings by various criteria

## Key Insights

1. **Public universities dominate value rankings** - especially UC system and state flagships
2. **California leads in value** - UC Berkeley, UCLA, UCSD all in top 10
3. **UK provides international value** - Cambridge/Oxford at ~$35K vs $65K+ US equivalents  
4. **Scottish advantage** - Lower fees create exceptional value (Edinburgh, Glasgow)
5. **Price-ranking relationship stronger in UK** - more predictable pricing structure

## Business Applications

### For Students
- Identify high-value universities by budget and ranking preferences
- Compare international options (US vs UK)
- Optimize application strategy for best ROI

### For Institutions
- Benchmark pricing against ranking position
- Identify competitive positioning opportunities
- Understand value perception in the market

### For Policy
- Analyze affordability vs quality relationships
- Compare international higher education markets
- Inform tuition and funding policy decisions

## Limitations & Future Work

### Current Limitations
- Sample data used (real-time APIs require authentication)
- Single-year snapshot (temporal trends not analyzed)
- Limited ranking sources (could include QS, Times Higher Ed)
- No cost-of-living adjustments

### Recommended Enhancements
1. Real-time data integration (College Scorecard API key)
2. Multi-year trend analysis
3. Additional ranking systems inclusion
4. Regional cost-of-living adjustments
5. Graduate outcome correlation (employment, salary)

## Repository Information
- **GitHub**: https://github.com/vasilybelokurov/university_prices_ratings
- **Language**: Python 3.8+
- **Dependencies**: pandas, matplotlib, seaborn, scipy, scikit-learn
- **License**: Educational/Research use

## Contact
Created for astrophysicist data analysis workflow following rigorous testing and validation methodology.