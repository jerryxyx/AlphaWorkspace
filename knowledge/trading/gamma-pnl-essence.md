# Gamma PnL Essence – Understanding the Volatility Premium

**Source:** [期权里Gamma PnL的本质](https://zhuanlan.zhihu.com/p/358768269) (Charlie, 香港中文大学 金融学硕士)  
**Published:** 2023‑03‑03 · Shanghai  
**Status:** Archived in 掘金之心公众号内容 · 80赞同

---

## Abstract

> “The reason for gamma PnL is the convexity of option price (second derivative of a non‑delta‑1 financial product).  
> The nature of gamma PnL is the market’s expected volatility premium.”

Gamma PnL is the profit/loss that remains after delta‑hedging an option position. It arises because option prices are **non‑linear** in the underlying – the **convexity** (gamma) creates an extra term in the Taylor expansion.  
The article argues that gamma PnL is fundamentally a bet on the **volatility premium** – the difference between implied volatility (what the market expects) and realised volatility (what actually happens).

---

## Key Concepts

### 1. Gamma–Theta Relationship
- **Gamma** = second derivative of option price w.r.t. spot; measures how fast delta changes.
- **Theta** = time decay; gamma and theta move in opposite directions as time passes.
- In a single option, gamma and vega go the same direction (long gamma → long vega).

### 2. Calendar‑Spread Greeks
By combining near‑ and far‑dated options, you can **decouple gamma and vega**:
- **Short near‑dated / long far‑dated** (debit calendar spread) → **positive gamma, negative vega**.
- **Long near‑dated / short far‑dated** (credit calendar spread) → **negative gamma, positive vega**.

> *Example:* ATM call calendar spread (short 1‑month, long 3‑month) – as expiry approaches, the short leg’s gamma rises faster (more negative gamma), while its vega falls faster (more positive vega).

### 3. Volatility Premium & Risk Aversion
- **Risk‑averse investors** demand a volatility premium → implied volatility > realised volatility.
- **Risk‑seeking investors** accept lower volatility premium → implied volatility < realised volatility.
- Most equity markets (especially Asian retail‑driven markets) are **risk‑seeking** → implied volatility tends to be **lower** than realised volatility.

### 4. Vanna (∂Δ/∂σ) – The Link Between IV and Spot
- **Positive vanna:** IV rises with spot (trending bull/bear market, risk‑seeking).  
  → Implied volatility > realised volatility.  
  → **Trade:** long gamma, short vega (credit calendar spread).
- **Negative vanna:** IV falls with spot (mean‑reverting market, risk‑averse).  
  → Implied volatility < realised volatility.  
  → **Trade:** short gamma, long vega (debit calendar spread).

> Negative vanna is more common in S&P 500 index options – shorting vega when IV is high wins ~80% of the time.

---

## Trading Strategy: Calendar Spread with 72% Annual ROE

### Setup
- **Instrument:** OTM call calendar spread (short near‑dated, long far‑dated).
- **Delta‑neutral** after hedging.
- **Exposure:** net option buying, negative vega, positive gamma.

### Return Profile
- **Margin‑based annualised ROE ≈ 72%** (for a credit‑spread variant).
- Edge comes from exploiting the **volatility premium** and **vanna sign**.

### Why It Works
1. Market is usually risk‑seeking → implied volatility undervalues realised volatility.
2. Negative vanna environment → short vega + long gamma benefits from IV drop and spot convexity.
3. Calendar spread isolates the gamma–vega mismatch.

---

## Case Studies

### AAPL (Nov 2019 – Aug 2020)
- Normally, long IV at a **trend‑tipping point** (where price acceleration stops) captures risk‑aversion shift.
- However, IV often failed to break above realised volatility – many false bottoms.
- On 2020‑07‑31, AAPL rose 11% in a bull trend, but **IV had been dropping** beforehand → market became less risk‑seeking, indicating the move was earnings‑driven (event risk) not sentiment‑driven.

### GME (Meme‑Stock Regime)
- **Yellow‑shaded periods** = market actively seeking risk → wide vol premium.
- The wider the gap between IV and realised vol, the more **herding** and **less efficient** price discovery.
- Eventually prices converge → edge in **shorting IV** when premium is excessive.

---

## Practical Takeaways

| Market Regime | Vanna Sign | IV vs. Realised | Gamma‑Vega Position |
|---------------|------------|-----------------|---------------------|
| Trending (risk‑seeking) | Positive | IV > Realised | Long gamma, short vega |
| Mean‑reverting (risk‑averse) | Negative | IV < Realised | Short gamma, long vega |

### Strategy Selection
- **Credit calendar spread** (short near, long far) when IV is high and vanna positive.
- **Debit calendar spread** (long near, short far) when IV is low and vanna negative.
- **Risk‑reversal** (short put, long call) can also exploit vanna/skew during market reversals.

### Human‑Nature Edge
- **Buffett‑style value investing** and **betting‑against‑beta (BAB)** outperform because humans are inherently **risk‑averse**.
- No one pays an infinite price for a game with infinite payoff (St. Petersburg Paradox) – after winning 100 poker hands straight, motivation to gamble decreases.

> “What ultimately makes long gamma a good strategy is exploiting the sure human nature of risk aversity and behavioral finance.”

---

## References & Further Reading
- **Calendar‑Spread Greeks** – Black‑Scholes PDE, gamma‑theta‑vega decomposition.
- **Volatility Premium** – Risk‑aversion utility curves, certainty‑equivalent volatility.
- **Vanna & Skew** – Relationship between spot moves and implied‑volatility surface.
- **St. Petersburg Paradox** – Behavioral foundation of risk‑premium pricing.

---

*Document generated from Zhihu article “期权里Gamma PnL的本质” (2023‑03‑03).  
Last updated: 2026‑03‑27*