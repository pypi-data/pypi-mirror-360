"""
Prompt library for LLM-as-judge metrics.
"""

class PromptLibrary:
    """Library of validated prompts for LLM evaluation."""
    
    PROMPTS = {
        "accuracy": """
        You are an expert evaluator assessing the factual accuracy of responses.
        Rate the accuracy on a scale of 0.0 to 1.0 where:
        - 1.0 = Completely accurate, all facts are correct
        - 0.5 = Partially accurate, some facts are correct
        - 0.0 = Completely inaccurate, facts are wrong
        
        Input: {input_text}
        Output: {output_text}
        Reference: {reference_text}
        
        Provide only a numeric score between 0.0 and 1.0.
        """,
        
        "helpfulness": """
        You are an expert evaluator assessing how helpful a response is to the user.
        Rate the helpfulness on a scale of 0.0 to 1.0 where:
        - 1.0 = Extremely helpful, fully addresses the user's need
        - 0.5 = Moderately helpful, partially addresses the need
        - 0.0 = Not helpful, does not address the user's need
        
        Input: {input_text}
        Output: {output_text}
        
        Provide only a numeric score between 0.0 and 1.0.
        """,
        
        "coherence": """
        You are an expert evaluator assessing the coherence of responses.
        Rate the coherence on a scale of 0.0 to 1.0 where:
        - 1.0 = Perfectly coherent, logical flow
        - 0.5 = Mostly coherent, minor issues
        - 0.0 = Incoherent, hard to follow
        
        Output: {output_text}
        
        Provide only a numeric score between 0.0 and 1.0.
        """,
        
        "groundedness": """
        You are an expert evaluator assessing how well a response is grounded in the provided context.
        Rate the groundedness on a scale of 0.0 to 1.0 where:
        - 1.0 = Fully grounded, all information comes from context
        - 0.5 = Partially grounded, some information from context
        - 0.0 = Not grounded, information not supported by context
        
        Context: {context}
        Output: {output_text}
        
        Provide only a numeric score between 0.0 and 1.0.
        """,
        
        "relevance": """
        You are an expert evaluator assessing the relevance of responses.
        Rate the relevance on a scale of 0.0 to 1.0 where:
        - 1.0 = Highly relevant to the input
        - 0.5 = Moderately relevant
        - 0.0 = Not relevant at all
        
        Input: {input_text}
        Output: {output_text}
        
        Provide only a numeric score between 0.0 and 1.0.
        """
    }
    
    @classmethod
    def get_prompt(cls, name: str) -> str:
        """Get a prompt by name."""
        return cls.PROMPTS.get(name, "Rate this response on a scale of 0.0 to 1.0.") 