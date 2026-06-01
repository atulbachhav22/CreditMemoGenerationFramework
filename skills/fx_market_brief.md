# Skill Name: FX Market Brief

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Fetches live USD exchange-rate data via MCP and produces a concise FX market brief relevant to cross-border trade-finance decisions.
- Tags: fx, currency, trade-finance, mcp-demo

## Context
This skill demonstrates MCP integration by using the mcp-server-fetch MCP server to pull
live exchange-rate data from the public Frankfurter API (no auth required).

The output is a compact FX market brief that a credit analyst can attach to a cross-border
credit memo to quantify currency risk.

## MCP Context

### MCP: fx_today
- Server: python -m mcp_server_fetch
- Tool: fetch
- Arguments: {"url": "https://api.frankfurter.app/latest?from=USD", "max_length": 3000}
- Description: Today's USD exchange rates against major currencies

### MCP: fx_year_ago
- Server: python -m mcp_server_fetch
- Tool: fetch
- Arguments: {"url": "https://api.frankfurter.app/2025-05-30?from=USD", "max_length": 3000}
- Description: USD exchange rates one year prior for year-over-year comparison

## Steps

### Step 1: Parse and Summarise Current Rates

**Instruction:**
The fx_today context contains JSON from the Frankfurter API with today's USD exchange rates.

Extract the following key pairs from the rates object and present them in a clean markdown table:
EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR

Include the date field from the API response as the Rate Date above the table.

**Expected Output:**
A markdown table of the 8 currency pairs with Rate Date shown above the table.

**Verification:**
- Table must contain all 8 currency codes: EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR
- Rate Date must be present and in YYYY-MM-DD format
- All rate values must be positive numbers

---

### Step 2: Year-over-Year FX Movement Analysis

**Instruction:**
You have two data sets:
- Today's rates from Step 1 (also in fx_today context)
- Rates from approximately one year ago in the fx_year_ago context

For each of the 8 currencies (EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR):
1. Calculate the percentage change: ((today - prior) / prior) * 100
2. Classify the movement: STRENGTHENED (USD gained >2%), STABLE (within 2%), WEAKENED (USD lost >2%)
3. Assign a trade-finance implication based on movement direction

Output a JSON object with a fx_yoy_analysis array.

**Expected Output:**
JSON with fx_yoy_analysis array containing code, today, year_ago, pct_change, movement, trade_implication for each currency.

**Verification:**
- All 8 currencies must be present
- pct_change must be a number
- movement must be STRENGTHENED, STABLE, or WEAKENED
- trade_implication must be a non-empty string

---

### Step 3: Generate FX Market Brief

**Instruction:**
Using the rate table from Step 1 and the YoY analysis from Step 2, write a concise FX Market Brief
suitable for attaching to a trade-finance credit memo.

Include:
1. Executive Summary (2-3 sentences): overall USD strength/weakness narrative
2. Key Movements Table: currencies classified STRENGTHENED or WEAKENED only
3. Trade Finance Risk Assessment: rate LOW/MODERATE/HIGH for import cost risk, export competitiveness risk, FX hedging urgency
4. Analyst Recommendation (1-2 sentences): whether to apply an FX risk buffer in credit terms

**Expected Output:**
A professional markdown report with all four sections.

**Verification:**
- Executive Summary must be present and at least 2 sentences
- Key Movements Table must be present
- All three risk dimensions must be rated LOW, MODERATE, or HIGH
- Analyst Recommendation must be present

## Final Output Format
A markdown FX Market Brief with executive summary, key movements, risk assessment, and recommendation.

## Success Criteria
1. Live rate data successfully fetched via MCP from Frankfurter API
2. YoY percentage changes calculated for all 8 currencies
3. Risk assessment is consistent with the movement data
4. Brief is concise enough to attach to a credit memo
