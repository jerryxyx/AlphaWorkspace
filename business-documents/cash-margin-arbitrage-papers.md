# Cash Margin Arbitrage between Warrants and Listed Options in Hong Kong: Academic Papers and Reports

*Compiled on 2026-03-13 via Tavily search*

## Overview
This document summarizes academic papers, theses, reports, and discussions related to cash margin arbitrage strategies between warrants and listed options in Hong Kong. Focus areas include pairs trading, margin differentials, vega-based arbitrage, and toxic-flow strategies.

---

## 1. Academic Papers

### 1.1 Test the arbitrage possibilities in Hong Kong option market by using box spread strategy
- **Source**: https://library2.smu.ca/handle/01/25265
- **Abstract**: The paper tests for arbitrage opportunities in the Hong Kong index options market using put‑call parity and box spread strategies. Using 3658 pairs of data (1829 long hedge positions and 1829 short hedge positions), a T‑test indicates significant arbitrage opportunities, though they exist only with very small probabilities.
- **Relevance**: Directly examines arbitrage in Hong Kong index options; box spread is a classic risk‑free arbitrage strategy that can be adapted to warrant‑option pairs.

### 1.2 Flow Toxicity of High Frequency Trading and Its Impact on Price Volatility
- **Source**: https://strathprints.strath.ac.uk/69344/1/Kang_etal_JFM_2019_Flow_toxicity_of_high_frequency_trading_and_its_impact_on_price_volatility.pdf
- **Note**: This paper discusses flow toxicity and adverse selection in high‑frequency trading environments, which is relevant for understanding toxic‑flow strategies in warrant/option markets.
- **Relevance**: Provides theoretical background on how toxic order flow affects liquidity and pricing, which can be exploited in arbitrage between warrants and options.

### 1.3 Making Derivative Warrants Market in Hong Kong
- **Source**: https://www.mssanz.org.au/MODSIM07/papers/29_s1/MakingDerivative_s1_Chow_.pdf
- **Summary**: Examines the market‑making dynamics of derivative warrants in Hong Kong, highlighting institutional constraints that make warrants more appealing than options for retail investors.
- **Relevance**: Describes the structural differences between the warrant and option markets that can give rise to arbitrage opportunities, especially regarding liquidity and margin treatment.

---

## 2. Theses & Dissertations

### 2.1 Options and structured warrants on the Hong Kong exchange: pricing processes and credit risk
- **Source**: https://researchprofiles.canberra.edu.au/en/studentTheses/options-and-structured-warrants-on-the-hong-kong-exchange-pricing/
- **Abstract**: Compares pricing processes of Hang Seng Index Options (HSIO) and Hang Seng Index Warrants (HSIW). Finds that HSIO exhibit both continuous and weak jump components, while HSIW exhibit a purely jump component. Credit risk of warrant issuers is a significant factor in pricing differences.
- **Key Findings**:
  - Warrants and options are priced differently due to distinct underlying processes.
  - Credit risk of the issuer affects warrant pricing.
  - Jump components in warrants create opportunities for volatility‑based (vega) arbitrage.
- **Relevance**: Essential for understanding the fundamental pricing disparities that enable cash margin arbitrage between warrants and options.

### 2.2 The profitability of pairs trading strategies on Hong‑Kong stock market: distance, cointegration, and correlation methods
- **Source**: https://ideas.repec.org/p/war/wpaper/2022-02.html
- **Summary**: Compares three pairs‑trading methodologies (distance, cointegration, correlation) on the Hong Kong stock market using Hang Seng Index constituents.
- **Relevance**: Pairs trading techniques can be applied to warrant‑option pairs, especially when margin differentials create temporary mispricings.

---

## 3. Regulatory & Industry Reports

### 3.1 A Report on the Derivative Warrants Market in Hong Kong
- **Source**: https://apps.sfc.hk/edistributionWeb/gateway/EN/consultation/openFile?refNo=05CP10
- **Summary**: SFC review examining the impact of the derivative warrants market on overall market stability, including volatility and relative size compared to options.
- **Relevance**: Provides regulatory context on how warrant trading is overseen and potential constraints that affect arbitrage.

### 3.2 Introduction to Derivative Warrants – HKEX
- **Source**: https://www.hkex.com.hk/-/media/HKEX-Market/Products/Securities/Structured-Products/Product-Sheet/2025-Feb/HKEX_DW_infosheet_en.pdf
- **Summary**: Official HKEX guide explaining cash settlement, trading mechanics, and margin treatment of derivative warrants.
- **Relevance**: Clarifies the cash‑settlement feature of Hong Kong warrants, a critical element in cash margin arbitrage strategies.

### 3.3 Final draft – Hong Kong margin and other risk mitigation standards
- **Source**: https://assets.kpmg.com/content/dam/kpmg/cn/pdf/en/2017/01/hk-margin-and-other-risk-mitigation-standards.pdf
- **Summary**: Outlines margin requirements for non‑centrally cleared OTC derivatives, which may indirectly affect margin calculations for warrant‑option arbitrage positions.
- **Relevance**: Understanding margin rules is essential for assessing the cost and feasibility of leveraged arbitrage trades.

---

## 4. Forum Discussions & Practical Insights

### 4.1 Crazy margin requirement on warrant arbitrage – Elite Trader
- **Source**: https://www.elitetrader.com/et/threads/crazy-margin-requirement-on-warrant-arbitrage.349210/
- **Summary**: A trader describes how Interactive Brokers imposes additive margin (X+Y) for a long warrant + short call position, treating the legs as non‑hedging. The post argues that warrants should partially offset short calls, especially when the warrant is exercisable before the call expires.
- **Key Quote**: “Margin requirement to buy one warrant = X, margin requirement to short one call at a higher strike = Y, margin requirement to buy one warrant and short one call = X+Y, as if they don't hedge each other at all.”
- **Relevance**: Direct real‑world example of margin differentials creating barriers to warrant‑option arbitrage, highlighting the need for broker‑level margin optimization.

### 4.2 The difference between warrants and options – FUTU HK
- **Source**: https://support.futunn.com/en/topic213
- **Summary**: Explains that options trading volume in Hong Kong is lower than warrants, leading to wider spreads and higher trading costs for options.
- **Relevance**: Liquidity and cost differences are key drivers of arbitrage opportunities; wider option spreads can be exploited against more liquid warrants.

---

## 5. Additional Relevant Sources

### 5.1 Pairs trading across Mainland China and Hong Kong stock markets
- **Source**: https://eprints.whiterose.ac.uk/id/eprint/143981/3/Pairs+Trading+Across+Mainland+China+and+Hong+Kong+Stock+Markets.pdf
- **Summary**: Applies stochastic control to dynamic pairs trading between dual‑listed A‑shares and H‑shares.
- **Relevance**: Methodology can be adapted to warrant‑option pairs trading across different listing venues.

### 5.2 Vega‑based arbitrage resources
- **General resources on vega and volatility arbitrage** (not Hong‑Kong‑specific):
  - Understanding Vega in Options Trading (Strike.money)
  - Vega Deep Dive Guide (Menthorq)
  - Volatility Arbitrage Basics (Investopedia)
- **Relevance**: Vega‑based strategies exploit differences in implied volatility between warrants and options, which may arise from different jump components (as found in Thesis 2.1).

### 5.3 Margin requirements for option strategies – FUTU HK
- **Source**: https://www.futuhk.com/en/support/topic2_540
- **Summary**: Lists margin calculations for various option strategies.
- **Relevance**: Benchmark for comparing margin treatment of options vs. warrants.

---

## 6. Key Themes & Arbitrage Opportunities

### 6.1 Pricing Disparities
- Warrants exhibit jump‑component pricing, while options have continuous components (Thesis 2.1).
- Credit risk of warrant issuers adds a premium to warrant prices.
- Lower liquidity and wider spreads in options create pricing inefficiencies.

### 6.2 Margin Differential Arbitrage
- Brokers often treat warrant + option positions as unhedged, imposing additive margin (Forum 4.1).
- This creates a capital barrier, but also an opportunity for those who can secure favorable margin treatment.
- Regulatory margin standards (Report 3.3) may affect cross‑product margining.

### 6.3 Vega / Volatility Arbitrage
- Different implied volatility processes between warrants and options can be exploited via vega‑neutral strategies.
- Warrant prices may over‑ or under‑react to volatility shocks compared to options.

### 6.4 Toxic‑Flow Strategies
- Flow toxicity research (Paper 1.2) suggests that adverse selection can be predicted and used to front‑run order flow between warrant and option markets.
- High‑frequency trading in one market can create temporary mispricings in the other.

### 6.5 Pairs Trading Implementation
- Cointegration and distance methods (Paper 2.2) can identify warrant‑option pairs with mean‑reverting spreads.
- Execution must account for liquidity differences and margin costs.

---

## 7. Gaps & Future Research
- Few papers directly address **cash margin arbitrage** between warrants and listed options in Hong Kong.
- Most existing literature focuses on pricing differences or arbitrage within a single product class (e.g., options‑only or warrants‑only).
- Empirical studies on the profitability of warrant‑option pairs trading are lacking.
- Broker‑level margin policies and their impact on arbitrage viability remain under‑documented.

---

## 8. Conclusion
The Hong Kong market presents unique arbitrage opportunities due to structural differences between the actively traded warrant market and the less‑liquid listed options market. Key drivers are pricing disparities (jump vs. continuous components), margin treatment, liquidity gaps, and volatility differentials. Successful strategies require deep understanding of both product characteristics and broker‑specific margin rules.

*This document will be updated as new sources are discovered.*