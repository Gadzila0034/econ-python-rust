# ?? Statistical Analyzer with Rust Backend 
 
Project for statistical data analysis with high-performance Rust backend and Python GUI interface. 
 
## ?? Quick Start 
 
### Installation: 
\`\`\`bash 
# 1. Install Rust module 
cd rust-core 
pip install maturin 
maturin develop 
cd .. 
 
# 2. Install Python dependencies 
cd statistics_app 
pip install -r requirements.txt 
cd .. 
\`\`\` 
 
### Run: 
\`\`\`bash 
python statistics_app/main.py 
\`\`\` 
 
## ?? Features 
 
? **Rust backend** - high-performance statistical calculations 
? **Python GUI** - intuitive Tkinter interface 
? **Complete statistics** - mean, variance, skewness, kurtosis 
? **Medians and modes** - calculation by intervals 
? **Histograms** - distribution visualization 
? **Large datasets** - supports 100,000+ data points 
 
## ?? Requirements 
 
- Python 3.8+ 
- Rust (installed automatically via maturin) 
- Tkinter (usually included with Python) 
 
## ?? Usage 
 
1. Run the application: \`python statistics_app/main.py\` 
2. Input data through the interface 
3. Click "Calculate" button 
4. View results in the table 
5. Click "Medians and Modes" for detailed information 
