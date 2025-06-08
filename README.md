# 📊 Excelbot

A powerful AI-driven conversational assistant that transforms Excel data analysis through natural language queries. Upload your Excel files and get instant insights, comprehensive dashboards, and interactive visualizations just by asking questions in plain English.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)
![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

## 🌟 Key Features

### 🤖 **AI-Powered Analysis**
- **Google Gemini Integration**: Advanced natural language understanding
- **Dynamic Code Generation**: AI writes custom Python/Plotly code for each query
- **Smart Fallback System**: Works even without API access
- **Context-Aware Responses**: Understands your specific data structure

### 📈 **Advanced Visualization**
- **Single Charts**: Bar, line, scatter, histogram, pie, box plots, heatmaps
- **Multiple Plot Analysis**: Generate several charts simultaneously
- **Comprehensive Dashboards**: 4-6 visualizations with automatic insights
- **Interactive Plots**: All charts are interactive with hover details

### 🔧 **Robust Data Handling**
- **Auto-Column Naming**: Handles Excel files without headers
- **Smart Column Mapping**: Automatically fixes case sensitivity issues
- **Data Type Detection**: Automatic numeric, categorical, date recognition
- **Missing Value Handling**: Graceful handling of incomplete data

### 💬 **Intuitive Interface**
- **Natural Language Queries**: Ask questions like "Show me sales by region"
- **Quick Action Buttons**: Instant dashboard, charts, and summaries
- **Chat History**: Track your analysis conversation
- **Real-time Processing**: Immediate responses and visualizations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (free tier available)
- Modern web browser

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/excel-insights-chatbot.git
cd excel-insights-chatbot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Set Up API Key**

Choose one method:

**Option A: Environment Variable**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Option B: Streamlit Secrets (Recommended)**
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

4. **Run the Application**
```bash
streamlit run app.py
```

5. **Open in Browser**
Navigate to `http://localhost:8501`

### Get Your Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key (free tier available)
4. Copy and use in your configuration

## 🎯 Usage Guide

### Step 1: Upload Your Excel File
- Click "Choose an Excel file" in the sidebar
- Upload any `.xlsx` file (up to 500 rows recommended)
- System automatically handles missing column names
- View data overview and column information

### Step 2: Quick Actions
Use the instant action buttons for common tasks:

- **📊 Create Dashboard**: Comprehensive analysis with multiple charts
- **📈 Multiple Charts**: Generate various visualizations
- **🔢 Data Summary**: Statistical overview
- **📋 Simple Overview**: Guaranteed working basic plots

### Step 3: Natural Language Queries

Ask questions in plain English:

#### Statistical Analysis
```
"What is the average sales amount?"
"Show me summary statistics for all numeric columns"
"Calculate correlations between variables"
```

#### Data Exploration
```
"How many unique customers do we have?"
"Show me records where revenue > 10000"
"What are the most common product categories?"
```

#### Single Visualizations
```
"Create a bar chart of sales by region"
"Make a histogram of customer ages"
"Show a scatter plot of price vs quantity"
```

#### Multiple Visualizations
```
"Show me multiple charts to analyze this data"
"Create several different plots for comparison"
"Generate various visualizations"
```

#### Dashboard Creation
```
"Create a comprehensive dashboard"
"Give me a complete analysis overview"
"Generate a summary dashboard with key insights"
```

## 📁 Project Structure

```
excel-insights-chatbot/
├── app.py                 # Main Streamlit application
├── data_processor.py      # Excel file handling and data operations
├── llm_handler.py         # Google Gemini API integration
├── requirements.txt       # Python dependencies
├── .streamlit/
│   ├── config.toml        # Streamlit configuration
│   └── secrets.toml       # API keys (create this)
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## 🏗️ Architecture Overview

### Core Components

#### 1. **DataProcessor** (`data_processor.py`)
- **Excel File Loading**: Handles `.xlsx` files with automatic preprocessing
- **Column Normalization**: Converts column names to consistent format
- **Auto-Naming**: Creates "Column 1", "Column 2" for unnamed columns
- **Data Operations**: Filtering, grouping, statistical analysis
- **Type Detection**: Automatic numeric, categorical, datetime recognition

#### 2. **LLMHandler** (`llm_handler.py`)
- **Gemini Integration**: Google Gemini API for natural language processing
- **Dynamic Prompting**: Context-aware prompt generation
- **Code Generation**: AI writes custom Plotly visualization code
- **Fallback System**: Rule-based responses when AI unavailable
- **Column Mapping**: Ensures correct column name usage

#### 3. **Main Application** (`app.py`)
- **Streamlit Interface**: User-friendly web application
- **Code Execution**: Safe execution of AI-generated plotting code
- **Chat System**: Interactive conversation with chat history
- **Dashboard Layout**: Multi-plot displays with organized sections
- **Error Handling**: Comprehensive error recovery and user feedback

### Data Flow

1. **File Upload** → Excel processing → Column normalization
2. **User Query** → LLM analysis → Code generation
3. **Code Execution** → Plot creation → Display results
4. **Error Recovery** → Fallback plots → User feedback

## 📊 Supported Analysis Types

### Statistical Operations
- Descriptive statistics (mean, median, mode, std)
- Correlation analysis
- Value counts and frequencies
- Data filtering and grouping
- Missing value analysis

### Visualization Types
- **Bar Charts**: Categorical comparisons
- **Line Charts**: Trends over time
- **Histograms**: Data distributions
- **Scatter Plots**: Variable relationships
- **Pie Charts**: Proportional data
- **Box Plots**: Outlier detection
- **Heatmaps**: Correlation matrices

### Dashboard Components
- Data overview with key metrics
- Distribution analysis for numeric columns
- Categorical analysis with top values
- Correlation heatmaps
- Outlier detection plots
- Relationship analysis

## 🛠️ Troubleshooting

### Common Issues

**File Upload Problems**
```
Issue: "Error loading Excel file"
Solution: Ensure file is .xlsx format and has proper structure
```

**API Connection Issues**
```
Issue: "Gemini API key not found"
Solution: Set GEMINI_API_KEY in environment or Streamlit secrets
```

**Plot Generation Errors**
```
Issue: "Plot Generation Error: Column not found"
Solution: System automatically fixes column names, but check data structure
```

**Dashboard Failures**
```
Issue: Some dashboard plots fail
Solution: Use "Simple Overview" button for guaranteed working visualizations
```

### Performance Tips
- Keep Excel files under 500 rows for optimal performance
- Use "Simple Overview" for large datasets
- Clear chat history periodically to free memory

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Follow coding standards and add tests
4. **Commit Changes**: `git commit -m 'Add amazing feature'`
5. **Push Branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**: Describe your changes clearly

### Development Setup
```bash
# Clone your fork
git clone https://github.com/your-username/excel-insights-chatbot.git

# Install development dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run app.py --server.runOnSave true
```

## 📝 Requirements

### Core Dependencies
```
streamlit>=1.28.0          # Web application framework
pandas>=2.0.0              # Data manipulation and analysis
plotly>=5.15.0             # Interactive visualization library
openpyxl>=3.1.0            # Excel file reading
google-generativeai>=0.3.0 # Google Gemini API client
numpy>=1.24.0              # Numerical computing
```

### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.9 or higher

## 🔒 Security & Privacy

### Data Handling
- **Local Processing**: Files processed in memory only
- **No Persistent Storage**: Data not saved after session
- **API Privacy**: Only data structure sent to AI, not actual values
- **Secure Execution**: Safe code execution environment

### API Security
- **Environment Variables**: Store API keys securely
- **Rate Limiting**: Respects Google API limits
- **Error Handling**: No sensitive data in error messages

## 📈 Performance Specifications

### Recommended Limits
- **File Size**: Up to 10MB Excel files
- **Data Dimensions**: 500 rows × 20 columns optimal
- **Concurrent Users**: Depends on deployment platform
- **Response Time**: 2-5 seconds for most queries

### Scalability
- **Horizontal Scaling**: Deploy multiple instances
- **Caching**: Built-in Streamlit caching
- **Memory Management**: Automatic cleanup after sessions

## 🆘 Support

### Getting Help
1. **Check Documentation**: Review this README thoroughly
2. **Search Issues**: Look for similar problems in GitHub issues
3. **Create Issue**: Provide detailed description and error logs
4. **Community**: Join discussions and share feedback

### Bug Reports
Include the following information:
- Python version and operating system
- Streamlit version
- Error messages and stack traces
- Steps to reproduce the issue
- Sample data (if possible)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Excel Insights Chatbot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

### Technologies Used
- **[Streamlit](https://streamlit.io/)** - For the intuitive web interface
- **[Google Gemini](https://ai.google/)** - For advanced AI capabilities
- **[Plotly](https://plotly.com/)** - For interactive visualizations
- **[Pandas](https://pandas.pydata.org/)** - For data manipulation
- **[OpenPyXL](https://openpyxl.readthedocs.io/)** - For Excel file processing

### Inspiration
Built to democratize data analysis and make Excel insights accessible to everyone through natural language interaction.

---

**Ready to transform your Excel analysis experience? 🚀**

Upload your data, ask questions in plain English, and discover insights you never knew existed!

For questions or support, please open an issue or reach out to our community.
