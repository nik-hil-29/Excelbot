import os
import re
import json
from typing import Dict, Any, Optional

import streamlit as st
import google.generativeai as genai

class LLMHandler:
    """Handles integration with Google Gemini for query processing and dynamic plot generation"""
    
    def __init__(self):
        """Initialize Gemini API client"""
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API with proper error handling"""
        try:
            # Get API key from Streamlit secrets or environment
            api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                st.error("⚠️ Gemini API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
        except Exception as e:
            st.error("Error initializing Gemini: " + str(e))
            self.model = None
    
    def process_query(self, user_query: str, data_context: str) -> Dict[str, Any]:
        """Process user query and return structured response with dynamic plotting"""
        if not self.model:
            return self._fallback_response(user_query, data_context)
        
        try:
            # Create comprehensive prompt for Gemini
            prompt = self._create_analysis_prompt(user_query, data_context)
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            return self._parse_gemini_response(response.text, user_query)
            
        except Exception as e:
            print("Gemini API error: " + str(e))
            return self._fallback_response(user_query, data_context)
    
    def _create_analysis_prompt(self, user_query: str, data_context: str) -> str:
        """Create comprehensive prompt for data analysis and dynamic plotting"""
        
        # Check if this is a dashboard request
        query_lower = user_query.lower()
        is_dashboard = any(word in query_lower for word in ['dashboard', 'overview', 'summary', 'comprehensive', 'all analysis', 'complete analysis'])
        
        if is_dashboard:
            return self._create_dashboard_prompt(user_query, data_context)
        
        # Build the regular prompt using string concatenation to avoid f-string issues
        prompt_start = """You are an expert data analyst and Python programmer helping users understand their Excel data through natural language queries.

DATASET CONTEXT:
"""
        
        prompt_middle = """

USER QUERY: \""""
        
        prompt_end = '''\"

Your task is to analyze the user's query and provide a structured response in JSON format with the following structure:

{
    "answer": "Human-readable answer to the query",
    "requires_data": true/false,
    "requires_plot": true/false,
    "requires_multiple_plots": false,
    "data_operation": {
        "type": "statistical_summary|filter|group_by|correlation|value_counts|custom_query",
        "columns": ["column_names"],
        "conditions": {"column": {"operator": "==|!=|>|<|>=|<=|contains", "value": "value"}},
        "group_column": "column_name",
        "agg_column": "column_name", 
        "agg_function": "count|sum|mean|median"
    },
    "plot_code": "Complete Python code using plotly to create the visualization",
    "plot_codes": ["array of plot codes if multiple plots requested"]
}

CRITICAL PLOT CODE REQUIREMENTS:

1. NEVER include import statements - all libraries are pre-imported
2. Available variables: df (DataFrame), px (plotly.express), go (plotly.graph_objects), pd (pandas), np (numpy)
3. Always assign the final plot to variable named 'fig'
4. **VERY IMPORTANT**: Use ONLY the NORMALIZED column names shown in parentheses in the dataset context
5. Write single-line or semicolon-separated code to avoid formatting issues

COLUMN NAME RULE:
In the dataset context, you will see:
- Original Name (normalized_name): description
ALWAYS use the normalized_name (in parentheses), NEVER the original name.

Example: If you see "Country (country): object", use 'country' NOT 'Country'

MULTIPLE PLOTS:
- If user asks for "multiple charts", "several plots", "compare different views", set requires_multiple_plots=true
- Provide array of plot codes in "plot_codes" field
- Each plot code should be complete and independent

EXAMPLE PLOT CODES:

For bar chart: fig = px.bar(df, x='normalized_column_name', y='value_column', title='Chart Title')

For histogram: fig = px.histogram(df, x='numeric_column', title='Distribution')

For scatter plot: fig = px.scatter(df, x='col1', y='col2', title='Relationship')

For value counts bar chart: 
counts = df['column'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Top Values')

ANALYSIS RULES:
- For statistical questions: set requires_data=true, requires_plot=false
- For single visualization: set requires_plot=true, generate plot_code
- For multiple visualizations: set requires_multiple_plots=true, generate plot_codes array
- Use only NORMALIZED column names that exist in the dataset (in parentheses)
- Keep responses concise and helpful

EXAMPLE RESPONSES:

Single Plot Example:
{
    "answer": "I will create a bar chart showing the distribution of your categorical data.",
    "requires_data": false,
    "requires_plot": true,
    "requires_multiple_plots": false,
    "data_operation": {},
    "plot_code": "counts = df['category_column'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Distribution of Categories')",
    "plot_codes": []
}

Multiple Plots Example:
{
    "answer": "I will create multiple visualizations to show different aspects of your data.",
    "requires_data": false,
    "requires_plot": false,
    "requires_multiple_plots": true,
    "data_operation": {},
    "plot_code": "",
    "plot_codes": [
        "fig = px.histogram(df, x='numeric_col', title='Distribution')",
        "counts = df['category_col'].value_counts(); fig = px.bar(x=counts.index, y=counts.values, title='Categories')"
    ]
}

Respond with ONLY the JSON structure, no additional text.'''
        
        # Safely concatenate without f-strings
        full_prompt = prompt_start + data_context + prompt_middle + user_query + prompt_end
        
        return full_prompt
    
    def _create_dashboard_prompt(self, user_query: str, data_context: str) -> str:
        """Create specialized prompt for dashboard/comprehensive analysis requests"""
        
        prompt_start = """You are an expert data analyst creating a comprehensive dashboard for Excel data analysis.

DATASET CONTEXT:
"""
        
        prompt_middle = """

USER REQUEST: \""""
        
        prompt_end = '''\"

Create a comprehensive dashboard with multiple visualizations and analysis. Return JSON with this structure:

{
    "answer": "I will create a comprehensive dashboard with multiple insights about your data.",
    "requires_data": true,
    "requires_plot": false,
    "requires_multiple_plots": true,
    "requires_dashboard": true,
    "data_operation": {
        "type": "statistical_summary",
        "columns": []
    },
    "plot_code": "",
    "plot_codes": [
        "array of 4-6 different plot codes for comprehensive analysis"
    ],
    "dashboard_sections": [
        {
            "title": "Data Overview",
            "description": "Basic statistics and data shape information"
        },
        {
            "title": "Distribution Analysis", 
            "description": "Histograms for numeric columns"
        },
        {
            "title": "Categorical Analysis",
            "description": "Bar charts for categorical columns"
        },
        {
            "title": "Correlation Analysis",
            "description": "Heatmap showing relationships between numeric variables"
        }
    ]
}

CRITICAL COLUMN NAME RULE:
In the dataset context, you will see:
- Original Name (normalized_name): description
ALWAYS use the normalized_name (in parentheses), NEVER the original name.

Example: If you see "Country (country): object", use 'country' NOT 'Country'
Example: If you see "Total Score (total_score): int64", use 'total_score' NOT 'Total Score'

DASHBOARD REQUIREMENTS:
1. Create 4-6 different visualizations covering:
   - Distributions of numeric columns (histograms)
   - Counts of categorical columns (bar charts)  
   - Correlations between numeric columns (heatmap)
   - Box plots for outlier detection
   - Scatter plots for relationships

2. Use ONLY NORMALIZED column names from the dataset context (in parentheses)
3. Each plot should be independent and complete
4. Focus on the most important insights

EXAMPLE DASHBOARD RESPONSE:
{
    "answer": "I will create a comprehensive dashboard with 5 key visualizations analyzing your data from multiple angles including distributions, categories, correlations, and outliers.",
    "requires_data": true,
    "requires_plot": false,
    "requires_multiple_plots": true,
    "requires_dashboard": true,
    "data_operation": {
        "type": "statistical_summary",
        "columns": []
    },
    "plot_code": "",
    "plot_codes": [
        "fig = px.histogram(df, x='numeric_col1', title='Distribution of Numeric Column 1')",
        "counts = df['categorical_col1'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Top Categories')",
        "numeric_df = df.select_dtypes(include=['number']); corr_matrix = numeric_df.corr(); fig = px.imshow(corr_matrix, title='Correlation Heatmap', color_continuous_scale='RdBu')",
        "fig = px.box(df, y='numeric_col1', title='Box Plot - Outlier Detection')",
        "fig = px.scatter(df, x='numeric_col1', y='numeric_col2', title='Relationship Analysis')"
    ],
    "dashboard_sections": [
        {"title": "Data Overview", "description": "Statistical summaries and data quality"},
        {"title": "Numeric Distributions", "description": "Histograms showing data distributions"},
        {"title": "Categorical Analysis", "description": "Most frequent categories and their counts"},
        {"title": "Correlation Analysis", "description": "Relationships between numeric variables"},
        {"title": "Outlier Detection", "description": "Box plots identifying potential outliers"}
    ]
}

Respond with ONLY the JSON structure, no additional text.'''
        
        # Safely concatenate without f-strings
        full_prompt = prompt_start + data_context + prompt_middle + user_query + prompt_end
        
        return full_prompt
    
    def _parse_gemini_response(self, response_text: str, original_query: str) -> Dict[str, Any]:
        """Parse and validate Gemini's JSON response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_response = json.loads(json_str)
                
                # Validate required fields
                if 'answer' not in parsed_response:
                    parsed_response['answer'] = "I analyzed your query but couldn't generate a proper response."
                
                # Set default values for missing fields
                parsed_response.setdefault('requires_plot', False)
                parsed_response.setdefault('requires_data', False)
                parsed_response.setdefault('requires_multiple_plots', False)
                parsed_response.setdefault('requires_dashboard', False)
                parsed_response.setdefault('data_operation', {})
                parsed_response.setdefault('plot_code', '')
                parsed_response.setdefault('plot_codes', [])
                parsed_response.setdefault('dashboard_sections', [])
                
                return parsed_response
            else:
                # No JSON found, treat as plain text response
                return {
                    'answer': response_text,
                    'requires_plot': False,
                    'requires_data': False,
                    'requires_multiple_plots': False,
                    'requires_dashboard': False,
                    'data_operation': {},
                    'plot_code': '',
                    'plot_codes': [],
                    'dashboard_sections': []
                }
                
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'answer': response_text if response_text else "I couldn't process your query properly.",
                'requires_plot': False,
                'requires_data': False,
                'requires_multiple_plots': False,
                'requires_dashboard': False,
                'data_operation': {},
                'plot_code': '',
                'plot_codes': [],
                'dashboard_sections': []
            }
    
    def _fallback_response(self, user_query: str, data_context: str) -> Dict[str, Any]:
        """Provide rule-based fallback when Gemini is unavailable"""
        query_lower = user_query.lower()
        
        # Extract potential column names from context
        columns = self._extract_columns_from_context(data_context)
        numeric_columns = self._extract_numeric_columns_from_context(data_context)
        categorical_columns = [col for col in columns if col not in numeric_columns]
        
        # Check for dashboard request
        if any(word in query_lower for word in ['dashboard', 'overview', 'summary', 'comprehensive', 'all analysis', 'complete analysis']):
            return self._create_fallback_dashboard(columns, numeric_columns, categorical_columns)
        
        # Check for multiple plots request
        elif any(word in query_lower for word in ['multiple', 'several', 'various', 'different charts', 'compare']):
            return self._create_fallback_multiple_plots(query_lower, columns, numeric_columns, categorical_columns)
        
        # Rule-based query classification for single responses
        elif any(word in query_lower for word in ['average', 'mean', 'median', 'sum', 'total', 'statistics', 'summary']):
            return {
                'answer': "I'll calculate statistical summaries for the numeric columns in your dataset.",
                'requires_plot': False,
                'requires_data': True,
                'requires_multiple_plots': False,
                'requires_dashboard': False,
                'data_operation': {
                    'type': 'statistical_summary',
                    'columns': numeric_columns
                },
                'plot_code': '',
                'plot_codes': [],
                'dashboard_sections': []
            }
        
        elif any(word in query_lower for word in ['chart', 'plot', 'graph', 'visualization', 'show']):
            # Generate simple plot code based on query type
            plot_code = self._generate_fallback_plot_code(query_lower, columns, numeric_columns)
            
            return {
                'answer': "I'll create a visualization for your data using the available columns.",
                'requires_plot': True,
                'requires_data': False,
                'requires_multiple_plots': False,
                'requires_dashboard': False,
                'data_operation': {},
                'plot_code': plot_code,
                'plot_codes': [],
                'dashboard_sections': []
            }
        
        elif any(word in query_lower for word in ['filter', 'where', 'under', 'over', 'above', 'below']):
            return {
                'answer': "I'll filter the data based on your criteria. However, I need more specific conditions to apply the filter properly.",
                'requires_plot': False,
                'requires_data': True,
                'requires_multiple_plots': False,
                'requires_dashboard': False,
                'data_operation': {
                    'type': 'filter',
                    'conditions': {}
                },
                'plot_code': '',
                'plot_codes': [],
                'dashboard_sections': []
            }
        
        else:
            return {
                'answer': "I understand you want to analyze your data, but I'm currently running in fallback mode. Please ensure the Gemini API is properly configured for more advanced query processing.",
                'requires_plot': False,
                'requires_data': False,
                'requires_multiple_plots': False,
                'requires_dashboard': False,
                'data_operation': {},
                'plot_code': '',
                'plot_codes': [],
                'dashboard_sections': []
            }
    
    def _create_fallback_dashboard(self, columns: list, numeric_columns: list, categorical_columns: list) -> Dict[str, Any]:
        """Create fallback dashboard with multiple visualizations"""
        plot_codes = []
        dashboard_sections = []
        
        # Add histogram for first numeric column
        if numeric_columns:
            col = numeric_columns[0]
            plot_codes.append("fig = px.histogram(df, x='" + col + "', title='Distribution of " + col.replace('_', ' ').title() + "')")
            dashboard_sections.append({
                "title": "Numeric Distribution",
                "description": "Distribution analysis of " + col.replace('_', ' ').title()
            })
        
        # Add bar chart for first categorical column
        if categorical_columns:
            col = categorical_columns[0]
            plot_codes.append("counts = df['" + col + "'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Top Categories in " + col.replace('_', ' ').title() + "')")
            dashboard_sections.append({
                "title": "Categorical Analysis",
                "description": "Most frequent values in " + col.replace('_', ' ').title()
            })
        
        # Add correlation heatmap if multiple numeric columns
        if len(numeric_columns) > 1:
            # Build column list string for the correlation plot
            numeric_cols_str = "['" + "', '".join(numeric_columns) + "']"
            plot_codes.append("numeric_df = df[" + numeric_cols_str + "]; corr_matrix = numeric_df.corr(); fig = px.imshow(corr_matrix, title='Correlation Heatmap', text_auto=True, color_continuous_scale='RdBu')")
            dashboard_sections.append({
                "title": "Correlation Analysis",
                "description": "Relationships between numeric variables"
            })
        
        # Add box plot for outlier detection
        if numeric_columns:
            col = numeric_columns[0]
            plot_codes.append("fig = px.box(df, y='" + col + "', title='Outlier Detection - " + col.replace('_', ' ').title() + "')")
            dashboard_sections.append({
                "title": "Outlier Detection",
                "description": "Box plot analysis for " + col.replace('_', ' ').title()
            })
        
        # Add scatter plot if we have at least 2 numeric columns
        if len(numeric_columns) >= 2:
            col1, col2 = numeric_columns[0], numeric_columns[1]
            plot_codes.append("fig = px.scatter(df, x='" + col1 + "', y='" + col2 + "', title='Relationship: " + col2.replace('_', ' ').title() + " vs " + col1.replace('_', ' ').title() + "')")
            dashboard_sections.append({
                "title": "Relationship Analysis",
                "description": "Scatter plot showing relationship between key variables"
            })
        
        return {
            'answer': "I'll create a comprehensive dashboard with " + str(len(plot_codes)) + " key visualizations analyzing your data from multiple perspectives.",
            'requires_plot': False,
            'requires_data': True,
            'requires_multiple_plots': True,
            'requires_dashboard': True,
            'data_operation': {
                'type': 'statistical_summary',
                'columns': numeric_columns
            },
            'plot_code': '',
            'plot_codes': plot_codes,
            'dashboard_sections': dashboard_sections
        }
    
    def _create_fallback_multiple_plots(self, query_lower: str, columns: list, numeric_columns: list, categorical_columns: list) -> Dict[str, Any]:
        """Create multiple plots based on available data"""
        plot_codes = []
        
        # Add relevant plots based on available columns
        if 'histogram' in query_lower and numeric_columns:
            for col in numeric_columns[:2]:  # Limit to 2 histograms
                plot_codes.append("fig = px.histogram(df, x='" + col + "', title='Distribution of " + col.replace('_', ' ').title() + "')")
        
        if 'bar' in query_lower and categorical_columns:
            for col in categorical_columns[:2]:  # Limit to 2 bar charts
                plot_codes.append("counts = df['" + col + "'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Top Values in " + col.replace('_', ' ').title() + "')")
        
        # Default: create a mix of plots
        if not plot_codes:
            if numeric_columns:
                col = numeric_columns[0]
                plot_codes.append("fig = px.histogram(df, x='" + col + "', title='Distribution of " + col.replace('_', ' ').title() + "')")
            if categorical_columns:
                col = categorical_columns[0]
                plot_codes.append("counts = df['" + col + "'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Categories in " + col.replace('_', ' ').title() + "')")
            if len(numeric_columns) >= 2:
                col1, col2 = numeric_columns[0], numeric_columns[1]
                plot_codes.append("fig = px.scatter(df, x='" + col1 + "', y='" + col2 + "', title='Relationship Analysis')")
        
        return {
            'answer': "I'll create " + str(len(plot_codes)) + " different visualizations to show various aspects of your data.",
            'requires_plot': False,
            'requires_data': False,
            'requires_multiple_plots': True,
            'requires_dashboard': False,
            'data_operation': {},
            'plot_code': '',
            'plot_codes': plot_codes,
            'dashboard_sections': []
        }
    
    def _generate_fallback_plot_code(self, query_lower: str, columns: list, numeric_columns: list) -> str:
        """Generate simple plot code for fallback mode"""
        if not columns:
            return "fig = px.bar(x=['No Data'], y=[0], title='No data available for plotting')"
        
        # Determine chart type based on keywords
        if 'bar' in query_lower and len(columns) >= 1:
            col = columns[0]
            return "counts = df['" + col + "'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Distribution of " + col.replace('_', ' ').title() + "')"
        
        elif 'histogram' in query_lower and numeric_columns:
            col = numeric_columns[0]
            return "fig = px.histogram(df, x='" + col + "', title='Distribution of " + col.replace('_', ' ').title() + "')"
        
        elif 'scatter' in query_lower and len(numeric_columns) >= 2:
            col1, col2 = numeric_columns[0], numeric_columns[1]
            return "fig = px.scatter(df, x='" + col1 + "', y='" + col2 + "', title='" + col2.replace('_', ' ').title() + " vs " + col1.replace('_', ' ').title() + "')"
        
        else:
            # Default bar chart of first column
            col = columns[0]
            return "counts = df['" + col + "'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Top 10 values in " + col.replace('_', ' ').title() + "')"
    
    def _extract_columns_from_context(self, data_context: str) -> list:
        """Extract column names from data context string"""
        columns = []
        lines = data_context.split('\n')
        for line in lines:
            if ' - ' in line and '(' in line and ')' in line:
                # Extract normalized column name from parentheses
                match = re.search(r'\(([^)]+)\)', line)
                if match:
                    columns.append(match.group(1))
        return columns
    
    def _extract_numeric_columns_from_context(self, data_context: str) -> list:
        """Extract numeric column names from data context"""
        numeric_columns = []
        lines = data_context.split('\n')
        for line in lines:
            if 'int64' in line or 'float64' in line:
                match = re.search(r'\(([^)]+)\)', line)
                if match:
                    numeric_columns.append(match.group(1))
        return numeric_columns