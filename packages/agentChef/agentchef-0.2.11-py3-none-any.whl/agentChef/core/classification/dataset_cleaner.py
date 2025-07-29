import os
import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from tqdm import tqdm
import re
import numpy as np

# Import the PandasQueryIntegration
try:
    from agentChef.core.llamaindex.pandas_query import PandasQueryIntegration, OllamaLlamaIndexIntegration
    HAS_QUERY_INTEGRATION = True
except ImportError:
    HAS_QUERY_INTEGRATION = False

from agentChef.core.crawlers.crawlers_module import ParquetStorageWrapper

class DatasetCleaner:
    """
    A class to clean and validate expanded datasets by comparing them to original conversations
    and identifying/fixing quality issues using NLP queries through an LLM interface.
    
    Works alongside DatasetExpander to ensure high-quality conversation data.
    """
    
    def __init__(self, ollama_interface, output_dir="./cleaned_output", use_llama_index=True):
        """
        Initialize the DatasetCleaner.
        
        Args:
            ollama_interface: An interface to Ollama for generating text and analyzing datasets
            output_dir (str): Directory to save cleaned datasets
            use_llama_index (bool): Whether to use LlamaIndex for advanced DataFrame querying
        """
        self.ollama_interface = ollama_interface
        self.output_dir = output_dir
        self.use_llama_index = use_llama_index
        
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Initialize pandas query integration if available and requested
        self.pandas_query = None
        self.ollama_query = None
        
        if use_llama_index and HAS_QUERY_INTEGRATION:
            try:
                # Remove openai_api_key, just use ollama integration
                self.pandas_query = PandasQueryIntegration(
                    verbose=True,
                    synthesize_response=True
                )
                self.logger.info("Initialized PandasQueryIntegration for advanced DataFrame analysis")
            except ImportError:
                self.logger.warning("LlamaIndex not available. Falling back to OllamaLlamaIndexIntegration.")
                try:
                    self.ollama_query = OllamaLlamaIndexIntegration(
                        ollama_model=getattr(ollama_interface, 'model', "llama3"),
                        verbose=True
                    )
                    self.logger.info("Initialized OllamaLlamaIndexIntegration for DataFrame analysis")
                except ImportError:
                    self.logger.warning("Neither LlamaIndex nor Ollama are available for advanced DataFrame querying")
    
    def _perform_advanced_analysis(self, orig_df: pd.DataFrame, expanded_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform advanced analysis using PandasQueryIntegration.
        
        Args:
            orig_df: DataFrame with original conversations
            expanded_df: DataFrame with expanded conversations
            
        Returns:
            Dictionary with advanced analysis results
        """
        analysis_results = {}
        
        try:
            # If we have the pandas query integration available
            if self.pandas_query:
                # Get insights for both datasets
                orig_insights = self.pandas_query.generate_dataset_insights(orig_df, num_insights=3)
                expanded_insights = self.pandas_query.generate_dataset_insights(expanded_df, num_insights=3)
                
                # Compare the datasets using Parquet storage for efficiency
                storage = ParquetStorageWrapper()
                comparison = self.pandas_query.compare_datasets(
                    orig_df, expanded_df,
                    df1_name="Original", df2_name="Expanded",
                    aspects=["shape", "statistics", "distributions"]
                )
                
                analysis_results = {
                    "original_insights": orig_insights,
                    "expanded_insights": expanded_insights,
                    "comparison": comparison
                }
                
            # Otherwise, if we have the Ollama query integration
            elif self.ollama_query:
                # Form some basic analysis queries
                queries = [
                    "Compare the average content length between original and expanded conversations",
                    "Identify the main differences in word count and sentence structure",
                    "Summarize the key quality differences between original and expanded data"
                ]
                
                # Create a combined dataframe for comparison
                combined_df = pd.concat([
                    orig_df.assign(dataset="original"),
                    expanded_df.assign(dataset="expanded")
                ])
                
                # Run queries
                query_results = {}
                for query in queries:
                    result = self.ollama_query.query_dataframe_with_ollama(combined_df, query)
                    query_results[query] = result
                
                analysis_results = {
                    "ollama_analysis": query_results
                }
                
        except Exception as e:
            self.logger.error(f"Error performing advanced analysis: {str(e)}")
            analysis_results["error"] = str(e)
            
        return analysis_results
    
    def clean_dataset(self, 
                     original_conversations: List[List[Dict[str, str]]], 
                     expanded_conversations: List[List[Dict[str, str]]],
                     cleaning_criteria: Dict[str, bool] = None) -> List[List[Dict[str, str]]]:
        """
        Clean the expanded dataset by fixing identified issues.
        
        Args:
            original_conversations: List of original conversations
            expanded_conversations: List of expanded conversations
            cleaning_criteria: Dictionary of criteria to use for cleaning:
                - fix_hallucinations (bool): Fix factual errors or hallucinations
                - normalize_style (bool): Ensure consistent style
                - correct_grammar (bool): Fix grammar issues
                - ensure_coherence (bool): Ensure conversation flow is coherent
            
        Returns:
            List of cleaned conversations
        """
        if cleaning_criteria is None:
            cleaning_criteria = {
                "fix_hallucinations": True,
                "normalize_style": True,
                "correct_grammar": True,
                "ensure_coherence": True
            }
        
        self.logger.info("Cleaning expanded dataset...")
        
        # First analyze the dataset
        analysis = self.analyze_dataset(original_conversations, expanded_conversations)
        
        # Clean conversations based on analysis
        cleaned_conversations = []
        
        for idx, expanded_conv in enumerate(tqdm(expanded_conversations, desc="Cleaning conversations")):
            # Find corresponding original conversation (if it exists)
            original_idx = idx % len(original_conversations)
            original_conv = original_conversations[original_idx]
            
            # Check if this conversation has issues that need fixing
            needs_cleaning = False
            for issue in analysis["detailed_issues"]:
                if issue["conversation_idx"] == idx:
                    needs_cleaning = True
                    break
            
            if needs_cleaning:
                # Clean this conversation
                cleaned_conv = self._clean_conversation(
                    original_conv, 
                    expanded_conv,
                    cleaning_criteria
                )
                cleaned_conversations.append(cleaned_conv)
            else:
                # Keep as is if no issues detected
                cleaned_conversations.append(expanded_conv)
                
        return cleaned_conversations
    
    def _clean_conversation(self, 
                           original_conv: List[Dict[str, str]], 
                           expanded_conv: List[Dict[str, str]],
                           criteria: Dict[str, bool]) -> List[Dict[str, str]]:
        """
        Clean a single conversation by fixing issues.
        
        Args:
            original_conv: Original conversation
            expanded_conv: Expanded conversation with potential issues
            criteria: Cleaning criteria
            
        Returns:
            Cleaned conversation
        """
        cleaned_conv = []
        
        # Compare each turn in the conversation
        for i, (expanded_turn, original_turn) in enumerate(zip(expanded_conv, original_conv)):
            source = expanded_turn['from']
            
            # Skip if this turn doesn't need cleaning (based on source type)
            if source not in ["human", "gpt"]:
                cleaned_conv.append(expanded_turn.copy())
                continue
                
            # Check and clean this turn
            if self._needs_cleaning(expanded_turn, original_turn, criteria):
                cleaned_value = self._clean_turn_content(
                    original_turn['value'],
                    expanded_turn['value'],
                    source,
                    i,
                    criteria
                )
                
                cleaned_conv.append({
                    'from': source,
                    'value': cleaned_value
                })
            else:
                cleaned_conv.append(expanded_turn.copy())
                
        return cleaned_conv
    
    def _needs_cleaning(self, 
                       expanded_turn: Dict[str, str], 
                       original_turn: Dict[str, str],
                       criteria: Dict[str, bool]) -> bool:
        """
        Determine if a turn needs cleaning based on quick heuristics.
        
        Args:
            expanded_turn: Expanded conversation turn
            original_turn: Original conversation turn
            criteria: Cleaning criteria
            
        Returns:
            True if turn needs cleaning, False otherwise
        """
        expanded_value = expanded_turn['value']
        original_value = original_turn['value']
        
        # Check for obvious issues
        if criteria.get("correct_grammar", False):
            # Look for common grammar issues
            grammar_issues = re.search(r'\b(i\s+is|they\s+is|we\s+is|you\s+is)\b', 
                                      expanded_value, 
                                      re.IGNORECASE)
            if grammar_issues:
                return True
        
        if criteria.get("ensure_coherence", False):
            # Check if expanded content is too short or too long compared to original
            if len(expanded_value) < len(original_value) * 0.5 or len(expanded_value) > len(original_value) * 2:
                return True
        
        # More sophisticated checks would need LLM analysis
        return False
    
    def _clean_turn_content(self, 
                           original_content: str, 
                           expanded_content: str, 
                           source: str,
                           turn_idx: int,
                           criteria: Dict[str, bool]) -> str:
        """
        Clean the content of a conversation turn using LLM.
        
        Args:
            original_content: Content from original turn
            expanded_content: Content from expanded turn
            source: Source of the turn ('human' or 'gpt')
            turn_idx: Index of the turn in the conversation
            criteria: Cleaning criteria
            
        Returns:
            Cleaned turn content
        """
        system_prompt = """You are a conversation data cleaning assistant. Your task is to fix issues in AI-generated 
        conversation data while maintaining the original intent and meaning. Follow these guidelines:
        
        1. Fix any factual errors or hallucinations by referring to the original content
        2. Ensure the text maintains a consistent style appropriate for the source (human or AI assistant)
        3. Correct grammar and spelling issues
        4. Ensure the content is coherent in the context of a conversation
        5. The cleaned content should be a refined version of the expanded content, not just a copy of the original
        
        Return only the cleaned content without additional commentary or explanations."""
        
        # Build criteria-specific instructions
        criteria_instructions = []
        if criteria.get("fix_hallucinations", False):
            criteria_instructions.append("- Fix any factual inconsistencies or hallucinations by referring to the original content")
        if criteria.get("normalize_style", False):
            criteria_instructions.append("- Ensure consistent style and tone appropriate for the source type")
        if criteria.get("correct_grammar", False):
            criteria_instructions.append("- Fix any grammar, spelling, or punctuation errors")
        if criteria.get("ensure_coherence", False):
            criteria_instructions.append("- Ensure the content flows naturally in a conversation context")
        
        criteria_str = "\n".join(criteria_instructions)
        
        user_prompt = f"""Original content: {original_content}
        
        Expanded content (needs cleaning): {expanded_content}
        
        Source type: {source}
        Turn index: {turn_idx}
        
        Please clean the expanded content according to these criteria:
        {criteria_str}
        
        Provide only the cleaned content without any additional text."""

        try:
            response = self.ollama_interface.chat(messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ])
            
            cleaned_content = response['message']['content'].strip()
            return cleaned_content
            
        except Exception as e:
            self.logger.error(f"Error cleaning turn content: {str(e)}")
            return expanded_content  # Return the original expanded content if cleaning fails

    def _convert_conversations_to_df(self, conversations: List[Dict]) -> pd.DataFrame:
        """
        Convert conversations to a pandas DataFrame for analysis.
        
        Args:
            conversations: List of conversation dictionaries
            
        Returns:
            DataFrame with conversation data
        """
        if not conversations:
            return pd.DataFrame()
        
        rows = []
        for conv_idx, conversation in enumerate(conversations):
            # Handle different conversation formats
            if isinstance(conversation, dict):
                # Check if it's a conversation with 'conversations' key
                if 'conversations' in conversation:
                    conv_data = conversation['conversations']
                elif 'messages' in conversation:
                    conv_data = conversation['messages']
                else:
                    # Assume the whole dict is the conversation data
                    conv_data = conversation
                
                # If conv_data is a list (typical conversation format)
                if isinstance(conv_data, list):
                    for turn_idx, turn in enumerate(conv_data):
                        if isinstance(turn, dict):
                            # Extract the actual content based on different possible keys
                            content = ""
                            role = turn.get('from', turn.get('role', 'unknown'))
                            
                            # Try different content keys
                            for key in ['value', 'content', 'text', 'message']:
                                if key in turn and turn[key]:
                                    content = turn[key]
                                    break
                            
                            if not content and 'human' in turn:
                                content = turn['human']
                            elif not content and 'gpt' in turn:
                                content = turn['gpt']
                            
                            rows.append({
                                'conversation_id': conv_idx,
                                'turn_id': turn_idx,
                                'role': role,
                                'content': content,
                                'content_length': len(content) if content else 0
                            })
                elif isinstance(conv_data, dict):
                    # Handle single turn conversations
                    content = ""
                    for key in ['value', 'content', 'text', 'message', 'human', 'gpt']:
                        if key in conv_data and conv_data[key]:
                            content = conv_data[key]
                            break
                    
                    rows.append({
                        'conversation_id': conv_idx,
                        'turn_id': 0,
                        'role': 'unknown',
                        'content': content,
                        'content_length': len(content) if content else 0
                    })
        
        if not rows:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['conversation_id', 'turn_id', 'role', 'content', 'content_length'])
        
        return pd.DataFrame(rows)

    def analyze_dataset(self, original_conversations: List[Dict], expanded_conversations: List[Dict]) -> Dict[str, Any]:
        """
        Analyze the quality of expanded conversations compared to originals.
        
        Args:
            original_conversations: List of original conversation dictionaries
            expanded_conversations: List of expanded conversation dictionaries
            
        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Analyzing expanded dataset quality...")
        
        analysis_results = {
            "total_original": len(original_conversations),
            "total_expanded": len(expanded_conversations),
            "issues_by_type": {},
            "detailed_issues": []
        }
        
        # Convert to dataframes for easier analysis
        orig_df = self._convert_conversations_to_df(original_conversations)
        expanded_df = self._convert_conversations_to_df(expanded_conversations)
        
        # Check if DataFrames are empty
        if orig_df.empty or expanded_df.empty:
            self.logger.warning("One or both DataFrames are empty, skipping analysis")
            analysis_results["error"] = "Empty DataFrames - cannot perform analysis"
            return analysis_results
        
        # Analyze content length differences using the 'content' column
        if 'content' in orig_df.columns and 'content' in expanded_df.columns:
            # Content length is already calculated in _convert_conversations_to_df
            length_diff = self._analyze_length_differences(orig_df, expanded_df)
            analysis_results["length_analysis"] = length_diff
        else:
            self.logger.warning("No content column found in DataFrames")
            analysis_results["length_analysis"] = {"error": "No content column found"}
        
        # If PandasQueryIntegration is available, use it for enhanced analysis
        if self.pandas_query or self.ollama_query:
            try:
                advanced_analysis = self._perform_advanced_analysis(orig_df, expanded_df)
                analysis_results["advanced_analysis"] = advanced_analysis
            except Exception as e:
                self.logger.error(f"Error in advanced analysis: {str(e)}")
                analysis_results["advanced_analysis"] = {"error": str(e)}
        
        # Run NLP analysis on sample pairs
        try:
            semantic_issues = self._analyze_semantic_quality(original_conversations, expanded_conversations)
            analysis_results["issues_by_type"] = semantic_issues["issues_by_type"]
            analysis_results["detailed_issues"] = semantic_issues["detailed_issues"]
        except Exception as e:
            self.logger.error(f"Error in semantic analysis: {str(e)}")
            analysis_results["issues_by_type"] = {"error": str(e)}
            analysis_results["detailed_issues"] = []
        
        return analysis_results

    def _analyze_length_differences(self, orig_df: pd.DataFrame, expanded_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze differences in content length between original and expanded datasets.
        
        Args:
            orig_df: DataFrame with original conversations
            expanded_df: DataFrame with expanded conversations
            
        Returns:
            Dictionary with length analysis results
        """
        try:
            # Use the pre-calculated content_length column
            orig_lengths = orig_df['content_length'].describe()
            expanded_lengths = expanded_df['content_length'].describe()
            
            # Calculate percentage differences
            mean_diff = ((expanded_lengths['mean'] - orig_lengths['mean']) / orig_lengths['mean']) * 100
            median_diff = ((expanded_lengths['50%'] - orig_lengths['50%']) / orig_lengths['50%']) * 100
            
            return {
                "original_stats": orig_lengths.to_dict(),
                "expanded_stats": expanded_lengths.to_dict(),
                "mean_length_change_percent": mean_diff,
                "median_length_change_percent": median_diff,
                "analysis": {
                    "significant_change": abs(mean_diff) > 20,  # Flag if >20% change
                    "direction": "increase" if mean_diff > 0 else "decrease"
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing length differences: {str(e)}")
            return {"error": str(e)}
    
    def set_model(self, model_name: str):
        """Update the model used for dataset cleaning."""
        if self.ollama_interface:
            self.ollama_interface.set_model(model_name)
        self.logger.info(f"Set dataset cleaner model to: {model_name}")
        
        # Update query integration if available
        if self.pandas_query and hasattr(self.pandas_query, 'set_model'):
            self.pandas_query.set_model(model_name)
        if self.ollama_query and hasattr(self.ollama_query, 'set_model'):
            self.ollama_query.set_model(model_name)