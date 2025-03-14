# Changelog

## [Unreleased]

### Added
- Implemented a new prompt template system for managing and generating prompts
- Added JSON template files for all analysis types (financial, competitive, growth, risk)
- Created a summary template for investment recommendations
- Added a planning template for determining next steps
- Added test scripts for the prompt template system and analysis agent
- Added test script for the orchestrator to verify integration with the updated AnalysisAgent
- Added `extract_output_to_dict` method to PromptTemplate class for parsing structured output from LLMs
- Added support for XML-like tags, JSON, and key-value formats in output extraction

### Changed
- Updated `analysis_prompts.py` to use the new prompt template system
- Refactored `AnalysisAgent` class to use the new prompt template system
- Improved the summarize_analyses method to use the template-based summary_prompt
- Enhanced documentation in README.md to explain the prompt template system
- Updated orchestrator.py to use the ToolAgent's execute_tool method instead of direct method calls
- Made output_format parameter optional in PromptTemplate constructor

### Fixed
- Fixed initialization bug in AnalysisAgent class by adding OpenAI client initialization
- Improved error handling in prompt generation functions
- Fixed compatibility issues between orchestrator.py and the updated AnalysisAgent
- Fixed nested tag handling in XML-like output extraction

## [0.1.0] - 2023-05-15

### Added
- Initial release of DeepThinkingChain
- Basic implementation of AnalysisAgent
- Support for financial data analysis
- Integration with OpenAI API 