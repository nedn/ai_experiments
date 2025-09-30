# AI Context Size Loss Experiment Script Utility

## Overview

This document outlines the development of a comprehensive script utility for running the AI Context Size Loss experiment. The experiment aims to demonstrate that AI models (specifically Gemini) experience higher failure rates when processing prompts with multiple tasks compared to multiple prompts with fewer tasks each. The script utility will automate the entire experimental process using code conversion tasks (sprintf to snprintf) with varying batch sizes to measure performance degradation as context size increases.

## Script Utility Architecture

### Core Components

1. **Experiment Runner Script** (`run_context_size_experiment.py`)
   - Main entry point for running the experiment
   - Command-line interface for configuration
   - Orchestrates all experimental phases
   - Handles logging and progress tracking

2. **Data Management Module** (`data_manager.py`)
   - Loads and preprocesses CodeSnippet data
   - Handles batch sampling and randomization
   - Manages data validation and integrity
   - Provides data access utilities

3. **AI Integration Module** (`ai_client.py`)
   - Interfaces with Gemini API
   - Handles prompt generation and formatting
   - Manages API rate limiting and retries
   - Tracks token usage and costs

4. **Validation Module** (`validator.py`)
   - Automated conversion validation
   - Manual validation sampling
   - Results analysis and scoring
   - Error categorization and reporting

5. **Results Management Module** (`results_manager.py`)
   - Stores experimental results
   - Generates reports and visualizations
   - Exports data in multiple formats
   - Provides result querying capabilities

6. **Configuration Module** (`config.py`)
   - Experiment parameters and settings
   - API credentials management
   - Output directory configuration
   - Logging configuration

### Script Utility Features

- **Automated Experiment Execution**: Run complete experiments with single command
- **Configurable Parameters**: Customize batch sizes, iterations, and validation criteria
- **Progress Tracking**: Real-time progress monitoring and logging
- **Error Handling**: Robust error recovery and retry mechanisms
- **Results Export**: Multiple output formats (JSON, CSV, HTML reports)
- **Visualization**: Automatic chart generation for results analysis
- **Resume Capability**: Resume interrupted experiments from last checkpoint
- **Parallel Processing**: Concurrent execution for faster results

## Command-Line Interface

### Basic Usage

```bash
# Run complete experiment with default settings
python run_context_size_experiment.py

# Run with custom configuration
python run_context_size_experiment.py --config custom_config.yaml

# Run specific batch sizes only
python run_context_size_experiment.py --batch-sizes 1,5,10,20

# Resume interrupted experiment
python run_context_size_experiment.py --resume --checkpoint-dir ./checkpoints

# Run with custom output directory
python run_context_size_experiment.py --output-dir ./results/experiment_001

# Run in parallel mode
python run_context_size_experiment.py --parallel --max-workers 4

# Generate report only (from existing results)
python run_context_size_experiment.py --report-only --results-dir ./results/experiment_001
```

### Configuration Options

```bash
# Available command-line options
python run_context_size_experiment.py --help

Options:
  --config FILE              Configuration file path
  --batch-sizes LIST         Comma-separated list of batch sizes
  --iterations N             Number of iterations per batch size (default: 5)
  --output-dir DIR           Output directory for results
  --checkpoint-dir DIR       Checkpoint directory for resuming
  --resume                   Resume from last checkpoint
  --parallel                 Enable parallel processing
  --max-workers N            Maximum number of parallel workers
  --report-only              Generate report from existing results
  --results-dir DIR          Results directory for report generation
  --verbose                  Enable verbose logging
  --dry-run                  Show what would be executed without running
  --validate-only            Run validation only (no AI calls)
  --api-key KEY              Override API key from config
  --temperature FLOAT        AI model temperature (default: 0.1)
  --max-tokens INT           Maximum tokens per request
  --timeout INT              Request timeout in seconds
```

### Configuration File Format

```yaml
# config.yaml
experiment:
  name: "context_size_loss_experiment"
  description: "AI Context Size Loss Experiment"
  version: "1.0.0"

batch_sizes: [1, 2, 3, 5, 10, 15, 20, 30, 50, 66]
iterations_per_batch: 5
random_seed: 42

ai:
  model: "gemini-flash-latest"
  temperature: 0.1
  max_tokens: 4096
  timeout: 30
  retry_attempts: 3
  retry_delay: 1.0

data:
  source_file: "context_size_loss/rise_data/sprintf_snippets.json"
  validation_sample_rate: 0.1
  max_context_lines: 10

output:
  base_dir: "./results"
  formats: ["json", "csv", "html", "pdf"]
  include_visualizations: true
  checkpoint_interval: 10

logging:
  level: "INFO"
  file: "experiment.log"
  console: true
  max_file_size: "10MB"
  backup_count: 5

parallel:
  enabled: false
  max_workers: 4
  batch_timeout: 300
```


## Script Utility Features

### 1. Automated Experiment Execution
- **Single Command Execution**: Run complete experiments with one command
- **Progress Tracking**: Real-time progress monitoring with detailed logging
- **Error Recovery**: Automatic retry mechanisms for failed requests
- **Checkpoint System**: Resume interrupted experiments from last checkpoint
- **Parallel Processing**: Concurrent execution for faster results

### 2. Data Management
- **Automatic Data Loading**: Load CodeSnippet data from JSON files
- **Smart Sampling**: Stratified random sampling with no snippet reuse
- **Data Validation**: Ensure data integrity and consistency
- **Batch Generation**: Create balanced batches across different sizes
- **Memory Management**: Efficient handling of large datasets

### 3. AI Integration
- **Multi-Model Support**: Support for different AI models (gemini-flash-latest, gemini-flash-lite-latest, gemini-2.5-pro)
- **Rate Limiting**: Intelligent rate limiting and retry logic
- **Token Tracking**: Monitor token usage and costs
- **Response Parsing**: Robust JSON parsing with error handling
- **Prompt Optimization**: Dynamic prompt generation based on batch size

### 4. Validation and Analysis
- **Automated Validation**: Comprehensive validation of conversion results
- **Manual Sampling**: Random sampling for manual validation
- **Error Categorization**: Classify different types of failures
- **Statistical Analysis**: Calculate success rates and performance metrics
- **Quality Scoring**: Multi-dimensional quality assessment

### 5. Results and Reporting
- **Multiple Formats**: Export results in JSON, CSV, HTML, and PDF
- **Visualizations**: Automatic chart generation for results analysis
- **Interactive Reports**: HTML reports with interactive elements
- **Data Export**: Raw data export for further analysis
- **Comparison Tools**: Compare results across different experiments

### 6. Configuration Management
- **YAML Configuration**: Human-readable configuration files
- **Command Line Override**: Override any configuration via CLI
- **Environment Variables**: Support for environment-based configuration
- **Template System**: Pre-built configuration templates
- **Validation**: Configuration validation and error reporting

## Usage Examples

### Basic Experiment Execution

```bash
# Run complete experiment with default settings
python run_experiment.py

# Run with custom batch sizes
python run_experiment.py --batch-sizes 1,5,10,20,50

# Run with custom configuration file
python run_experiment.py --config my_experiment.yaml

# Run in parallel mode for faster execution
python run_experiment.py --parallel --max-workers 4

# Resume interrupted experiment
python run_experiment.py --resume --checkpoint-dir ./checkpoints
```

### Advanced Configuration

```bash
# Run with specific AI model settings
python run_context_size_experiment.py --temperature 0.2 --max-tokens 8192

# Run with custom output directory and formats
python run_context_size_experiment.py --output-dir ./results/exp_001 --formats json,csv,html

# Run validation only (no AI calls)
python run_context_size_experiment.py --validate-only --results-dir ./results/exp_001

# Generate report from existing results
python run_context_size_experiment.py --report-only --results-dir ./results/exp_001

# Dry run to see what would be executed
python run_context_size_experiment.py --dry-run --batch-sizes 1,5,10
```

### Configuration File Example

```yaml
# experiment_config.yaml
experiment:
  name: "context_size_loss_v2"
  description: "Testing AI performance with different batch sizes"
  version: "2.0.0"

# Test different batch sizes
batch_sizes: [1, 2, 3, 5, 10, 15, 20, 30, 50, 66]
iterations_per_batch: 10  # More iterations for better statistics
random_seed: 42

# AI configuration
ai:
  model: "gemini-flash-latest"
  temperature: 0.1
  max_tokens: 4096
  timeout: 60
  retry_attempts: 5
  retry_delay: 2.0

# Data configuration
data:
  source_file: "context_size_loss/rise_data/sprintf_snippets.json"
  validation_sample_rate: 0.15  # 15% manual validation
  max_context_lines: 15

# Output configuration
output:
  base_dir: "./results/experiment_v2"
  formats: ["json", "csv", "html", "pdf"]
  include_visualizations: true
  checkpoint_interval: 5

# Logging configuration
logging:
  level: "DEBUG"
  file: "experiment_v2.log"
  console: true
  max_file_size: "50MB"
  backup_count: 10

# Parallel processing
parallel:
  enabled: true
  max_workers: 8
  batch_timeout: 600
```

### Script Integration Examples

```python
# Using the script programmatically
from run_context_size_experiment import ExperimentRunner
from config import ExperimentConfig

# Load configuration
config = ExperimentConfig.from_file("my_config.yaml")

# Create runner
runner = ExperimentRunner(config)

# Run experiment
results = runner.run_experiment()

# Generate report
runner.generate_report()

# Access results
print(f"Success rate: {results['overall_success_rate']:.2%}")
print(f"Total tokens used: {results['total_tokens']}")
```

### Batch Processing Examples

```bash
# Run multiple experiments with different configurations
for temp in 0.1 0.2 0.3; do
  python run_context_size_experiment.py --temperature $temp --output-dir "./results/temp_$temp"
done

# Run experiments for different models
for model in gemini-flash-latest gemini-flash-lite-latest gemini-2.5-pro; do
  python run_context_size_experiment.py --model $model --output-dir "./results/model_$model"
done

# Run experiments with different batch size ranges
python run_context_size_experiment.py --batch-sizes 1,2,3,4,5 --output-dir "./results/small_batches"
python run_context_size_experiment.py --batch-sizes 10,20,30,40,50 --output-dir "./results/medium_batches"
python run_context_size_experiment.py --batch-sizes 50,60,66 --output-dir "./results/large_batches"
```


## Expected Outcomes

### Success Rate Predictions
- **Batch size 1**: 95-98% success rate
- **Batch size 5**: 90-95% success rate
- **Batch size 10**: 80-90% success rate
- **Batch size 20**: 70-80% success rate
- **Batch size 50**: 50-70% success rate
- **Batch size 66**: 30-50% success rate

### Key Metrics to Track
1. **Accuracy Degradation Curve**: Success rate vs batch size
2. **Failure Threshold**: Batch size where success rate drops below 80%
3. **Cost Efficiency**: Tokens per successful conversion
4. **Time Efficiency**: Response time per successful conversion


## Risk Mitigation

### Technical Risks
1. **API Rate Limits**: Implement exponential backoff and retry logic
2. **Token Limits**: Monitor token usage and implement chunking if needed
3. **Response Parsing**: Implement robust JSON parsing with error handling
4. **Data Quality**: Validate input data and handle edge cases

### Experimental Risks
1. **Sample Bias**: Use random sampling and multiple iterations
2. **Model Variability**: Use consistent temperature and parameters
3. **Validation Errors**: Implement both automated and manual validation
4. **Statistical Significance**: Ensure adequate sample sizes

## Success Criteria

### Primary Success Criteria
- Demonstrate clear correlation between batch size and failure rate
- Identify specific threshold points where performance degrades significantly
- Provide actionable insights for AI prompt design

### Secondary Success Criteria
- Establish baseline performance metrics for sprintf→snprintf conversion
- Create reusable validation framework for code conversion tasks
- Generate cost-benefit analysis for different batch sizes

## CodeSnippet Implementation Details

### Core Classes
- **CodeSnippet**: Immutable data structure for individual code snippets
- **CodeSnippetList**: Immutable collection of frozen CodeSnippet objects
- **Utility Functions**: JSON serialization and conversion helpers

### Key Features
- **Immutability**: Objects can be frozen for thread safety and data integrity
- **JSON Serialization**: Built-in `to_json()` and `from_json()` methods
- **Validation**: Automatic validation of required fields and data types
- **Utility Methods**: Content extraction, line counting, and analysis methods
- **Thread Safety**: Frozen objects are immutable and thread-safe

### Usage in Experiment
```python
# Load snippets
snippets = snippets_from_json_list(json_data)
snippet_list = CodeSnippetList(snippets)

# Generate prompts
for snippet in snippet_list:
    content = snippet.get_full_content()
    file_path = snippet.file_path
    # Use in prompt generation

# Validation
original_content = snippet.get_full_content()
# Compare with converted code
```

## Deliverables

1. **Experimental Results**: Comprehensive dataset of all test results
2. **Analysis Report**: Statistical analysis and insights using CodeSnippet metrics
3. **Visualizations**: Charts showing success rate vs batch size
4. **Code Repository**: All experimental code, validation tools, and CodeSnippet classes
5. **Recommendations**: Best practices for AI prompt design with multiple tasks
6. **CodeSnippet Library**: Reusable code snippet management system

## Future Extensions

1. **Model Comparison**: Test with different AI models (gemini-flash-latest, gemini-flash-lite-latest, gemini-2.5-pro)
2. **Task Complexity**: Test with different types of code conversion tasks
3. **Prompt Optimization**: Experiment with different prompt templates
4. **Context Management**: Test with different context window sizes
5. **Real-world Validation**: Apply findings to actual development workflows

---

*This experiment plan provides a comprehensive framework for investigating the impact of context size on AI model performance when handling multiple tasks in a single prompt.*
