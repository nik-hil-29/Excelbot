import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_processor import DataProcessor
from llm_handler import LLMHandler
import traceback
import sys
from io import StringIO

def initialize_session_state():
    """Initialize session state variables"""
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = None
    if 'llm_handler' not in st.session_state:
        st.session_state.llm_handler = LLMHandler()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False

def execute_plot_code(code: str, df: pd.DataFrame) -> tuple:
    """Execute the generated plot code safely with column name fixing"""
    try:
        # Clean the code - remove any import statements and markdown artifacts
        code_lines = code.strip().split('\n')
        clean_lines = []
        for line in code_lines:
            line = line.strip()
            # Skip import statements, markdown artifacts, and empty lines
            if (not line.startswith('import') and 
                not line.startswith('from') and 
                not line.startswith('```') and 
                line and 
                not line == 'python' and
                not line == 'json'):
                clean_lines.append(line)
        
        # Join lines with semicolons for single-line execution
        cleaned_code = '; '.join(clean_lines) if len(clean_lines) > 1 else ''.join(clean_lines)
        
        # Fix column name case issues by mapping to actual dataframe columns
        cleaned_code = fix_column_names_in_code(cleaned_code, df)
        
        # Create a comprehensive safe execution environment
        safe_globals = {
            'pd': pd,
            'px': px,
            'go': go,
            'df': df,
            'np': np,
            'plotly': px,
            # Add common functions that might be used
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'reversed': reversed,
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
            }
        }
        
        # Capture stdout for any print statements
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # Execute the cleaned code
        local_vars = {}
        exec(cleaned_code, safe_globals, local_vars)
        
        # Restore stdout
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        
        # Look for 'fig' variable in local_vars
        if 'fig' in local_vars:
            return local_vars['fig'], output, None
        else:
            return None, output, "No 'fig' variable found in the generated code. Code executed: " + cleaned_code
            
    except Exception as e:
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        error_msg = "Error executing plot code: " + str(e) + "\nCode attempted: " + str(code)
        return None, "", error_msg

def fix_column_names_in_code(code: str, df: pd.DataFrame) -> str:
    """Fix column name case issues in generated code"""
    try:
        # Get actual column names from dataframe
        actual_columns = list(df.columns)
        
        # Create mapping of potential column names to actual ones
        column_mapping = {}
        for actual_col in actual_columns:
            # Map variations of the column name
            variations = [
                actual_col,  # exact match
                actual_col.lower(),  # lowercase
                actual_col.upper(),  # uppercase  
                actual_col.title(),  # title case
                actual_col.replace('_', ' ').title(),  # with spaces and title case
                actual_col.replace('_', ' ').upper(),  # with spaces and uppercase
                actual_col.replace('_', ' ').lower(),  # with spaces and lowercase
            ]
            
            for variation in variations:
                column_mapping[variation] = actual_col
        
        # Replace column references in the code
        fixed_code = code
        for wrong_name, correct_name in column_mapping.items():
            if wrong_name != correct_name:  # Only replace if different
                # Replace in various contexts
                patterns = [
                    f"'{wrong_name}'",  # single quotes
                    f'"{wrong_name}"',  # double quotes
                    f"['{wrong_name}']",  # in brackets with single quotes
                    f'["{wrong_name}"]',  # in brackets with double quotes
                ]
                
                for pattern in patterns:
                    replacement = pattern.replace(wrong_name, correct_name)
                    fixed_code = fixed_code.replace(pattern, replacement)
        
        return fixed_code
        
    except Exception as e:
        # If fixing fails, return original code
        print(f"Warning: Could not fix column names in code: {str(e)}")
        return code

def display_data_overview():
    """Display overview of uploaded data"""
    if st.session_state.data_processor and st.session_state.data_uploaded:
        data_info = st.session_state.data_processor.get_data_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", data_info['rows'])
        with col2:
            st.metric("Total Columns", data_info['columns'])
        with col3:
            st.metric("Data Types", len(data_info['dtypes']))
        
        with st.expander("View Data Sample"):
            st.dataframe(st.session_state.data_processor.df.head())
        
        with st.expander("Column Information"):
            col_info_df = pd.DataFrame({
                'Column': data_info['dtypes'].keys(),
                'Data Type': data_info['dtypes'].values(),
                'Missing Values': [st.session_state.data_processor.df[col].isnull().sum() 
                                 for col in data_info['dtypes'].keys()]
            })
            st.dataframe(col_info_df)

def _create_simple_fallback_plot(plot_index: int, data_processor) -> str:
    """Create simple fallback plots for dashboard failures"""
    try:
        summary = data_processor.get_data_summary()
        numeric_columns = summary['numeric_columns']
        categorical_columns = summary['categorical_columns']
        
        # Create different fallback plots based on index
        if plot_index == 0 and numeric_columns:
            # Simple histogram
            return "fig = px.histogram(df, x='" + numeric_columns[0] + "', title='Data Distribution')"
        elif plot_index == 1 and categorical_columns:
            # Simple bar chart
            return "counts = df['" + categorical_columns[0] + "'].value_counts().head(5); fig = px.bar(x=counts.index, y=counts.values, title='Category Distribution')"
        elif plot_index == 2 and len(numeric_columns) >= 2:
            # Simple scatter plot
            return "fig = px.scatter(df, x='" + numeric_columns[0] + "', y='" + numeric_columns[1] + "', title='Data Relationship')"
        elif numeric_columns:
            # Default histogram
            return "fig = px.histogram(df, x='" + numeric_columns[0] + "', title='Data Analysis')"
        elif categorical_columns:
            # Default bar chart
            return "counts = df['" + categorical_columns[0] + "'].value_counts().head(5); fig = px.bar(x=counts.index, y=counts.values, title='Data Analysis')"
        else:
            return None
    except:
        return None

def process_user_query(query):
    """Process user query and generate response with dynamic plotting"""
    if not st.session_state.data_processor:
        return "Please upload an Excel file first."
    
    try:
        # Get data context for the LLM
        data_context = st.session_state.data_processor.get_data_context()
        
        # Process query with LLM
        response = st.session_state.llm_handler.process_query(query, data_context)
        
        result = {'text': response.get('answer', 'I could not process your query.')}
        
        # Handle data operations
        if response.get('requires_data'):
            data_result = st.session_state.data_processor.execute_data_query(response.get('data_operation', {}))
            if data_result is not None:
                result['data'] = data_result
        
        # Handle dashboard functionality
        if response.get('requires_dashboard'):
            result['is_dashboard'] = True
            result['dashboard_sections'] = response.get('dashboard_sections', [])
            
            # Process multiple plots for dashboard
            plot_codes = response.get('plot_codes', [])
            if plot_codes:
                result['multiple_plots'] = []
                df_for_plot = st.session_state.data_processor.df
                successful_plots = 0
                
                for i, plot_code in enumerate(plot_codes):
                    fig, output, error = execute_plot_code(plot_code, df_for_plot)
                    plot_result = {
                        'plot_code': plot_code,
                        'section_info': response.get('dashboard_sections', [])[i] if i < len(response.get('dashboard_sections', [])) else {'title': 'Analysis ' + str(i+1), 'description': 'Data visualization'}
                    }
                    
                    if fig:
                        plot_result['plot'] = fig
                        if output:
                            plot_result['plot_info'] = output
                        successful_plots += 1
                    elif error:
                        plot_result['plot_error'] = error
                        # Try a simpler fallback plot for failed dashboard items
                        fallback_code = _create_simple_fallback_plot(i, st.session_state.data_processor)
                        if fallback_code:
                            fallback_fig, _, fallback_error = execute_plot_code(fallback_code, df_for_plot)
                            if fallback_fig:
                                plot_result['plot'] = fallback_fig
                                plot_result['plot_code'] = fallback_code
                                plot_result['plot_info'] = "Fallback visualization"
                                successful_plots += 1
                    
                    result['multiple_plots'].append(plot_result)
                
                # Update answer to reflect successful plots
                if successful_plots > 0:
                    result['text'] = result['text'] + " Successfully generated " + str(successful_plots) + " out of " + str(len(plot_codes)) + " visualizations."
        
        # Handle multiple plots (non-dashboard)
        elif response.get('requires_multiple_plots'):
            plot_codes = response.get('plot_codes', [])
            if plot_codes:
                result['multiple_plots'] = []
                df_for_plot = st.session_state.data_processor.df
                
                for i, plot_code in enumerate(plot_codes):
                    fig, output, error = execute_plot_code(plot_code, df_for_plot)
                    plot_result = {
                        'plot_code': plot_code,
                        'title': 'Chart ' + str(i+1)
                    }
                    
                    if fig:
                        plot_result['plot'] = fig
                        if output:
                            plot_result['plot_info'] = output
                    elif error:
                        plot_result['plot_error'] = error
                    
                    result['multiple_plots'].append(plot_result)
        
        # Handle single plot generation
        elif response.get('requires_plot'):
            plot_code = response.get('plot_code', '')
            if plot_code:
                # Store the plot code for debugging
                result['plot_code'] = plot_code
                
                # Use the original dataframe for plotting
                df_for_plot = st.session_state.data_processor.df
                fig, output, error = execute_plot_code(plot_code, df_for_plot)
                
                if fig:
                    result['plot'] = fig
                    if output:
                        result['plot_info'] = output
                elif error:
                    result['plot_error'] = error
        
        return result
        
    except Exception as e:
        return {'text': "Error processing query: " + str(e)}

def display_chat_message(message, is_user=True):
    """Display chat message with appropriate styling"""
    if is_user:
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            if isinstance(message, dict):
                # Display text response
                if 'text' in message:
                    st.write(message['text'])
                
                # Display dashboard
                if message.get('is_dashboard'):
                    st.subheader("📊 Comprehensive Dashboard")
                    
                    # Display data summary first
                    if 'data' in message and message['data'] is not None:
                        with st.expander("📋 Statistical Summary", expanded=True):
                            if isinstance(message['data'], pd.DataFrame):
                                st.dataframe(message['data'])
                    
                    # Display multiple plots in dashboard format
                    if 'multiple_plots' in message:
                        dashboard_sections = message.get('dashboard_sections', [])
                        
                        # Create columns for dashboard layout
                        if len(message['multiple_plots']) >= 2:
                            cols = st.columns(2)
                        else:
                            cols = [st.container()]
                        
                        for i, plot_result in enumerate(message['multiple_plots']):
                            col_index = i % len(cols)
                            with cols[col_index]:
                                # Display section info
                                section_info = plot_result.get('section_info', {})
                                section_title = section_info.get('title', 'Analysis ' + str(i+1))
                                section_desc = section_info.get('description', 'Data visualization')
                                
                                st.subheader(section_title)
                                st.caption(section_desc)
                                
                                # Display plot
                                if 'plot' in plot_result:
                                    st.plotly_chart(plot_result['plot'], use_container_width=True)
                                elif 'plot_error' in plot_result:
                                    st.error("Plot error: " + plot_result['plot_error'])
                                    with st.expander("🔧 Generated Code"):
                                        st.code(plot_result['plot_code'], language='python')
                
                # Display multiple plots (non-dashboard)
                elif 'multiple_plots' in message:
                    st.subheader("📈 Multiple Visualizations")
                    
                    # Create tabs for multiple plots
                    if len(message['multiple_plots']) > 1:
                        tabs = st.tabs([plot_result.get('title', 'Chart ' + str(i+1)) for i, plot_result in enumerate(message['multiple_plots'])])
                        
                        for i, (tab, plot_result) in enumerate(zip(tabs, message['multiple_plots'])):
                            with tab:
                                if 'plot' in plot_result:
                                    st.plotly_chart(plot_result['plot'], use_container_width=True)
                                    
                                    if 'plot_info' in plot_result and plot_result['plot_info']:
                                        with st.expander("ℹ️ Plot Details"):
                                            st.text(plot_result['plot_info'])
                                
                                elif 'plot_error' in plot_result:
                                    st.error("Plot Generation Error: " + plot_result['plot_error'])
                                
                                with st.expander("🔧 Generated Code"):
                                    st.code(plot_result['plot_code'], language='python')
                    else:
                        # Single plot in multiple plots array
                        plot_result = message['multiple_plots'][0]
                        if 'plot' in plot_result:
                            st.plotly_chart(plot_result['plot'], use_container_width=True)
                        elif 'plot_error' in plot_result:
                            st.error("Plot Generation Error: " + plot_result['plot_error'])
                        
                        with st.expander("🔧 Generated Code"):
                            st.code(plot_result['plot_code'], language='python')
                
                # Display single data table
                elif 'data' in message and message['data'] is not None and not message.get('is_dashboard'):
                    if isinstance(message['data'], pd.DataFrame):
                        st.subheader("📊 Data Results")
                        st.dataframe(message['data'])
                    else:
                        st.write(message['data'])
                
                # Display single plot
                elif 'plot' in message:
                    st.subheader("📈 Visualization")
                    st.plotly_chart(message['plot'], use_container_width=True)
                    
                    # Show any additional plot information
                    if 'plot_info' in message and message['plot_info']:
                        with st.expander("Plot Generation Details"):
                            st.text(message['plot_info'])
                    
                    # Show generated code for debugging
                    if 'plot_code' in message and message['plot_code']:
                        with st.expander("🔧 Generated Plot Code"):
                            st.code(message['plot_code'], language='python')
                
                # Display single plot error
                if 'plot_error' in message and not message.get('multiple_plots'):
                    st.error("Plot Generation Error: " + message['plot_error'])
                    if 'plot_code' in message and message['plot_code']:
                        with st.expander("🐛 Problematic Code"):
                            st.code(message['plot_code'], language='python')
            else:
                st.write(message)

def main():
    st.set_page_config(
        page_title="Excel Insights Chatbot",
        page_icon="📊",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("📊 Excelbot")
    st.markdown("Upload your Excel file and ask questions in natural language to get instant insights and visualizations!")
    
    # Sidebar for file upload and data overview
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx'],
            help="Upload a .xlsx file with structured data"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing Excel file..."):
                    st.session_state.data_processor = DataProcessor(uploaded_file)
                    st.session_state.data_uploaded = True
                st.success("File uploaded successfully!")
                
                # Display data overview
                st.header("📋 Data Overview")
                display_data_overview()
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.session_state.data_uploaded = False
    
    # Main chat interface
    if st.session_state.data_uploaded:
        st.header("💬 Chat with your data")
        
        # Display chat history
        for message in st.session_state.chat_history:
            display_chat_message(message['content'], message['is_user'])
        
        # Query input
        if query := st.chat_input("Ask a question about your data..."):
            # Add user message to history
            st.session_state.chat_history.append({
                'content': query,
                'is_user': True
            })
            display_chat_message(query, is_user=True)
            
            # Process query and get response
            with st.spinner("Analyzing your query and generating insights..."):
                response = process_user_query(query)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                'content': response,
                'is_user': False
            })
            display_chat_message(response, is_user=False)
        
        # Example queries
        with st.expander("💡 Example Questions"):
            st.markdown("""
            **📊 Single Analysis:**
            - What is the average of all numeric columns?
            - Show me summary statistics for the data
            - Create a bar chart showing the distribution of [column]
            - Make a histogram of [numeric column]
            
            **📈 Multiple Visualizations:**
            - Show me multiple charts to analyze the data
            - Create several different plots for comparison
            - Generate various visualizations for this dataset
            
            **🎛️ Dashboard & Comprehensive Analysis:**
            - Create a dashboard for this data
            - Give me a comprehensive overview of the dataset
            - Show me a complete analysis with multiple insights
            - Generate a summary dashboard with all key visualizations
            
            **🔍 Data Filtering & Exploration:**
            - How many unique values are in each column?
            - Show me records where [condition]
            - What are the most common values in [column]?
            - Filter data based on specific criteria
            
            **🔗 Advanced Analysis:**
            - Show me correlations between numeric columns
            - Create a correlation heatmap
            - Identify outliers in the data
            - Compare different groups in the data
            """)
        
        # Quick action buttons
        st.subheader("🚀 Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Create Dashboard"):
                st.session_state.chat_history.append({
                    'content': "Create a comprehensive dashboard with multiple visualizations",
                    'is_user': True
                })
                with st.spinner("Creating dashboard..."):
                    response = process_user_query("Create a comprehensive dashboard with multiple visualizations")
                st.session_state.chat_history.append({
                    'content': response,
                    'is_user': False
                })
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        
        with col2:
            if st.button("📈 Multiple Charts"):
                st.session_state.chat_history.append({
                    'content': "Show me multiple different charts to analyze this data",
                    'is_user': True
                })
                with st.spinner("Generating multiple charts..."):
                    response = process_user_query("Show me multiple different charts to analyze this data")
                st.session_state.chat_history.append({
                    'content': response,
                    'is_user': False
                })
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        
        with col3:
            if st.button("🔢 Data Summary"):
                st.session_state.chat_history.append({
                    'content': "Give me statistical summaries of all the data",
                    'is_user': True
                })
                with st.spinner("Calculating statistics..."):
                    response = process_user_query("Give me statistical summaries of all the data")
                st.session_state.chat_history.append({
                    'content': response,
                    'is_user': False
                })
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        
        with col4:
            if st.button("📋 Simple Overview"):
                # Create a guaranteed working simple overview
                summary = st.session_state.data_processor.get_data_summary()
                simple_response = {
                    'text': "Here's a simple overview of your data with basic visualizations that are guaranteed to work:",
                    'is_dashboard': True,
                    'multiple_plots': [],
                    'dashboard_sections': []
                }
                
                # Add simple plots that should always work
                df_for_plot = st.session_state.data_processor.df
                
                # Data shape info
                simple_response['text'] += " Your dataset has " + str(summary['rows']) + " rows and " + str(summary['columns']) + " columns."
                
                # Add first available plot
                if summary['numeric_columns']:
                    col = summary['numeric_columns'][0]
                    fig, _, _ = execute_plot_code("fig = px.histogram(df, x='" + col + "', title='Distribution of " + col.replace('_', ' ').title() + "')", df_for_plot)
                    if fig:
                        simple_response['multiple_plots'].append({
                            'plot': fig,
                            'section_info': {'title': 'Numeric Distribution', 'description': 'Distribution of ' + col.replace('_', ' ').title()}
                        })
                
                if summary['categorical_columns']:
                    col = summary['categorical_columns'][0]
                    fig, _, _ = execute_plot_code("counts = df['" + col + "'].value_counts().head(10); fig = px.bar(x=counts.index, y=counts.values, title='Top Values in " + col.replace('_', ' ').title() + "')", df_for_plot)
                    if fig:
                        simple_response['multiple_plots'].append({
                            'plot': fig,
                            'section_info': {'title': 'Categorical Analysis', 'description': 'Most frequent values in ' + col.replace('_', ' ').title()}
                        })
                
                st.session_state.chat_history.append({
                    'content': "Show me a simple overview of the data",
                    'is_user': True
                })
                st.session_state.chat_history.append({
                    'content': simple_response,
                    'is_user': False
                })
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        
        # Clear chat history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
    
    else:
        st.info("👆 Please upload an Excel file in the sidebar to get started!")
        
        # Show sample usage without data
        st.header("🎯 What can this chatbot do?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Dynamic Data Analysis")
            st.markdown("""
            - **Smart Statistics**: Calculates relevant metrics based on your data
            - **Flexible Filtering**: Understands natural language conditions
            - **Intelligent Grouping**: Groups and aggregates data contextually
            - **Pattern Detection**: Finds correlations and trends automatically
            """)
        
        with col2:
            st.subheader("📊 AI-Generated Visualizations")
            st.markdown("""
            - **Context-Aware Charts**: Creates appropriate visualizations for your query
            - **Custom Plot Generation**: Writes plotting code tailored to your data
            - **Interactive Plots**: All charts are interactive and responsive
            - **Multiple Chart Types**: Bar, line, scatter, pie, histogram, heatmap, and more
            """)
        
        st.header("🚀 How It Works")
        st.markdown("""
        1. **Upload** your Excel file using the sidebar
        2. **Ask** questions in plain English about your data
        3. **Get** instant answers with relevant visualizations
        4. **Explore** further with follow-up questions
        
        The AI understands your data structure and generates custom Python code to create 
        the most appropriate visualizations for your specific questions!
        """)

if __name__ == "__main__":
    main()