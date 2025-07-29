# EvalX: Next-Generation LLM Evaluation Framework

[![PyPI version](https://badge.fury.io/py/evalx.svg)](https://badge.fury.io/py/evalx)
[![Python versions](https://img.shields.io/pypi/pyversions/evalx.svg)](https://pypi.org/project/evalx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

EvalX is a comprehensive evaluation framework for Large Language Model applications that combines traditional metrics, LLM-as-judge evaluations, and intelligent agentic orchestration with research-grade validation.

## 🚀 Key Features

- **🤖 Agentic Orchestration**: Natural language instructions → automatic evaluation planning
- **📊 Comprehensive Metrics**: Traditional + LLM-as-judge + hybrid approaches
- **🔬 Research-Grade Validation**: Statistical analysis, confidence intervals, meta-evaluation
- **🎨 Multimodal Support**: Vision-language, code, audio evaluation
- **⚡ Production Ready**: Async processing, caching, CLI interface
- **🎯 Adaptive Selection**: AI-powered optimal metric selection

## 🏗️ Unique Innovations

### Meta-Evaluation System
EvalX includes the industry's first **meta-evaluation system** that assesses the quality of evaluation metrics themselves:
- Reliability assessment through test-retest analysis
- Validity measurement against ground truth
- Bias detection across demographic groups
- Interpretability scoring

### Adaptive Metric Selection
Automatically selects optimal metrics based on:
- Task type and domain
- Quality requirements (research vs. production)
- Computational constraints
- Fairness requirements

## 📦 Installation

```bash
pip install evalx
```

For development:
```bash
pip install evalx[dev]
```

For research features:
```bash
pip install evalx[research]
```

For production deployment:
```bash
pip install evalx[production]
```

## 🎯 Quick Start

### Natural Language Evaluation
```python
import evalx

# Create evaluation suite from natural language instruction
suite = evalx.EvaluationSuite.from_instruction(
    "Evaluate my chatbot responses for helpfulness and accuracy"
)

# Your data
data = [
    {
        "input": "What's the capital of France?",
        "output": "The capital of France is Paris.",
        "reference": "Paris is the capital city of France."
    }
]

# Run evaluation
results = await suite.evaluate_async(data)
print(results.summary())
```

### Fine-Grained Control
```python
from evalx import MetricSuite

# Create custom metric combination
suite = MetricSuite()
suite.add_traditional_metric("bleu_score")
suite.add_traditional_metric("semantic_similarity", threshold=0.8)
suite.add_llm_judge("accuracy", model="gpt-4")

results = suite.evaluate(data)
```

### Research-Grade Analysis
```python
from evalx import ResearchSuite

# Comprehensive statistical analysis
suite = ResearchSuite(
    metrics=["accuracy", "helpfulness", "bleu"],
    confidence_level=0.95,
    bootstrap_samples=1000
)

results = await suite.evaluate_research_grade(data)
print(f"Mean ± Std: {results.mean:.3f} ± {results.std:.3f}")
print(f"95% CI: [{results.confidence_interval[0]:.3f}, {results.confidence_interval[1]:.3f}]")
```

## 🎨 Multimodal Evaluation

```python
from evalx.metrics.multimodal import MultimodalInput, ImageCaptionQualityMetric

# Image captioning evaluation
input_data = MultimodalInput(
    input_text="Describe this image",
    output_text="A beautiful sunset over the ocean",
    image="path/to/image.jpg"
)

metric = ImageCaptionQualityMetric()
result = metric.evaluate(input_data)
```

## 🔬 Meta-Evaluation

```python
from evalx.meta_evaluation import MetaEvaluator

# Evaluate your metrics' quality
meta_evaluator = MetaEvaluator()
quality_report = meta_evaluator.evaluate_metric_quality(
    metric=my_metric,
    evaluation_data=test_data,
    ground_truth=human_ratings
)

print(f"Metric Quality: {quality_report.overall_quality:.3f}")
print(f"Reliability: {quality_report.reliability:.3f}")
print(f"Validity: {quality_report.validity:.3f}")
print(f"Bias Score: {quality_report.bias:.3f}")
```

## 🖥️ Command Line Interface

```bash
# Evaluate using natural language
evalx evaluate "Check my chatbot for helpfulness" --data data.json

# Research-grade evaluation
evalx research --data data.json --metrics accuracy helpfulness --confidence 0.95

# List available metrics
evalx metrics --list
```

## 📊 Supported Metrics

### Traditional Metrics
- **BLEU**: N-gram overlap with smoothing
- **ROUGE**: Recall-oriented evaluation (ROUGE-1, ROUGE-2, ROUGE-L)
- **METEOR**: Semantic matching with synonyms and stemming
- **BERTScore**: Contextual embedding similarity
- **Semantic Similarity**: Sentence transformer-based
- **Exact Match**: String matching with normalization
- **Levenshtein**: Edit distance with word/character level

### LLM-as-Judge Metrics
- **Accuracy**: Factual correctness assessment
- **Helpfulness**: Response utility evaluation
- **Coherence**: Logical consistency measurement
- **Groundedness**: Source attribution verification
- **Relevance**: Query-response alignment

### Multimodal Metrics
- **Image-Text Alignment**: CLIP-based similarity
- **Image Caption Quality**: Comprehensive captioning assessment
- **Code Correctness**: Syntax, execution, security analysis
- **Audio Quality**: Signal processing metrics

## 🏆 Why EvalX?

| Feature | EvalX | DeepEval | LangChain | Ragas |
|---------|-------|----------|-----------|-------|
| Meta-evaluation | ✅ **Unique** | ❌ | ❌ | ❌ |
| Statistical rigor | ✅ **Best** | Basic | Basic | Good |
| Multimodal support | ✅ **Comprehensive** | Limited | Limited | Limited |
| Adaptive selection | ✅ **Unique** | ❌ | ❌ | ❌ |
| Natural language interface | ✅ **Full** | ❌ | ❌ | ❌ |
| Production ready | ✅ **Complete** | Good | Basic | Good |

## 📚 Documentation

- [Architecture Overview](https://github.com/evalx-ai/evalx/blob/main/ARCHITECTURE.md)
- [Installation Guide](https://github.com/evalx-ai/evalx/blob/main/INSTALLATION_GUIDE.md)
- [Examples](https://github.com/evalx-ai/evalx/tree/main/examples)
- [API Reference](https://evalx.readthedocs.io)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the AI evaluation community
- Inspired by advances in LLM evaluation research
- Designed for both researchers and practitioners

## 📞 Support

- [GitHub Issues](https://github.com/evalx-ai/evalx/issues)
- [Documentation](https://evalx.readthedocs.io)
- [Community Discussions](https://github.com/evalx-ai/evalx/discussions)

---

**EvalX: Making AI evaluation comprehensive, reliable, and accessible.**
