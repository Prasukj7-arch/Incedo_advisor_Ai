"""
Creates 5 mock financial research PDFs for the RAG Knowledge Base.
Run once: python create_research_docs.py
"""
from fpdf import FPDF
import os

os.makedirs("research_docs", exist_ok=True)

def create_pdf(filename, title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, content)
    pdf.output(f"research_docs/{filename}")
    print(f"Created: research_docs/{filename}")

# ── Report 1: Semiconductor Sector ───────────────────────────────────────────
create_pdf("semiconductor_outlook_2025.pdf", "Semiconductor Sector Outlook 2025", """
Goldman Sachs Research | Technology Sector | May 2025

EXECUTIVE SUMMARY
The semiconductor sector is poised for a strong recovery in 2025, driven primarily by
artificial intelligence chip demand. We maintain a BUY rating on the sector with a
12-month price target implying 18% upside from current levels.

KEY FINDINGS

AI Chip Demand Surge
- Data center GPU demand is expected to grow 45% YoY in 2025
- NVIDIA maintains dominant 80% market share in AI training chips
- AMD gaining ground with MI300X, capturing 12% of AI inference market
- Custom silicon (Google TPU, AWS Trainium) growing but limited to internal use

Memory Recovery
- DRAM prices recovering after 18-month downturn, up 23% QoQ in Q1 2025
- HBM (High Bandwidth Memory) for AI applications at premium pricing
- Samsung and SK Hynix benefiting from tight HBM supply

Inventory Correction Complete
- PC and smartphone inventory normalization complete as of Q4 2024
- Consumer electronics demand stabilizing at pre-pandemic levels
- Enterprise storage demand recovering with cloud capex expansion

RISKS
- Geopolitical risk: US-China chip export restrictions could impact TSMC revenue by 8-12%
- Cyclicality: Semiconductor stocks historically volatile with 40-60% drawdowns in downturns
- Competition: Intel foundry ambitions could disrupt TSMC's dominance by 2027

TOP PICKS
1. NVIDIA (NVDA) - BUY, Target $950 - AI chip dominance, data center growth
2. TSMC (TSM) - BUY, Target $180 - Foundry monopoly, pricing power
3. Broadcom (AVGO) - BUY, Target $1,400 - Custom AI silicon, networking chips
4. Micron (MU) - BUY, Target $130 - HBM beneficiary, DRAM recovery

VALUATION
Sector trades at 28x forward P/E vs 5-year average of 22x, justified by AI growth premium.
Fair value estimate implies 15-20% upside for quality names over 12 months.

CONCLUSION
We recommend overweighting semiconductors in technology portfolios. Focus on AI
infrastructure plays (NVIDIA, Broadcom) and memory recovery stories (Micron).
Avoid legacy industrial semiconductor exposure until capex cycle recovers in H2 2025.
""")

# ── Report 2: Banking Sector ──────────────────────────────────────────────────
create_pdf("banking_sector_report_2025.pdf", "Indian Banking Sector Report Q1 2025", """
Morgan Stanley Research | Financial Services | April 2025

EXECUTIVE SUMMARY
Indian banking sector demonstrates resilience with strong credit growth and improving
asset quality. Private sector banks outperforming PSU banks on return metrics.
We initiate coverage with an OVERWEIGHT stance on the sector.

SECTOR OVERVIEW

Credit Growth
- System credit growth at 14.2% YoY, above RBI's 12% projection
- Retail loans leading growth at 18% YoY (personal loans, home loans, auto loans)
- Corporate credit recovering with 11% growth as capex cycle resumes
- MSME lending growing at 22% YoY supported by government schemes

Asset Quality
- Gross NPA ratio declined to 3.2% from 4.1% a year ago
- Net NPA at 0.8%, near decade lows
- Provision coverage ratio at 76%, providing strong buffer
- SMA-2 (Special Mention Accounts) stable at 0.6% of advances

Profitability
- System ROA at 1.2%, highest in 15 years
- Net Interest Margins holding at 3.8% despite rate pressure
- Cost-to-income improving to 44% from 48% on operating leverage

TOP PICKS
1. HDFC Bank - OVERWEIGHT, Target Rs 1,950
   - Best-in-class liability franchise, merger integration on track
   - ROA target of 1.8% by FY27, credit cost normalization complete
2. ICICI Bank - OVERWEIGHT, Target Rs 1,400
   - Strong retail franchise, technology-led growth
   - ROE expansion to 18% expected by FY26
3. Kotak Mahindra Bank - EQUAL WEIGHT, Target Rs 1,850
   - Premium valuation limits upside, CEO transition risk
4. Axis Bank - OVERWEIGHT, Target Rs 1,250
   - Citibank integration synergies materializing, ROA improving

RISKS
- RBI rate cuts could compress NIMs by 15-20 bps
- Unsecured retail loan stress emerging in microfinance segment
- Regulatory risk: RBI tightening on personal loan growth

CONCLUSION
Maintain OVERWEIGHT. HDFC Bank and ICICI Bank are top picks offering combination
of growth, quality, and reasonable valuation. Avoid PSU banks given valuation premium
not justified by return differential.
""")

# ── Report 3: IT Sector ───────────────────────────────────────────────────────
create_pdf("it_sector_outlook_2025.pdf", "Indian IT Sector Outlook FY2026", """
JP Morgan Research | Technology Services | March 2025

EXECUTIVE SUMMARY
Indian IT sector faces near-term headwinds from BFSI spending slowdown and
discretionary IT cuts, but GenAI deal momentum provides medium-term catalyst.
We expect revenue growth acceleration to 8-10% in FY26 from 4-6% in FY25.

DEMAND ENVIRONMENT

GenAI Tailwinds
- GenAI deal TCV reached $4.2B in FY25, up 180% YoY
- Implementation projects moving from PoC to production deployment
- Accenture partnership model being replicated by Indian IT majors
- TCS GenAI platform (TCS WisdomNext) gaining enterprise traction

BFSI Vertical
- US banking IT budgets under pressure due to deposit margin compression
- European BFSI cautious on discretionary spending
- India BFSI strong with digital banking transformation initiatives
- Expected recovery in US BFSI spending by Q3 FY26

Geographic Performance
- North America: Cautious, 3-4% growth expected
- Europe: Headwinds from macro, 2-3% growth
- India domestic: Strong, 18-20% growth
- Rest of World: Middle East strong on Vision 2030 spending

COMPANY ANALYSIS
1. TCS - OVERWEIGHT, Target Rs 4,200
   - Market share gains in GenAI, strong deal pipeline
   - Revenue growth 7-9% FY26, margin stable at 24-25%
2. Infosys - OVERWEIGHT, Target Rs 1,850
   - Cobalt cloud platform differentiator, guidance upgrade likely
   - Revenue growth 8-10% FY26, operating margin 21-22%
3. HCL Technologies - OVERWEIGHT, Target Rs 1,950
   - Products business (HCL Software) underappreciated
   - Revenue growth 6-8% FY26, best margin profile
4. Wipro - EQUAL WEIGHT, Target Rs 580
   - CEO transition stabilizing, still in recovery mode
   - Revenue growth 4-6% FY26, margin improvement ongoing

RISKS
- USD/INR appreciation hurts revenue in rupee terms
- Visa restrictions could increase onsite delivery costs
- Client budget freezes if US enters recession

CONCLUSION
Accumulate IT on dips. TCS and Infosys are quality compounders for long-term portfolios.
Near-term volatility provides entry opportunity. Target 12-month returns of 15-20%.
""")

# ── Report 4: FMCG Sector ─────────────────────────────────────────────────────
create_pdf("fmcg_sector_report_2025.pdf", "FMCG Sector Analysis India 2025", """
UBS Research | Consumer Staples | February 2025

EXECUTIVE SUMMARY
Indian FMCG sector recovering from urban consumption slowdown with rural demand
acting as key growth driver. Volume growth recovery expected in H2 FY25.
We maintain NEUTRAL stance with selective stock picking recommended.

SECTOR DYNAMICS

Rural Recovery
- Rural FMCG growth at 8.2% vs urban 5.1%, gap widening
- Good monsoon FY24 supporting agri income and rural spending
- Government transfers and NREGA spending boosting disposable income
- 2-wheeler sales as proxy: rural up 14% vs urban up 7%

Premiumization Trend
- Premium products growing 2x faster than mass market
- Health and wellness category growing 22% YoY
- Direct-to-consumer brands gaining 3-4% market share
- Modern trade and e-commerce now 28% of FMCG sales

Input Cost Environment
- Palm oil prices stable, down 18% from peak
- Crude derivative packaging costs declining
- Gross margin expansion of 150-200 bps expected in FY26
- Companies reinvesting savings in A&P to defend market share

TOP PICKS
1. Hindustan Unilever (HUL) - BUY, Target Rs 2,800
   - Volume recovery play, rural exposure beneficial
   - Margin expansion on track, 23% EBITDA margin target FY26
2. ITC - BUY, Target Rs 520
   - Cigarette pricing power, FMCG scale benefits emerging
   - Hotels business value unlocking, 28x P/E attractive
3. Dabur - EQUAL WEIGHT, Target Rs 580
   - International business headwinds, domestic recovering
4. Marico - BUY, Target Rs 680
   - Parachute coconut oil pricing cycle turning positive
   - Vietnam business recovery adding to growth

RISKS
- Heat wave impact on summer product demand
- Competition from regional players with lower prices
- Raw material price reversal if El Nino impacts monsoon

CONCLUSION
FMCG sector offers defensive characteristics with moderate growth. Prefer companies
with strong rural exposure and premiumization capability. HUL and ITC are top picks.
""")

# ── Report 5: Macro Outlook ───────────────────────────────────────────────────
create_pdf("macro_outlook_india_2025.pdf", "India Macro Outlook 2025-2026", """
Deutsche Bank Research | Economics | May 2025

EXECUTIVE SUMMARY
India remains the fastest-growing major economy globally with GDP growth of 7.2% in
FY25. We maintain our FY26 GDP growth forecast at 6.8%, supported by infrastructure
investment, consumption recovery, and services export growth.

MACROECONOMIC INDICATORS

GDP Growth
- FY25 GDP growth: 7.2% (above consensus of 6.8%)
- FY26 forecast: 6.8% (domestic consumption recovery key driver)
- Manufacturing PMI at 58.4, highest in 15 years
- Services PMI at 61.2, led by IT and financial services

Inflation
- CPI inflation at 4.1%, within RBI target band of 2-6%
- Food inflation moderating to 3.8% after vegetable price normalization
- Core inflation at 3.4%, lowest since 2019
- RBI rate cuts of 50-75 bps expected in H2 FY26

Currency
- INR at 83.5/USD, managed depreciation of 2-3% expected
- CAD at 1.2% of GDP, comfortable financing from FPI and FDI inflows
- Forex reserves at $650B, 11 months of import cover

Fiscal Position
- Fiscal deficit at 5.1% of GDP, on consolidation path
- Government capex at Rs 11.1 lakh crore, highest ever
- Tax revenue buoyancy at 1.3x, GST collections at record Rs 1.87 lakh crore

INVESTMENT IMPLICATIONS

Equity Market Outlook
- Nifty 50 target: 26,500 (12-month), implying 12% upside
- Small and midcap valuations stretched, prefer largecaps
- FPI flows expected at $20-25B in FY26

Fixed Income
- 10-year G-Sec yield target: 6.50% by March 2026
- Duration play attractive as rate cuts materialize
- Corporate bonds offering 75-100 bps spread, selective opportunities

Sector Preferences
- OVERWEIGHT: Financials, Infrastructure, Consumer Discretionary
- EQUAL WEIGHT: IT, Healthcare, Energy
- UNDERWEIGHT: Metals, Telecom, Utilities

RISKS
- Global recession risk: 25% probability, would cut growth to 5.5%
- Oil price spike above $100/bbl would widen CAD and pressure INR
- El Nino impact on agriculture and rural consumption
- US Fed policy: Higher-for-longer would pressure capital flows

CONCLUSION
India structural growth story intact. Near-term volatility from global factors provides
accumulation opportunity. Maintain overweight on Indian equities vs EM peers.
Prefer quality largecaps with domestic consumption exposure.
""")

print("\nAll 5 research PDFs created in research_docs/ folder!")
print("Next step: Upload to S3")