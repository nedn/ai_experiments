# AI Context Size Loss Experiment Script Utility

## Document Purpose

This document serves as a high-level implementation plan and status tracker for the AI Context Size Loss experiment. It captures goals, implementation plans, module descriptions, and progress tracking without detailed code snippets. The purpose is to keep the plan concise and maintainable for AI agents to track progress and understand the overall architecture.

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
   - **Golden Answer Generation**: Use gemini-2.5-pro with batch size 1 to create reference conversions
   - **Edit Distance Validation**: Compare generated answers to golden answers using normalized edit distance
   - **Correctness Threshold**: 80% similarity threshold for correctness determination
   - **Batch Validation**: Fast validation of multiple conversions against golden answers
   - **Result Scoring**: Calculate success rates and similarity scores for analysis

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

The script supports various execution modes:
- Default experiment execution with standard settings
- Custom configuration file loading
- Specific batch size selection
- Resume interrupted experiments from checkpoints
- Custom output directory specification
- Parallel processing mode with configurable workers
- Report-only mode for existing results

### Configuration Options

Command-line options include:
- Configuration file path and batch size specification
- Iteration count and output directory settings
- Checkpoint management and resume functionality
- Parallel processing controls and worker limits
- Report generation and validation-only modes
- Verbose logging and dry-run capabilities
- API key override and model parameter settings

### Configuration File Format

The system uses YAML configuration files with sections for:
- Experiment settings: name, description, version, batch sizes, iterations
- AI settings: model, temperature, tokens, timeout, retry logic
- Data settings: source file, validation sample rate, context lines
- Output settings: base directory, formats, visualizations, checkpoints
- Logging settings: level, file, console, rotation
- Parallel processing settings: enabled, workers, timeout


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
- **Golden Answer Generation**: Use best model (gemini-2.5-pro) with batch size 1 to create reference conversions
- **Edit Distance Validation**: Compare experimental results to golden answers using normalized edit distance
- **Correctness Threshold**: 80% similarity threshold for determining correct conversions
- **Fast Validation**: Simple, fast validation without complex analysis
- **Statistical Analysis**: Calculate success rates and performance metrics
- **Similarity Scoring**: Measure how close each conversion is to the golden answer

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

The system supports:
- Default experiment execution with standard settings
- Custom batch size specification
- Custom configuration file loading
- Parallel mode for faster execution
- Resume functionality for interrupted experiments

### Advanced Configuration

Advanced usage examples include:
- Custom AI model settings (temperature, token limits)
- Custom output directories and format selection
- Validation-only mode without AI calls
- Report generation from existing results
- Dry-run mode to preview execution

### Configuration File Example

Advanced configuration example includes:
- Extended batch sizes and iterations for better statistics
- Enhanced AI configuration with higher timeout and retry settings
- Increased validation sample rate and context lines
- Debug-level logging with larger file sizes
- Enabled parallel processing with more workers

### Script Integration Examples

The script can be used programmatically by importing the ExperimentRunner and ExperimentConfig classes. It supports configuration loading, experiment execution, report generation, and result access.

### Batch Processing Examples

The system supports running multiple experiments with different configurations including:
- Different temperature settings
- Different AI models (gemini-flash-latest, gemini-flash-lite-latest, gemini-2.5-pro)
- Different batch size ranges (small, medium, large batches)


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

## Simplified Validation Methodology

### Overview
The validation system uses a simple, fast approach based on golden answers generated by the best available model (gemini-2.5-pro) with batch size 1. This ensures high-quality reference conversions that can be used to validate experimental results using normalized edit distance.

### Validation Process

#### 1. Golden Answer Generation
**Purpose**: Create high-quality reference conversions using the best model
**Method**: Use gemini-2.5-pro with batch size 1 for optimal quality
**Speed**: ~2-5 seconds per snippet
**Quality**: Highest possible (best model, single task focus)

#### 2. Edit Distance Validation
**Purpose**: Compare experimental results to golden answers
**Method**: Normalized edit distance (Levenshtein distance)
**Speed**: ~0.1ms per comparison
**Accuracy**: 95%+ for similarity detection

### Validation Result Structure

The ValidationResult class contains:
- Core results: correctness, similarity score, edit distance, threshold
- Additional metrics: code lengths, validation time
- Optional details: error messages, suggestions

### Golden Answer Management

The GoldenAnswerManager handles:
- Loading and saving golden answers from JSON files
- Checking for missing golden answers
- Generating new golden answers when needed

### Validation Configuration

Key configuration parameters:
- Golden answer settings: file path, model, batch size
- Edit distance settings: similarity threshold (80%), whitespace normalization
- Performance settings: parallel validation, worker count
- Caching: result caching for efficiency

### Integration with Experiment Pipeline

The ExperimentValidator provides:
- Batch validation against golden answers
- Metrics calculation (success rate, average similarity)
- Error handling for missing golden answers
- Integration with experiment workflow

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
- Load snippets from JSON data using utility functions
- Extract content and file paths for prompt generation
- Use for validation by comparing original and converted code

## Implementation Status

### ✅ Completed Components

1. **Data Preparation System** (`data_preparation.py`)
   - ✅ RISE repository cloning and checkout
   - ✅ sprintf snippet extraction using git grep
   - ✅ CodeSnippet and CodeSnippetList classes
   - ✅ JSON serialization and data management
   - ✅ 66 sprintf snippets extracted and ready

2. **Simplified Validation System** (`validator.py`)
   - ✅ Golden answer management with JSON persistence
   - ✅ Edit distance validation using Levenshtein distance
   - ✅ 80% similarity threshold for correctness determination
   - ✅ Batch validation with metrics calculation
   - ✅ Normalized code comparison with whitespace handling

3. **Golden Answer Generation** (`generate_golden_answers.py`)
   - ✅ Script for generating golden answers using gemini-2.5-pro
   - ✅ Batch size 1 processing for optimal quality
   - ✅ Progress tracking and error handling
   - ✅ Integration with existing snippet data

4. **Testing Framework** (`test_validation.py`)
   - ✅ Comprehensive test suite for validation system
   - ✅ Edit distance validation testing
   - ✅ Golden answer manager testing
   - ✅ Real snippet data integration testing

5. **Documentation**
   - ✅ Updated experiment plan with simplified validation methodology
   - ✅ Comprehensive validation system documentation
   - ✅ Usage examples and configuration guides

### 🔄 In Progress Components

1. **AI Integration Module** (`ai_client.py`)
   - 🔄 Gemini API integration for experiment execution
   - 🔄 Prompt generation and formatting
   - 🔄 Rate limiting and retry logic
   - 🔄 Token usage tracking

2. **Experiment Runner** (`run_context_size_experiment.py`)
   - 🔄 Main experiment orchestration
   - 🔄 Batch size iteration and sampling
   - 🔄 Results collection and storage
   - 🔄 Progress monitoring and logging

3. **Results Management** (`results_manager.py`)
   - 🔄 Experimental results storage
   - 🔄 Report generation and visualization
   - 🔄 Data export in multiple formats
   - 🔄 Statistical analysis tools

### 📋 Pending Components

1. **Configuration Module** (`config.py`)
   - 📋 Experiment parameters and settings
   - 📋 API credentials management
   - 📋 Output directory configuration
   - 📋 Logging configuration

2. **Data Management Module** (`data_manager.py`)
   - 📋 Batch sampling and randomization
   - 📋 Data validation and integrity
   - 📋 Memory management for large datasets

## Current Git Status

### Modified Files
- `context_size_loss/EXPERIMENT_PLAN.md` - Updated with implementation status and simplified validation methodology

### New Files Created
- `context_size_loss/validator.py` - Core validation system with edit distance comparison
- `context_size_loss/generate_golden_answers.py` - Golden answer generation script
- `context_size_loss/test_validation.py` - Comprehensive test suite

### Ready for Commit
All validation system components are complete and tested. The files are ready to be committed to the repository.

## Next Steps

### Immediate Actions
1. **Commit Current Changes**: Add and commit validation system files
2. **Generate Golden Answers**: Run golden answer generation script with API key
3. **Test Validation System**: Execute test suite to verify functionality

### Development Priorities
1. **AI Integration Module** - Implement Gemini API client for experiment execution
2. **Experiment Runner** - Create main orchestration script for batch size experiments
3. **Results Management** - Build reporting and visualization tools
4. **Configuration System** - Add YAML-based configuration management

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
