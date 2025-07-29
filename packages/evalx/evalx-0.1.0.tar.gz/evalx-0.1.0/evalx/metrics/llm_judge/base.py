"""
Base LLM-as-judge metric implementation.
"""

import asyncio
import json
from typing import Dict, Any, Union, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from ...core.base import BaseMetric
from ...core.types import EvaluationInput, MetricResult, ModelConfig
from .models import ModelManager
from .structured_output import StructuredOutputParser
from .prompts import PromptLibrary


class LLMJudgeMetric(BaseMetric):
    """
    Base class for LLM-as-judge evaluation metrics.
    
    Provides structured evaluation using language models with advanced
    prompt engineering, few-shot learning, and robust error handling.
    """
    
    def __init__(
        self,
        name: str,
        prompt: str,
        model: str = "gpt-4",
        scale: str = "binary",
        few_shot_examples: Optional[List[Dict[str, Any]]] = None,
        structured_output: bool = True,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        # Determine required inputs based on prompt variables
        required_inputs = self._extract_required_inputs(prompt)
        
        super().__init__(
            name=name,
            description=f"LLM-as-judge metric for {name} using {model}",
            required_inputs=required_inputs,
            **kwargs
        )
        
        self.prompt = prompt
        self.model = model
        self.scale = scale
        self.few_shot_examples = few_shot_examples or []
        self.structured_output = structured_output
        self.system_message = system_message
        
        # Model configuration
        self.model_config = ModelConfig(
            model_id=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Initialize components
        self.model_manager = ModelManager()
        self.output_parser = StructuredOutputParser(scale=scale)
        
        # Build the complete prompt with few-shot examples
        self._build_complete_prompt()
    
    def _extract_required_inputs(self, prompt: str) -> List[str]:
        """Extract required input fields from prompt template."""
        import re
        
        # Find all variables in {variable} format
        variables = re.findall(r'\{(\w+)\}', prompt)
        
        # Map to EvaluationInput fields
        field_mapping = {
            'input': 'input_text',
            'input_text': 'input_text',
            'output': 'output_text',
            'output_text': 'output_text',
            'response': 'output_text',
            'reference': 'reference_text',
            'reference_text': 'reference_text',
            'context': 'context',
        }
        
        required_fields = []
        for var in variables:
            field = field_mapping.get(var, var)
            if field not in required_fields:
                required_fields.append(field)
        
        return required_fields
    
    def _build_complete_prompt(self) -> None:
        """Build the complete prompt including few-shot examples and instructions."""
        prompt_parts = []
        
        # Add system message if provided
        if self.system_message:
            prompt_parts.append(f"System: {self.system_message}")
        
        # Add few-shot examples
        if self.few_shot_examples:
            prompt_parts.append("Here are some examples:")
            for i, example in enumerate(self.few_shot_examples, 1):
                example_text = f"Example {i}:\n"
                example_text += self._format_prompt_variables(example)
                if "score" in example:
                    example_text += f"\nScore: {example['score']}"
                if "reasoning" in example:
                    example_text += f"\nReasoning: {example['reasoning']}"
                prompt_parts.append(example_text)
        
        # Add main evaluation prompt
        prompt_parts.append("Now evaluate the following:")
        prompt_parts.append(self.prompt)
        
        # Add output format instructions
        if self.structured_output:
            format_instructions = self.output_parser.get_format_instructions()
            prompt_parts.append(format_instructions)
        
        self.complete_prompt = "\n\n".join(prompt_parts)
    
    def _format_prompt_variables(self, data: Dict[str, Any]) -> str:
        """Format prompt variables from data dictionary."""
        try:
            return self.prompt.format(**data)
        except KeyError as e:
            # Handle missing variables gracefully
            return self.prompt.replace(f"{{{e.args[0]}}}", f"[Missing: {e.args[0]}]")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _call_model_async(self, formatted_prompt: str) -> str:
        """Call the LLM model with retry logic."""
        try:
            client = self.model_manager.get_client(self.model)
            response = await client.generate_async(
                prompt=formatted_prompt,
                config=self.model_config
            )
            return response
        except Exception as e:
            raise Exception(f"Model call failed: {str(e)}")
    
    def _call_model_sync(self, formatted_prompt: str) -> str:
        """Call the LLM model synchronously."""
        try:
            client = self.model_manager.get_client(self.model)
            response = client.generate(
                prompt=formatted_prompt,
                config=self.model_config
            )
            return response
        except Exception as e:
            raise Exception(f"Model call failed: {str(e)}")
    
    def _compute_score(self, input_data: EvaluationInput) -> Union[float, Dict[str, Any]]:
        """Compute LLM-based evaluation score."""
        try:
            # Format the prompt with input data
            prompt_data = {
                'input_text': input_data.input_text or "",
                'output_text': input_data.output_text or "",
                'reference_text': input_data.reference_text or "",
                'context': input_data.context or "",
                'input': input_data.input_text or "",
                'output': input_data.output_text or "",
                'response': input_data.output_text or "",
                'reference': input_data.reference_text or "",
            }
            
            formatted_prompt = self._format_prompt_variables(prompt_data)
            
            # Call the model
            response = self._call_model_sync(formatted_prompt)
            
            # Parse the response
            if self.structured_output:
                parsed_result = self.output_parser.parse(response)
            else:
                # Simple numeric extraction for unstructured output
                parsed_result = self._extract_numeric_score(response)
            
            return {
                "score": parsed_result.get("score", 0.0),
                "reasoning": parsed_result.get("reasoning", response),
                "raw_response": response,
                "model": self.model,
                "scale": self.scale
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "model": self.model,
                "scale": self.scale
            }
    
    async def _compute_score_async(self, input_data: EvaluationInput) -> Union[float, Dict[str, Any]]:
        """Compute LLM-based evaluation score asynchronously."""
        try:
            # Format the prompt with input data
            prompt_data = {
                'input_text': input_data.input_text or "",
                'output_text': input_data.output_text or "",
                'reference_text': input_data.reference_text or "",
                'context': input_data.context or "",
                'input': input_data.input_text or "",
                'output': input_data.output_text or "",
                'response': input_data.output_text or "",
                'reference': input_data.reference_text or "",
            }
            
            formatted_prompt = self._format_prompt_variables(prompt_data)
            
            # Call the model asynchronously
            response = await self._call_model_async(formatted_prompt)
            
            # Parse the response
            if self.structured_output:
                parsed_result = self.output_parser.parse(response)
            else:
                parsed_result = self._extract_numeric_score(response)
            
            return {
                "score": parsed_result.get("score", 0.0),
                "reasoning": parsed_result.get("reasoning", response),
                "raw_response": response,
                "model": self.model,
                "scale": self.scale
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "model": self.model,
                "scale": self.scale
            }
    
    async def evaluate_async(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate asynchronously using LLM."""
        try:
            self.validate_input(input_data)
            start_time = asyncio.get_event_loop().time()
            
            score_dict = await self._compute_score_async(input_data)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            result = MetricResult(
                metric_name=self.name,
                value=score_dict,
                metadata={
                    "execution_time": execution_time,
                    "weight": self.weight,
                    **self.metadata
                }
            )
            
            # Add confidence and explanation
            if "score" in score_dict:
                result.confidence = self._calculate_confidence(score_dict)
                result.explanation = self._generate_explanation(score_dict)
            
            return result
            
        except Exception as e:
            return MetricResult(
                metric_name=self.name,
                value={"score": 0.0, "error": str(e)},
                metadata={"error": str(e)}
            )
    
    def _extract_numeric_score(self, response: str) -> Dict[str, Any]:
        """Extract numeric score from unstructured response."""
        import re
        
        # Try to find a number between 0 and 1
        numbers = re.findall(r'\b0?\.\d+\b|\b[01]\b', response)
        if numbers:
            try:
                score = float(numbers[0])
                if 0 <= score <= 1:
                    return {"score": score, "reasoning": response}
            except ValueError:
                pass
        
        # Try to find a number on a scale (e.g., 1-5, 1-10)
        scale_matches = re.findall(r'\b([1-9]|10)\b', response)
        if scale_matches:
            try:
                score = int(scale_matches[0])
                # Normalize to 0-1 scale (assuming max is 5 or 10)
                if score <= 5:
                    normalized = (score - 1) / 4  # 1-5 scale
                else:
                    normalized = (score - 1) / 9  # 1-10 scale
                return {"score": normalized, "reasoning": response}
            except ValueError:
                pass
        
        # Default to 0 if no score found
        return {"score": 0.0, "reasoning": response}
    
    def _calculate_confidence(self, score_dict: Dict[str, Any]) -> float:
        """Calculate confidence based on model and response quality."""
        if "error" in score_dict:
            return 0.0
        
        base_confidence = 0.7  # Base confidence for LLM judges
        
        # Adjust based on model quality
        if "gpt-4" in self.model:
            base_confidence += 0.1
        elif "claude-3" in self.model:
            base_confidence += 0.1
        elif "gpt-3.5" in self.model:
            base_confidence -= 0.1
        
        # Adjust based on structured output
        if self.structured_output:
            base_confidence += 0.1
        
        # Adjust based on reasoning quality
        reasoning = score_dict.get("reasoning", "")
        if len(reasoning) > 100:  # Longer reasoning suggests more thoughtful evaluation
            base_confidence += 0.05
        
        return max(0.1, min(1.0, base_confidence))
    
    def _generate_explanation(self, score_dict: Dict[str, Any]) -> str:
        """Generate human-readable explanation."""
        if "error" in score_dict:
            return f"LLM evaluation failed: {score_dict['error']}"
        
        score = score_dict.get("score", 0.0)
        reasoning = score_dict.get("reasoning", "")
        model = score_dict.get("model", self.model)
        
        explanation = f"{self.name.title()} score: {score:.3f} (evaluated by {model}). "
        
        if reasoning and reasoning != score_dict.get("raw_response", ""):
            explanation += f"Reasoning: {reasoning[:200]}..."
        elif reasoning:
            explanation += f"Model response: {reasoning[:200]}..."
        
        return explanation 