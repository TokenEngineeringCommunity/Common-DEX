*For the glossary of terms, see the end of the document*

# Inspiration/Problem

In the classical market maker models (such as a *constant product model*,  as used in Uniswap), the *slippage* for the trade A->B is proportional to the amount of A and B assets that exchange has reserved for this trading pair. 
Unfortunately, current DEX designs are utilizing reserve assets in a suboptimal way:
- [Uniswap](uniswap.io) has ETH as a central token, so every trade between tokens A and B needs to be split into A->ETH and ETH->B trades, and naturally half of the whole reserve needs to be kept as ETH. Even worse, Uniswaps ETH reserve is fractioned into parts corresponding to each other traded token, so each trading pair can use only a small fraction of the total ETH reserve. 
- [Bancor](bancor.network) uses a concept of a *target reserve ratio* for each token, what provides incentive for *arbitrageurs* to keep each token reserves close to the target values. Unfortunatelly, it lacks a mechanism of balancing these ratios, so they need to be set up manually and do not necessarily correspond to the actual volume on each of the assets (what in turn causes suboptimal slippage for traders). 
- [Balancer](balancer.finance), contrary to the name, also does not have a rebalancing mechanism. Instead, it nicely merges the Bancor idea of *target reserve ratios* for each token (which are called *weights* within the Balancer model) with a generalized *constant product model* of Uniswap. In the current version the *target reserve ratios/weights* are assumed to be constant. 

# What it does/Solution

Common is a DEX model that automatically balances reserve ratios in order to minimize the average slippage over all trades. 
The balancing is based purely on incentive mechanisms, hence does not rely on external price or volume oracles.
The proposed balancing mechanism is independent from price equations, so it could be used with any market maker model.
In scope of this project, I'm using prices as in the generalized constant product model.


Variables in the model:

$W_i$ - *weight* (as in Uniswap nomenclature), or *target reserve ratios*(as in Bancor nomenclature) of a token $i$,

$B_i$ - *balance* of token $i$ in the system, i.e., amount of $i$ in the traded reserves,

$V = \prod B_i^{W_i}$ - value function, which system keeps constant during the trades (but it changes with market makers' deposits and withdrawals)

$CMN_{issued} $ - amount of issued CMN tokens ($P_{issued}$ in the Balancer whitepaper)

$\mathcal{M}$ - set of market makers

$\mathcal{T}$ - set of supported tokens


$~$


The Common DEX is operating under the following premises (the equations are based on generalized contant product model as derived and proven in [Balancer whitepaper](https://balancer.finance/whitepaper.html)):
- Everyone can become a market maker by deposititing any or all of the supported tokens. In exchange, internal Common tokens (CMN) are minted in an amount proportional to the size of the deposit ([case of depositing one token](https://balancer.finance/whitepaper.html#single-asset-deposit), [case of depositing all supported tokens in proporions as currently in the deposit](https://balancer.finance/whitepaper.html#all-asset-depositwithdrawal)).
- Every market maker (i.e., every holder of CMN tokens) has a right to vote for the *target reserve ratios* of the supported tokens. Market makers voting power equals the amount of CMN possesed, and votes can be arbitrarily distributed among supported tokens. We denote the voting power that market maker $m$ decides to allocate on token $i$ as $\mathrm{A}_{m,i}$. The resulting *target reserve ratio* equals 

$$W_i = \frac{\Sigma_{m\in \mathcal{M}} \mathrm{A}_{m,i}}{\Sigma_{m\in \mathcal{M}, j\in \mathcal{T}} \mathrm{A}_{m,j}} = \frac{\Sigma_{m\in \mathcal{M}} \mathrm{A}_{m,i}}{CMN_{issued}}$$.
- Any pair of supported tokens is tradable for anyone with [rate](https://balancer.finance/whitepaper.html#out-given-in) given by CPM
- Each trade is subject to a fee proportional to the traded amount (say 0.3% of the trade, as in Uniswap). The fee $f$ of a traded pair of tokens $i,j$ is distributed among market makers proportionally to the votes given on $i$ and $j$, so the fee awarded to the market maker $m$ equals 
$$f_m = \frac{f}{2}\cdot \Big(\frac{A_{m,i}}{\Sigma_{n\in \mathcal{M}} A_{n,i}}+\frac{A_{m,j}}{\Sigma_{n\in \mathcal{M}} A_{n,j}}  \Big)$$

$~$

Slightly informally (i.e., without equations) the minimalization of average slippage happens through the following balancing feedback loop:

1. Fees from each trade are distributed only among market makers voting on traded tokens (proportional to votes). If some token X has higher fees/votes ratio then others, market makers are incentivized to allocate more votes for it to maximize their returns from fees.

2. Adding votes for X increases its *target reserve ratio*.

3. Higher *target reserve ratio* causes the price of X to increase in each pair (i.e., before the system rebalances the reserves).

4. Incentivized by preferential rates, arbitrageurs sell more X to the system (i.e., they execute (X->*anything else*) trades).

5. After more X tokens are entered to the system, slippage for pairs containing X decreases.

$~$

Now more formally, we can prove the following:

###### Theorem 1. 
Described mechanism converges to the situation in which the weight of each token is proportional to its traded volume. 

$~$

*Proof*:



Based on the *target reserve ratio* equation we have:
$$W_i = \frac{\Sigma_{m\in \mathcal{M}} \mathrm{A}_{m,i}}{CMN_{issued}}$$ 

$$ W_i\cdot CMN_{issued} = \Sigma_{m\in \mathcal{M}}\mathrm{A}_{m,i}\ \ \ \ \ \ \ \ (1)$$ 

The total fee earned by market maker $m$ in a unit of time equals (where $*$ follows from $(1)$):

$$ F_m = \Sigma_{i, j\in\mathcal{T}} \Big(\frac{\mathrm{volume}(i,j)}{2}\cdot\Big( \frac{A_{m,i}}{\Sigma_{n\in \mathcal{M}} A_{n,i}}+\frac{A_{m,j}}{\Sigma_{n\in \mathcal{M}} A_{n,j}}\Big)  \Big) 
= \Sigma_{i\in\mathcal{T}} \Big(\mathrm{volume}(i)\cdot\Big( \frac{A_{m,i}}{\Sigma_{n\in \mathcal{M}} A_{n,i}}\Big)  \Big) $$


$$\stackrel{*}{=} \Sigma_{i\in\mathcal{T}} \Big( \frac{\mathrm{volume}(i)\cdot A_{m,i}}{ W_i\cdot CMN_{issued}  }\Big) 
= CMN_{issued}\cdot\Sigma_{i\in\mathcal{T}} \Big(  A_{m,i}\cdot\frac{\mathrm{volume}(i)}{ W_i  }\Big) $$

Assume now that there is a token $i$ for which the ratio $\frac{\mathrm{volume}(i)}{ W_i  }$ is higher than for the other tokens. Then, for every market maker it is profitable to assign more votes to that token, and hence increase the fee earned. Q.E.D


# How I built it

The generalized constant product model is based on Balancer, and  the balancing loop is my original idea.


# Challenges I ran into

1. It occured to be quite hard to formalize a mechanism for listing new tokens within such a model
2. As pointed out by Billy Rennekamp, DEX based on such mechanism itself would be susceptible to putting unreasonably high fraction of its reserves in highly traded tokens with very unstable price (AKA *shitcoins*), hence putting at risk market makers' capital. Due to this limitation, without further work the design should be rather used for a federated list of traded tokens. The issue can be partially alleviated by replacing logarithm in the price equations with a function with a horizontal asymptote (ex. $\frac{1}{1-f(x)}$ for any $f$ descending to $0$), so that even unbounded influx of a single type of token can't allow to buy the whole of the system reserves. Other proposed heuristics included shutting off the listed token after it reaches some 'danger threshold'.
3. Relation between balances $B_i$ and $B_j$ and the slippage on the $i,j$ trading pair is not trivial, and the concept of 'average slippage' is somewhat loosely defined (what is the average size of the trade? What is the distribution of the trade sizes?). It remains an open problem to me whether the equilibrium in which balances directly proportional to the traded volumes is the best possible in terms of slippage minimization.

# Accomplishments that I'm proud of
- the balancing feedback loop is surprisingly well formalized considering the time constraints
- the specification chart (AKA 'differential specification') is a piece of art,
- I've proven a theorem on a hackathon!


# What I learned
- how to formalize incentive mechanisms with [differential specification](https://community.cadcad.org/t/differential-specification-syntax-key/31),
- what is cadCAD and how to use it,
- that constant product model easily generalizes for multiple tokens with different weights, and that someone actually already did the hard part of performing all the price calculations (thanks Michael Zargham for showing me Balancer),
- that [volatility risk](https://en.wikipedia.org/wiki/Volatility_risk) should be taken into account when designing DEXes. 

# What's next for Common
1. To alleviate the problem in challenge nr 2., another mechanism should to be put in place, which would hold voters for a given token X accountable for its excessive drops in price.

2. The mechanism of listing new tokens should be formalized. **Important note:** without resolving issue 1., allowing for listing new tokens by users or market makers could lead to various exploits based on listing different shady assets (which are, for example, hacked in a way giving someone access to unlimited amounts of tokens).

3. Of course, it needs to be implemented, preferably using some interoperability stack to allow for decentralized trading of non-ERC-20 tokens (ex., Bitcoin...). Currently it seems that such interoperability is possible either via deploying DEX on Ethereum and trustless wrapping of non-ERC-20 tokens (see ex., Keep [tBTC concept](http://docs.keep.network/tbtc/index.pdf), the same would need to be done for every other problematic token...), or by deploying on a platform with built-in decentralized bridges (ex., Cosmos hubs and zones or Polkadot bridge chains). 

### Glossary of terms:

**DEX** - An exchange which operates in a decentralized way, i.e., without a central authority. 

**slippage** - refers to the difference between the expected price of a trade and the price at which the trade is executed. Slippage can occur at any time but is most prevalent during periods of higher volatility when market orders are used. It can also occur when a large order is executed but there isn't enough volume at the chosen price to maintain the current bid/ask spread. ([investopedia](https://www.investopedia.com/terms/s/slippage.asp)). *In the scope of this document, I'm referring particularly to the slippage occurring due to the large trades on pairs with insufficient liquidity*

**arbitrageur** - a type of investor who attempts to profit from market inefficiencies. An arbitrageur would, for example, seek out price discrepancies between stocks listed on more than one exchange by buying the undervalued shares on one exchange while short selling the same number of overvalued shares on another exchange, thus capturing risk-free profits as the prices on the two exchanges converge.
([investopedia](https://www.investopedia.com/terms/a/arbitrageur.asp))

**market maker** - a company or an individual that both sells to and also buys from its clients and is compensated by means of price differentials for the service of providing liquidity, reducing transaction costs and facilitating trade.

**constant product model** - a model of automated market maker for a tradable pair of tokens in which system keeps the product $X\cdot Y$ constant, where $X$ and $Y$ are the amounts of the tokens in systems deposit/reserve. ([basic model](https://github.com/runtimeverification/verified-smart-contracts/blob/uniswap/uniswap/x-y-k.pdf), [model generalized for many tokens with weights](https://balancer.finance/whitepaper.html))
