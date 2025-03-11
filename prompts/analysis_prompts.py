"""
Prompt templates for the Analysis Agent.

This module contains templates for generating prompts for the Analysis Agent
to analyze financial data and extract investment insights.
"""

# Base template for financial analysis
FINANCIAL_ANALYSIS_TEMPLATE = """
You are a financial analyst tasked with analyzing {symbol} as an investment opportunity.
Based on the provided financial data, conduct a comprehensive analysis focusing on:

1. Business Overview:
   - Core business model and revenue streams
   - Market position and competitive landscape

2. Financial Health:
   - Key financial metrics and ratios
   - Balance sheet strength and debt levels
   - Cash flow generation and capital allocation

3. Growth Prospects:
   - Historical growth rates and future projections
   - Market opportunities and expansion potential
   - R&D investments and innovation pipeline

4. Competitive Advantages:
   - Moat analysis (brand, network effects, switching costs, etc.)
   - Intellectual property and technological advantages
   - Scale advantages and operational efficiencies

5. Risks and Challenges:
   - Market risks and competitive threats
   - Regulatory and legal challenges
   - Financial risks (debt, liquidity, etc.)
   - Technological disruption risks

6. Valuation Assessment:
   - Current valuation metrics compared to historical averages and peers
   - Potential fair value range
   - Key valuation drivers

Provide a structured analysis with clear sections. Support your insights with specific data points from the provided information.

DATA:
{data}
"""

# Template for competitive analysis
COMPETITIVE_ANALYSIS_TEMPLATE = """
You are a financial analyst tasked with conducting a competitive analysis of {symbol} relative to its peers.
Based on the provided data, analyze:

1. Market Position:
   - Market share and positioning
   - Relative growth rates compared to industry
   - Competitive dynamics and industry structure

2. Comparative Financial Performance:
   - Revenue and earnings growth vs. peers
   - Margin analysis and operational efficiency
   - Return metrics (ROE, ROIC) comparison

3. Competitive Advantages:
   - Differentiation factors
   - Cost advantages or disadvantages
   - Brand strength and customer loyalty

4. Threats and Opportunities:
   - Emerging competitors and potential disruptors
   - Market share gain/loss trends
   - Strategic positioning for future industry developments

Provide specific comparisons to the peer companies mentioned in the data, highlighting where {symbol} outperforms or underperforms its competitors.

DATA:
{data}
"""

# Template for growth analysis
GROWTH_ANALYSIS_TEMPLATE = """
You are a financial analyst tasked with evaluating the growth prospects of {symbol}.
Based on the provided data, analyze:

1. Historical Growth Patterns:
   - Revenue, earnings, and cash flow growth rates
   - Organic vs. acquisition-driven growth
   - Geographic and product segment growth breakdown

2. Growth Drivers:
   - Market expansion opportunities
   - New product/service development
   - Pricing power and volume growth potential

3. Investment in Future Growth:
   - R&D spending and innovation pipeline
   - Capital expenditures and capacity expansion
   - Strategic acquisitions and partnerships

4. Growth Sustainability:
   - Addressable market size and penetration rates
   - Competitive intensity and market share trends
   - Regulatory or technological factors affecting growth

5. Growth Projections:
   - Analyst consensus estimates
   - Management guidance
   - Realistic growth scenarios (base, bull, bear cases)

Provide a balanced assessment of the company's growth potential, supported by specific data points.

DATA:
{data}
"""

# Template for risk assessment
RISK_ASSESSMENT_TEMPLATE = """
You are a financial analyst tasked with conducting a risk assessment of {symbol} as an investment.
Based on the provided data, analyze:

1. Financial Risks:
   - Debt levels and maturity profile
   - Liquidity position and cash burn rate
   - Currency and interest rate exposure

2. Business and Operational Risks:
   - Customer concentration
   - Supply chain vulnerabilities
   - Operational dependencies and bottlenecks

3. Market Risks:
   - Cyclicality and economic sensitivity
   - Competitive threats and market share erosion
   - Pricing pressure and margin compression

4. Regulatory and Legal Risks:
   - Current and potential regulatory challenges
   - Litigation and legal proceedings
   - Compliance requirements and associated costs

5. Technological Risks:
   - Disruption potential
   - Technology obsolescence
   - Cybersecurity and data privacy concerns

6. ESG Risks:
   - Environmental impact and sustainability concerns
   - Social responsibility and labor practices
   - Governance structure and shareholder rights

Provide a comprehensive risk assessment with probability and potential impact estimates where possible.

DATA:
{data}
"""

# Template for summarizing multiple analyses
SUMMARY_TEMPLATE = """
You are a financial advisor tasked with synthesizing multiple analyses of {symbol} into a comprehensive investment recommendation.
Based on the provided analyses, create a well-structured investment thesis that includes:

1. Investment Summary:
   - Overall recommendation (Buy/Hold/Sell)
   - Key investment merits and concerns
   - Target price range or expected return

2. Business Overview:
   - Core business model and value proposition
   - Market position and competitive landscape

3. Financial Analysis:
   - Key financial metrics and trends
   - Balance sheet and cash flow highlights

4. Growth Outlook:
   - Growth drivers and opportunities
   - Realistic growth projections

5. Competitive Advantages:
   - Sustainable moat factors
   - Differentiation from competitors

6. Risk Factors:
   - Key risks to the investment thesis
   - Mitigating factors or hedges

7. Valuation:
   - Current valuation metrics
   - Fair value estimate and methodology
   - Potential catalysts

Provide a balanced perspective that acknowledges both bullish and bearish arguments, with a clear rationale for the final recommendation.

ANALYSES:
{analyses}
"""

# New functions to generate different prompt templates

def initial_analysis_prompt(data: dict, symbol: str = None) -> str:
    """
    Generate a prompt for initial financial analysis of a company.
    
    This function creates a prompt for the first analysis iteration, focusing on
    general financial performance and business overview.
    
    Args:
        data (dict): Financial data for the company to be analyzed
        symbol (str, optional): The stock symbol of the company. If None, will try to extract from data.
        
    Returns:
        str: Formatted prompt for initial analysis
    """
    if symbol is None and 'symbol' in data:
        symbol = data.get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the data for the prompt
    formatted_data = ""
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_data += f"\n## {key.replace('_', ' ').title()}\n"
            for sub_key, sub_value in value.items():
                formatted_data += f"{sub_key}: {sub_value}\n"
        elif isinstance(value, list):
            formatted_data += f"\n## {key.replace('_', ' ').title()}\n"
            for item in value:
                if isinstance(item, dict):
                    formatted_data += "\n"
                    for item_key, item_value in item.items():
                        formatted_data += f"{item_key}: {item_value}\n"
                else:
                    formatted_data += f"- {item}\n"
        else:
            formatted_data += f"{key}: {value}\n"
    
    return FINANCIAL_ANALYSIS_TEMPLATE.format(symbol=symbol, data=formatted_data)

def detailed_analysis_prompt(data: dict, focus: str, symbol: str = None) -> str:
    """
    Generate a prompt for detailed analysis with a specific focus.
    
    This function creates a prompt for subsequent analysis iterations, focusing on
    specific aspects like competitive analysis, growth prospects, or risk assessment.
    
    Args:
        data (dict): Financial data for the company to be analyzed
        focus (str): The focus area for analysis ('competitive', 'growth', 'risk')
        symbol (str, optional): The stock symbol of the company. If None, will try to extract from data.
        
    Returns:
        str: Formatted prompt for detailed analysis
    """
    if symbol is None and 'symbol' in data:
        symbol = data.get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the data for the prompt
    formatted_data = ""
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_data += f"\n## {key.replace('_', ' ').title()}\n"
            for sub_key, sub_value in value.items():
                formatted_data += f"{sub_key}: {sub_value}\n"
        elif isinstance(value, list):
            formatted_data += f"\n## {key.replace('_', ' ').title()}\n"
            for item in value:
                if isinstance(item, dict):
                    formatted_data += "\n"
                    for item_key, item_value in item.items():
                        formatted_data += f"{item_key}: {item_value}\n"
                else:
                    formatted_data += f"- {item}\n"
        else:
            formatted_data += f"{key}: {value}\n"
    
    # Select the appropriate template based on the focus
    if focus.lower() == 'competitive':
        template = COMPETITIVE_ANALYSIS_TEMPLATE
    elif focus.lower() == 'growth':
        template = GROWTH_ANALYSIS_TEMPLATE
    elif focus.lower() == 'risk':
        template = RISK_ASSESSMENT_TEMPLATE
    else:
        # Default to financial analysis if focus is not recognized
        template = FINANCIAL_ANALYSIS_TEMPLATE
    
    return template.format(symbol=symbol, data=formatted_data)

def planning_prompt(analyses: list, symbol: str = None) -> str:
    """
    Generate a prompt for planning the next steps in the analysis process.
    
    This function creates a prompt for the planning agent to determine whether
    to continue with further analysis or proceed to summarization.
    
    Args:
        analyses (list): List of previous analysis results
        symbol (str, optional): The stock symbol of the company
        
    Returns:
        str: Formatted prompt for planning
    """
    if symbol is None and analyses and 'symbol' in analyses[0]:
        symbol = analyses[0].get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the analyses for the prompt
    formatted_analyses = ""
    for i, analysis in enumerate(analyses):
        formatted_analyses += f"\n## Analysis {i+1}: {analysis.get('analysis_type', 'General')}\n"
        
        # Add key insights
        if 'insights' in analysis:
            formatted_analyses += "\nKey Insights:\n"
            formatted_analyses += analysis['insights']
        
        # Add key points if available
        if 'key_points' in analysis and analysis['key_points']:
            formatted_analyses += "\n\nKey Points:\n"
            for point in analysis['key_points']:
                formatted_analyses += f"- {point}\n"
        
        # Add sentiment and confidence
        if 'sentiment' in analysis:
            formatted_analyses += f"\nSentiment: {analysis.get('sentiment', 'Neutral')}\n"
        if 'confidence' in analysis:
            formatted_analyses += f"Confidence: {analysis.get('confidence', 'Medium')}\n"
        
        formatted_analyses += "\n" + "-"*50 + "\n"
    
    planning_template = """
You are a research coordinator tasked with planning the next steps for analyzing {symbol} as an investment opportunity.
Based on the analyses conducted so far, determine whether:

1. Further analysis is needed (and what specific focus area)
2. The research is sufficient to proceed to final summarization

Consider the following factors:
- Have all key aspects been covered? (financial performance, competitive position, growth prospects, risks)
- Are there any areas with low confidence or contradictory findings that need further investigation?
- Is there sufficient information to make an investment recommendation?

Provide your decision with clear reasoning and specify the next focus area if further analysis is needed.

ANALYSES CONDUCTED SO FAR:
{analyses}

Your response should be structured as:
1. Assessment of current research completeness (%)
2. Decision: Continue Research or Proceed to Summarization
3. If continuing, specify the next focus area and justify
4. If proceeding to summarization, explain why the research is sufficient
"""
    
    return planning_template.format(symbol=symbol, analyses=formatted_analyses)
