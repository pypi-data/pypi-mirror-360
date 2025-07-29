import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
import random

# Import OllamaInterface
from agentChef.core.ollama.ollama_interface import OllamaInterface

# Import pandas_query if available
try:
    from agentChef.core.llamaindex.pandas_query import OllamaLlamaIndexIntegration
    HAS_QUERY_ENGINE = True
except ImportError:
    HAS_QUERY_ENGINE = False
    logging.warning("LlamaIndex not installed. OllamaLlamaIndexIntegration will not be available.")

class OllamaConversationGenerator:
    """
    A lightweight class to generate formatted conversations using Ollama models.
    Produces conversations in the format with alternating "from": "human" and "from": "gpt" entries.
    Enhanced with NLP hedging and analysis capabilities.
    """
    
    def __init__(self, model_name="llama3", enable_hedging=True, ollama_interface=None):
        """
        Initialize the conversation generator.
        
        Args:
            model_name (str): Name of the Ollama model to use for generating conversations.
            enable_hedging (bool): Whether to enable NLP hedging for more natural responses.
            ollama_interface (OllamaInterface, optional): Pre-configured Ollama interface.
                If None, a new interface will be created.
        """
        self.model = model_name
        self.enable_hedging = enable_hedging
        self.logger = logging.getLogger(__name__)
        
        # Use provided interface or create a new one
        self.ollama = ollama_interface if ollama_interface else OllamaInterface(model_name)
        
        # Initialize OllamaPandasQuery if available
        self.query_engine = None
        if HAS_QUERY_ENGINE and enable_hedging:
            try:
                self.query_engine = OllamaLlamaIndexIntegration(
                    ollama_model=model_name
                )
                self.logger.info("Initialized OllamaLlamaIndexIntegration for conversation analysis")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OllamaLlamaIndexIntegration: {e}")
        
    def generate_conversation(self, content, num_turns=3, conversation_context="research",
                           hedging_level="balanced", conversation_history=None):
        """
        Generate a conversation about the given content using separate human and AI prompts.
        
        Args:
            content (str): The content to generate a conversation about.
            num_turns (int): Number of back-and-forth turns in the conversation.
            conversation_context (str): Context to guide the conversation topic.
            hedging_level (str): Level of hedging to use in responses 
                                 ("confident", "balanced", "cautious").
            conversation_history (list, optional): Previous conversation history to build upon.
            
        Returns:
            list: A list of conversation turns in the format [{"from": "human", "value": "..."},
                                                             {"from": "gpt", "value": "..."}]
            or None if generation fails.
        """
        # Limit content length for the prompt
        truncated_content = content[:2000] if len(content) > 2000 else content
        
        # Build the conversation turn by turn
        conversation = conversation_history[:] if conversation_history else []
        
        try:
            for turn in range(num_turns):
                # Generate human question
                if turn == 0 and not conversation_history:
                    # First question - start the conversation
                    human_question = self._generate_human_question(
                        content=truncated_content,
                        conversation_context=conversation_context,
                        conversation_history=conversation,
                        is_first_question=True
                    )
                else:
                    # Follow-up question based on conversation so far
                    human_question = self._generate_human_question(
                        content=truncated_content,
                        conversation_context=conversation_context,
                        conversation_history=conversation,
                        is_first_question=False
                    )
                
                if not human_question:
                    self.logger.warning(f"Failed to generate human question for turn {turn + 1}")
                    break
                    
                conversation.append({"from": "human", "value": human_question})
                
                # Generate AI response
                ai_response = self._generate_ai_response(
                    content=truncated_content,
                    conversation_context=conversation_context,
                    conversation_history=conversation,
                    hedging_level=hedging_level
                )
                
                if not ai_response:
                    self.logger.warning(f"Failed to generate AI response for turn {turn + 1}")
                    # Remove the human question if we can't generate a response
                    conversation.pop()
                    break
                    
                conversation.append({"from": "gpt", "value": ai_response})
            
            # Validate the final conversation
            if conversation:
                self._validate_conversation_format(conversation)
                return conversation
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating conversation: {str(e)}")
            return None

    def _generate_human_question(self, content, conversation_context, conversation_history, is_first_question=False):
        """Generate a human question based on the content and conversation history."""
        
        if is_first_question:
            human_prompt = f"""You are a curious human asking questions about {conversation_context} content. 
            You have just been presented with the following information:

            {content}

            Generate a natural, engaging question that a human would ask to start learning about this topic. 
            The question should:
            - Be genuinely curious and show interest in understanding the content
            - Be specific enough to elicit a detailed response
            - Sound like how a real person would phrase a question
            - Be appropriate for the {conversation_context} context
            
            Return ONLY the question text, nothing else."""
        else:
            # Build conversation context for follow-up questions
            conversation_text = ""
            for turn in conversation_history:
                role = "Human" if turn["from"] == "human" else "AI Assistant"
                conversation_text += f"{role}: {turn['value']}\n\n"
            
            human_prompt = f"""You are a curious human continuing a conversation about {conversation_context} content.

            Original Content:
            {content}

            Conversation so far:
            {conversation_text}

            Generate a natural follow-up question that:
            - Builds on what has been discussed already
            - Shows deeper curiosity or asks for clarification/examples
            - Sounds like how a real person would continue the conversation
            - Doesn't repeat what has already been asked
            - Is appropriate for the {conversation_context} context
            
            Return ONLY the question text, nothing else."""
        
        try:
            response = self.ollama.chat(
                messages=[{"role": "system", "content": human_prompt}]
            )
            question = response['message']['content'].strip()
            
            # Clean up any extra formatting
            question = self._clean_generated_text(question)
            
            # Ensure it ends with a question mark
            if question and not question.endswith('?'):
                question += '?'
                
            return question if question else None
            
        except Exception as e:
            self.logger.error(f"Error generating human question: {str(e)}")
            return None

    def _generate_ai_response(self, content, conversation_context, conversation_history, hedging_level):
        """Generate an AI response based on the content and conversation history."""
        
        # Get hedging instructions
        hedging_instructions = self._get_hedging_instructions(hedging_level)
        
        # Build conversation context
        conversation_text = ""
        for turn in conversation_history:
            role = "Human" if turn["from"] == "human" else "AI Assistant"
            conversation_text += f"{role}: {turn['value']}\n\n"
        
        # Get the latest human question
        latest_question = conversation_history[-1]["value"] if conversation_history else "Please explain this content."
        
        ai_prompt = f"""You are a helpful AI assistant answering questions about {conversation_context} content.

        Original Content:
        {content}

        Conversation so far:
        {conversation_text}

        The human just asked: "{latest_question}"

        Provide a helpful, informative response that:
        - Directly addresses the human's question
        - Is based on the provided content
        - Is educational but conversational in tone
        - Shows expertise while remaining accessible
        - Builds naturally on the conversation flow
        
        {hedging_instructions}
        
        Return ONLY the response text, nothing else."""
        
        try:
            response = self.ollama.chat(
                messages=[{"role": "system", "content": ai_prompt}]
            )
            answer = response['message']['content'].strip()
            
            # Clean up any extra formatting
            answer = self._clean_generated_text(answer)
            
            return answer if answer else None
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {str(e)}")
            return None

    def _clean_generated_text(self, text):
        """Clean generated text of common formatting issues."""
        if not text:
            return text
            
        # Remove common prefixes that might leak through
        prefixes_to_remove = [
            "Question:", "Answer:", "Response:", "Human:", "AI:", "Assistant:",
            "Q:", "A:", "Here's a question:", "Here's the answer:", "I would ask:",
            "My response would be:", "The question is:", "The answer is:"
        ]
        
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
        
        # Remove quotes that might wrap the entire response
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1].strip()
        
        # Remove any remaining extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _get_hedging_instructions(self, hedging_level="balanced"):
        """
        Get instructions for hedging in AI responses based on the specified level.
        
        Args:
            hedging_level (str): Level of hedging ("confident", "balanced", "cautious")
            
        Returns:
            str: Hedging instructions
        """
        if not self.enable_hedging:
            return ""
            
        instructions = {
            "confident": """
            For AI assistant responses, use confident language with minimal hedging:
            - Use phrases like "This is..." rather than "I think this might be..."
            - Make direct statements about the content
            - Acknowledge limitations, but emphasize what is known with confidence
            - Avoid excessive qualifiers like "perhaps", "maybe", "possibly"
            """,
            
            "balanced": """
            For AI assistant responses, use balanced hedging appropriate to the confidence level:
            - Use phrases like "Based on the content..." or "It appears that..."
            - Express appropriate uncertainty when information is incomplete
            - Acknowledge limitations while still providing helpful information
            - Use natural, conversational hedging that doesn't undermine expertise
            """,
            
            "cautious": """
            For AI assistant responses, use careful hedging to express appropriate caution:
            - Use phrases like "From what I understand..." or "It seems possible that..."
            - Explicitly acknowledge limitations of knowledge
            - Make clear when you're making educated guesses vs. stating facts
            - Offer multiple perspectives or interpretations when appropriate
            - Use qualifiers like "likely", "possibly", "it appears" appropriately
            """
        }
        
        return instructions.get(hedging_level, instructions["balanced"])
    
    def _validate_conversation_format(self, conversation):
        """
        Validate that the conversation follows the expected format.
        Ensures each entry has "from" and "value" fields and corrects any issues.
        
        Args:
            conversation (list): The conversation to validate.
            
        Raises:
            ValueError: If the conversation format is invalid and can't be fixed.
        """
        if not isinstance(conversation, list):
            raise ValueError("Conversation is not a list")
            
        for i, turn in enumerate(conversation):
            # Ensure each turn has 'from' and 'value' keys
            if not isinstance(turn, dict):
                raise ValueError(f"Turn {i} is not a dictionary")
                
            # Normalize 'from' key, handle variations like 'role', 'speaker', etc.
            if 'from' not in turn:
                if 'role' in turn:
                    turn['from'] = 'human' if turn['role'] in ['user', 'human'] else 'gpt'
                elif 'speaker' in turn:
                    turn['from'] = 'human' if turn['speaker'] in ['user', 'human'] else 'gpt'
                else:
                    # Alternate based on position
                    turn['from'] = 'human' if i % 2 == 0 else 'gpt'
            
            # Normalize 'value' key, handle variations like 'content', 'message', 'text', etc.
            if 'value' not in turn:
                for key in ['content', 'message', 'text']:
                    if key in turn:
                        turn['value'] = turn[key]
                        break
                else:
                    raise ValueError(f"Turn {i} is missing 'value' or equivalent field")
            
            # Normalize "from" values
            if turn['from'].lower() in ['assistant', 'ai', 'bot', 'claude']:
                turn['from'] = 'gpt'
            elif turn['from'].lower() in ['user', 'human', 'person']:
                turn['from'] = 'human'
            
            # Ensure it's one of the two expected values
            if turn['from'] not in ['human', 'gpt']:
                turn['from'] = 'human' if i % 2 == 0 else 'gpt'
    
    def analyze_conversation_hedging(self, conversations):
        """
        Analyze hedging patterns in a set of conversations.
        
        Args:
            conversations (list): List of conversations to analyze
            
        Returns:
            dict: Analysis of hedging patterns
        """
        if not self.query_engine:
            # Do basic analysis without query engine
            return self._basic_hedging_analysis(conversations)
            
        # Convert conversations to DataFrame
        df = self._conversations_to_df(conversations)
        
        # Use query engine for advanced analysis
        try:
            hedging_analysis = self.query_engine.analyze_conversation_data(
                df, analysis_type="hedging"
            )
            return hedging_analysis
        except Exception as e:
            self.logger.error(f"Error using query engine for hedging analysis: {e}")
            return self._basic_hedging_analysis(conversations)
    
    def _basic_hedging_analysis(self, conversations):
        """
        Perform basic analysis of hedging patterns without using the query engine.
        
        Args:
            conversations (list): List of conversations to analyze
            
        Returns:
            dict: Basic analysis of hedging patterns
        """
        # Define common hedging phrases
        hedging_phrases = [
            "I think", "perhaps", "possibly", "might", "may", "could",
            "in my opinion", "it seems", "probably", "likely", "unlikely",
            "as far as I know", "to my knowledge", "I believe"
        ]
        
        results = {
            "total_conversations": len(conversations),
            "total_turns": 0,
            "hedging_counts": {phrase: 0 for phrase in hedging_phrases},
            "by_source": {"human": 0, "gpt": 0},
            "examples": []
        }
        
        for conv in conversations:
            for turn in conv:
                results["total_turns"] += 1
                source = turn.get('from', '')
                value = turn.get('value', '')
                
                                        # Count hedging phrases
                for phrase in hedging_phrases:
                    if re.search(r'\b' + re.escape(phrase) + r'\b', value, re.IGNORECASE):
                        results["hedging_counts"][phrase] += 1
                        results["by_source"][source] += 1
                        
                        # Store example if not too many already
                        if len(results["examples"]) < 10:
                            results["examples"].append({
                                "phrase": phrase,
                                "source": source,
                                "text": value[:100] + "..." if len(value) > 100 else value
                            })
        
        # Calculate percentages
        gpt_turns = sum(1 for conv in conversations for turn in conv if turn.get('from') == 'gpt')
        human_turns = results["total_turns"] - gpt_turns
        
        if gpt_turns > 0:
            results["gpt_hedging_rate"] = results["by_source"]["gpt"] / gpt_turns
        else:
            results["gpt_hedging_rate"] = 0
            
        if human_turns > 0:
            results["human_hedging_rate"] = results["by_source"]["human"] / human_turns
        else:
            results["human_hedging_rate"] = 0
            
        return results
    
    def _conversations_to_df(self, conversations):
        """
        Convert conversations to a DataFrame for analysis.
        
        Args:
            conversations (list): List of conversations to convert
            
        Returns:
            pd.DataFrame: DataFrame representation of conversations
        """
        rows = []
        
        for conv_idx, conversation in enumerate(conversations):
            for turn_idx, turn in enumerate(conversation):
                source = turn.get('from', '')
                value = turn.get('value', '')
                
                row = {
                    'conversation_idx': conv_idx,
                    'turn_idx': turn_idx,
                    'from': source,
                    'value': value,
                    'is_question': '?' in value[-5:],  # Simple check if it ends with a question
                    'length': len(value),
                    'word_count': len(value.split())
                }
                
                # Add hedging features
                hedging_phrases = [
                    "I think", "perhaps", "possibly", "might", "may", "could",
                    "in my opinion", "it seems", "probably", "likely", "unlikely",
                    "as far as I know", "to my knowledge", "I believe"
                ]
                
                for phrase in hedging_phrases:
                    row[f'has_{phrase.replace(" ", "_")}'] = int(
                        re.search(r'\b' + re.escape(phrase) + r'\b', value, re.IGNORECASE) is not None
                    )
                
                rows.append(row)
        
        return pd.DataFrame(rows)
    
    def generate_conversations_batch(self, content_chunks, num_turns=3, context="research",
                                  hedging_level="balanced"):
        """
        Generate multiple conversations from a list of content chunks.
        
        Args:
            content_chunks (list): List of text chunks to generate conversations about.
            num_turns (int): Number of turns in each conversation.
            context (str): Context to guide the conversation topic.
            hedging_level (str): Level of hedging to use.
            
        Returns:
            list: List of generated conversations.
        """
        conversations = []
        for i, chunk in enumerate(content_chunks):
            self.logger.info(f"Generating conversation {i+1}/{len(content_chunks)}...")
            conversation = self.generate_conversation(
                chunk, 
                num_turns, 
                context,
                hedging_level=hedging_level
            )
            if conversation:
                conversations.append(conversation)
        return conversations
    
    @staticmethod
    def chunk_text(content, chunk_size=2000, overlap=200):
        """
        Split text content into overlapping chunks of specified size.
        
        Args:
            content (str): Text to split into chunks.
            chunk_size (int): Maximum size of each chunk.
            overlap (int): Number of characters to overlap between chunks.
            
        Returns:
            list: List of text chunks.
        """
        chunks = []
        if len(content) <= chunk_size:
            return [content]
            
        start = 0
        while start < len(content):
            end = start + chunk_size
            if end >= len(content):
                chunks.append(content[start:])
                break
                
            # Try to end at a sentence or paragraph boundary
            for boundary in ['\n\n', '\n', '. ', '? ', '! ']:
                boundary_pos = content.rfind(boundary, start, end)
                if boundary_pos > start:
                    end = boundary_pos + len(boundary)
                    break
                    
            chunks.append(content[start:end])
            start = end - overlap
            
        return chunks
    
    def generate_hedged_response(self, prompt, hedging_profile="balanced", 
                              knowledge_level="medium", subject_expertise="general"):
        """
        Generate a response with appropriate hedging based on the specified profile.
        
        Args:
            prompt (str): The prompt to respond to
            hedging_profile (str): Hedging profile to use ("confident", "balanced", "cautious")
            knowledge_level (str): Level of knowledge about the topic ("high", "medium", "low")
            subject_expertise (str): Level of expertise in the subject
            
        Returns:
            str: Generated response with appropriate hedging
        """
        # Build hedging instructions based on profile
        hedging_instructions = self._get_hedging_instructions(hedging_profile)
        
        # Add knowledge level guidance
        knowledge_guidance = {
            "high": "You have extensive knowledge about this topic. Use confident language while still maintaining appropriate academic caution.",
            "medium": "You have moderate knowledge about this topic. Use balanced language that acknowledges limitations while providing helpful information.",
            "low": "You have limited knowledge about this topic. Use cautious language that clearly communicates uncertainty while still being helpful."
        }.get(knowledge_level, "You have moderate knowledge about this topic.")
        
        system_prompt = f"""You are an AI assistant responding to a question or prompt.
        {knowledge_guidance}
        
        {hedging_instructions}
        
        Your response should be informative, helpful, and appropriately hedged based on your confidence level.
        The subject area is {subject_expertise}.
        """
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            self.logger.error(f"Error generating hedged response: {str(e)}")
            return f"I apologize, but I couldn't generate a response due to an error: {str(e)}"
    
    def set_model(self, model_name: str):
        """Update the model used for generation."""
        self.model = model_name
        if self.ollama:
            self.ollama.set_model(model_name)
        self.logger.info(f"Set conversation generator model to: {model_name}")
        
        # Update query engine if it exists
        if self.query_engine and hasattr(self.query_engine, 'set_model'):
            self.query_engine.set_model(model_name)


# Example usage:
if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Sample content to generate conversation about
    sample_content = """
    Attention mechanisms have become an integral part of compelling sequence modeling
    and transduction models in various tasks, allowing modeling of dependencies without
    regard to their distance in the input or output sequences. In this paper we present the
    Transformer, a model architecture eschewing recurrence and instead relying entirely
    on an attention mechanism to draw global dependencies between input and output.
    """
    
    # Initialize the generator
    generator = OllamaConversationGenerator(model_name="llama3", enable_hedging=True)
    
    # Generate a conversation
    conversation = generator.generate_conversation(
        sample_content, 
        num_turns=3,
        conversation_context="AI research",
        hedging_level="balanced"
    )
    
    # Print the formatted conversation
    if conversation:
        print(json.dumps(conversation, indent=2))
    else:
        print("Failed to generate conversation")
        
    # Generate a hedged response
    prompt = "Explain how transformer models work in simple terms"
    hedged_response = generator.generate_hedged_response(
        prompt,
        hedging_profile="balanced",
        knowledge_level="high",
        subject_expertise="machine learning"
    )
    
    print("\nHedged Response:")
    print(hedged_response)
