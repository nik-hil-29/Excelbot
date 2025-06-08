import pandas as pd
import numpy as np
import re
from typing import Dict, Any, Optional, Union
import io

class DataProcessor:
    """Handles Excel file processing and data analysis operations"""
    
    def __init__(self, uploaded_file):
        """Initialize with uploaded Excel file"""
        self.original_file = uploaded_file
        self.df = self._load_and_process_excel(uploaded_file)
        self.column_mapping = self._create_column_mapping()
        
    def _load_and_process_excel(self, uploaded_file) -> pd.DataFrame:
        """Load and preprocess Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Handle missing column names
            df = self._handle_missing_column_names(df)
            
            # Clean column names
            df.columns = self._normalize_column_names(df.columns)
            
            # Basic data cleaning
            df = self._clean_data(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def _handle_missing_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle Excel files with missing or unnamed columns"""
        new_columns = []
        
        for i, col in enumerate(df.columns):
            col_str = str(col).strip()
            
            # Check if column name is missing or generic
            if (col_str.startswith('Unnamed:') or 
                col_str in ['', 'nan', 'NaN', 'None'] or
                col_str.isdigit() or
                len(col_str) == 0):
                new_columns.append(f'Column {i + 1}')
            else:
                new_columns.append(col_str)
        
        df.columns = new_columns
        return df
    
    def _normalize_column_names(self, columns):
        """Normalize column names for consistent processing"""
        normalized = []
        for col in columns:
            # Convert to string and strip whitespace
            col_str = str(col).strip()
            # Replace spaces and special characters with underscores
            col_normalized = re.sub(r'[^\w]', '_', col_str.lower())
            # Remove multiple consecutive underscores
            col_normalized = re.sub(r'_+', '_', col_normalized)
            # Remove leading/trailing underscores
            col_normalized = col_normalized.strip('_')
            normalized.append(col_normalized)
        return normalized
    
    def _create_column_mapping(self) -> Dict[str, str]:
        """Create mapping between normalized and original column names"""
        original_cols = pd.read_excel(self.original_file, engine='openpyxl').columns
        return dict(zip(self.df.columns, original_cols))
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform basic data cleaning operations"""
        # Convert obvious numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric if possible
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if not numeric_series.isna().all():
                    # If more than 80% of values are numeric, convert the column
                    if (numeric_series.notna().sum() / len(df)) > 0.8:
                        df[col] = numeric_series
        
        # Convert date columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary"""
        summary = {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'dtypes': dict(zip(self.df.columns, self.df.dtypes.astype(str))),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_columns': self.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object']).columns.tolist(),
            'datetime_columns': self.df.select_dtypes(include=['datetime64']).columns.tolist()
        }
        return summary
    
    def get_data_context(self) -> str:
        """Generate context string for LLM about the dataset"""
        summary = self.get_data_summary()
        
        context = f"""
        Dataset Information:
        - Total rows: {summary['rows']}
        - Total columns: {summary['columns']}
        
        Column Details:
        """
        
        for col in self.df.columns:
            original_name = self.column_mapping.get(col, col)
            dtype = summary['dtypes'][col]
            missing = summary['missing_values'][col]
            
            context += f"\n- {original_name} ({col}): {dtype}"
            if missing > 0:
                context += f" - {missing} missing values"
            
            # Add sample values for categorical columns
            if dtype == 'object' and col in summary['categorical_columns']:
                unique_vals = self.df[col].dropna().unique()[:5]
                context += f" - Sample values: {', '.join(map(str, unique_vals))}"
            
            # Add range for numeric columns
            elif col in summary['numeric_columns']:
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                context += f" - Range: {min_val} to {max_val}"
        
        return context
    
    def execute_data_query(self, operation: Dict[str, Any]) -> Optional[Union[pd.DataFrame, Dict, float, int]]:
        """Execute data operations based on LLM instructions"""
        try:
            operation_type = operation.get('type', '')
            
            if operation_type == 'statistical_summary':
                return self._get_statistical_summary(operation.get('columns', []))
            
            elif operation_type == 'filter':
                return self._filter_data(operation.get('conditions', {}))
            
            elif operation_type == 'group_by':
                return self._group_by_analysis(
                    operation.get('group_column', ''),
                    operation.get('agg_column', ''),
                    operation.get('agg_function', 'count')
                )
            
            elif operation_type == 'correlation':
                return self._get_correlation_analysis(operation.get('columns', []))
            
            elif operation_type == 'value_counts':
                return self._get_value_counts(operation.get('column', ''))
            
            elif operation_type == 'custom_query':
                return self._execute_custom_query(operation.get('query', ''))
            
            else:
                return None
                
        except Exception as e:
            print(f"Error executing data query: {str(e)}")
            return None
    
    def _get_statistical_summary(self, columns: list = None) -> pd.DataFrame:
        """Get statistical summary for specified columns"""
        if not columns:
            # Get all numeric columns
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filter columns that exist in dataframe
        valid_columns = [col for col in columns if col in self.df.columns]
        
        if not valid_columns:
            return pd.DataFrame()
        
        return self.df[valid_columns].describe()
    
    def _filter_data(self, conditions: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on conditions"""
        filtered_df = self.df.copy()
        
        for column, condition in conditions.items():
            if column not in self.df.columns:
                continue
                
            operator = condition.get('operator', '==')
            value = condition.get('value')
            
            if operator == '==':
                filtered_df = filtered_df[filtered_df[column] == value]
            elif operator == '!=':
                filtered_df = filtered_df[filtered_df[column] != value]
            elif operator == '>':
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == '<':
                filtered_df = filtered_df[filtered_df[column] < value]
            elif operator == '>=':
                filtered_df = filtered_df[filtered_df[column] >= value]
            elif operator == '<=':
                filtered_df = filtered_df[filtered_df[column] <= value]
            elif operator == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), case=False, na=False)]
        
        return filtered_df
    
    def _group_by_analysis(self, group_column: str, agg_column: str = None, agg_function: str = 'count') -> pd.DataFrame:
        """Perform group by analysis"""
        if group_column not in self.df.columns:
            return pd.DataFrame()
        
        if agg_column and agg_column not in self.df.columns:
            agg_column = None
        
        if agg_column:
            if agg_function == 'count':
                result = self.df.groupby(group_column)[agg_column].count().reset_index()
            elif agg_function == 'sum':
                result = self.df.groupby(group_column)[agg_column].sum().reset_index()
            elif agg_function == 'mean':
                result = self.df.groupby(group_column)[agg_column].mean().reset_index()
            elif agg_function == 'median':
                result = self.df.groupby(group_column)[agg_column].median().reset_index()
            else:
                result = self.df.groupby(group_column)[agg_column].count().reset_index()
        else:
            result = self.df.groupby(group_column).size().reset_index(name='count')
        
        return result
    
    def _get_correlation_analysis(self, columns: list = None) -> pd.DataFrame:
        """Get correlation analysis for numeric columns"""
        if not columns:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numeric_cols = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['int64', 'float64']]
        
        if len(numeric_cols) < 2:
            return pd.DataFrame()
        
        return self.df[numeric_cols].corr()
    
    def _get_value_counts(self, column: str) -> pd.DataFrame:
        """Get value counts for a specific column"""
        if column not in self.df.columns:
            return pd.DataFrame()
        
        value_counts = self.df[column].value_counts().reset_index()
        value_counts.columns = [column, 'count']
        return value_counts
    
    def _execute_custom_query(self, query: str) -> pd.DataFrame:
        """Execute custom pandas query (limited for security)"""
        try:
            # Basic safety check - only allow read operations
            forbidden_keywords = ['drop', 'delete', 'insert', 'update', 'exec', 'eval']
            if any(keyword in query.lower() for keyword in forbidden_keywords):
                return pd.DataFrame()
            
            # Execute query on dataframe
            result = self.df.query(query)
            return result
        except:
            return pd.DataFrame()
    
    def get_column_suggestions(self, partial_name: str) -> list:
        """Get column suggestions based on partial name match"""
        suggestions = []
        partial_lower = partial_name.lower()
        
        for col in self.df.columns:
            original_name = self.column_mapping.get(col, col)
            if partial_lower in col.lower() or partial_lower in original_name.lower():
                suggestions.append((original_name, col))
        
        return suggestions