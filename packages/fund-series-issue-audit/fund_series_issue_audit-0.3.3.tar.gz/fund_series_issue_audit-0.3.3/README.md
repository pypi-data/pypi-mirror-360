# Fund Series Issue Audit

A Python package for auditing and analyzing fund series issues. This package provides efficient tools for fund series issue auditing through portfolio vector comparison, asset composition validation, investor data analysis, and more.

## Version 0.3.0 Updates

- Added functional composition approach for filter implementation
- Created new audit_filter package for improved filter management
- Enhanced utility functions with clearer separation of filtering processes
- Added functionals.py for functional programming utilities
- Improved class implementations using new utility functions

## Version 0.2.9 Updates

- Added FullAudit class for comprehensive fund pair analysis
- Implemented full audit functionality without filtering constraints
- Added utility functions for generating and loading full audit results
- Enhanced comparison capabilities for all fund combinations

## Version 0.2.8 Updates

- Added SeriesIssueAudit class for object-oriented audit management
- Refactored code structure for better maintainability
- Improved dependency management with updated package versions
- Enhanced result comparison functionality

## Version 0.2.7 Updates

- Enhanced threshold application feature for automated audit results
- Improved result filtering and loading logic

## Version 0.2.6 Updates

- Added portfolio information application module for equity analysis
- Implemented functions to fetch listed equity portfolios
- Added division-specific portfolio aggregation functionality
- Implemented keyword search for equity information

## Version 0.2.5 Updates

- Further improved inner product calculation reliability
- Added raw comparison data preservation before NA handling
- Simplified vector extraction process with direct access to raw data
- Enhanced data flow in vector pair comparison pipeline

## Version 0.2.4 Updates

- Fixed inner product calculation bug in vector extraction process
- Improved vector conversion from string to numeric values
- Enhanced column selection logic for comparison dataframes
- Added explicit type casting to ensure numeric calculations

## Version 0.2.3 Updates

- Enhanced vector pair comparison functionality
- Improved delta calculation for same fund code comparison
- Added date reference display for same fund comparisons
- Moved delta calculation to vector_pair module for better code organization

## Version 0.2.2 Updates

- Added threshold option to result loading function for better filtering
- Improved data analysis capabilities with similarity threshold filtering

## Version 0.2.1 Updates

- Updated documentation with English-only content for better international accessibility
- Fixed minor bugs and improved code stability

## Version 0.2.0 Updates

- Major restructuring of modules into specialized subpackages:
  - `audit_asset`: Asset vector analysis and validation
  - `audit_date`: Date condition utilities and validation
  - `audit_investor`: Investor data loading and analysis
  - `audit_portfolio`: Portfolio vector comparison tools
  - `audit_result`: Automated audit result generation and storage
- Added new result_application module for complete automated audits
- Added dependency on fund_insight_engine for enhanced analysis
- Improved code organization and maintainability

## Version 0.1.4 Updates

- Fixed result output formatting for better data handling
- Added automatic index reset for consistent data structure

## Version 0.1.3 Updates

- Enhanced automated filtering system for more accurate results
- Improved final judgment output functionality
- Optimized performance for large dataset processing

## Key Features

- Portfolio Vector Analysis
  - Fund portfolio similarity calculation
  - Inner product-based portfolio comparison
  - Asset composition validation
- Investor Data Analysis
  - Investor count and total investment amount analysis
  - Cross-fund investor overlap analysis
- Automated Audit Reports
  - Automatic series issue audit result generation
  - CSV format result storage
  - Korean language support for data output

## Installation

You can install the package using pip:

```bash
pip install fund-series-issue-audit
```

Or directly from GitHub:

```bash
pip install git+https://github.com/nailen1/fund_series_issue_audit.git
```

## Requirements

- Python >= 3.11
- Dependencies:
  - openpyxl >= 3.1.5
  - scipy >= 1.11.0
  - requests >= 2.31.0
  - tqdm
  - shining_pebbles >= 0.5.3
  - canonical_transformer >= 0.2.4
  - financial_dataset_preprocessor >= 0.3.3
  - fund_insight_engine >= 0.1.3

## Usage Examples

### 1. Run Automated Series Issue Audit

```python
from fund_series_issue_audit.audit_result import save_automated_series_issue_audit

# Run and save automated series issue audit
result = save_automated_series_issue_audit(date_ref='2025-04-14')

# Check results
print(result.head())
```

### 2. Load Saved Audit Results

```python
from fund_series_issue_audit.audit_result import load_automated_series_issue_audit_result

# Load audit results for a specific date
audit_result = load_automated_series_issue_audit_result(date_ref='2025-04-14')

# Check results
print(audit_result.head())
```

### 3. Portfolio Vector Comparison Analysis

```python
from fund_series_issue_audit.audit_portfolio import PortfolioVector, VectorPair

# Create portfolio vectors for two funds
pv_i = PortfolioVector(fund_code='100142')
pv_j = PortfolioVector(fund_code='100015')

# Create and compare vector pair
vp = VectorPair(pv_i, pv_j)

# Calculate inner product (similarity)
print(f'Inner product: {vp.inner_product}')

# Detailed comparison results
comparison = vp.comparison
print(comparison)
```

## Development Setup

To set up the development environment:

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under a proprietary license. All rights reserved.

### Terms of Use

- Source code viewing and forking is allowed
- Commercial use is prohibited without explicit permission
- Redistribution or modification of the code is prohibited
- Academic and research use is allowed with proper attribution

## Author

**June Young Park**  
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

### Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
