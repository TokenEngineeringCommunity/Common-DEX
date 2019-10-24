import numpy as np

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

#amount of different tradable tokens and market makers in the system
n_tokens = 8
n_makers = 10

initial_token_prices = np.random.randint(1,1000,n_tokens)/10

#vector of CMN token ownership (1000 are minted and distributed among market makers with Dirchlet distribution)
CMN_ownership = 1000*np.random.dirichlet(np.ones(n_makers),size=1)

#initiate market makers votes for tokens

#trading volumes of tokens (not token pairs!). Expressed in values, not number of traded tokens!
initial_current_trade_volumes = np.random.dirichlet(np.ones(n_tokens))

#initial token weights (i.e. 'target deposit ratios'), calculated based on initial votes
#when no revoting happens, the system behaves as theere would be no voting at all, 
#just the hardcoded weights (as in Bancor or Balancer)
initial_weights = initial_current_trade_volumes.copy()
initial_votes = np.ones((n_makers, n_tokens))*initial_weights.reshape(1,n_tokens)
initial_votes /=  CMN_ownership.reshape(n_makers,1)

#initial deposit balances, expressed in number of tokens, not their value. #Note that token weights (target deposit 
#ratios) are referring to cumulative value of a given deposit, so normalization is needed.
initial_deposit_balances = 10000*np.random.randint(100,1000)*initial_weights/initial_token_prices

initial_conditions = {
    #initial deposit of each coin is proportional to its trading volume
    'revoting': True,
    'n_tokens': n_tokens,
    'n_makers': n_makers,
    'token_prices': initial_token_prices,
    'CMN_ownership': CMN_ownership,
    'past_trade_volumes': np.zeros(n_tokens), #will be used by market maker policies
    'current_trade_volumes': initial_current_trade_volumes,
    'weights': initial_weights,
    'votes': initial_votes,
    'deposit_balances': initial_deposit_balances,
    'fees_gathered': np.zeros(n_makers), #cumulative fees gathered by each market maker
    'arbitrageurs_revenue': 0, #cumulative revenue of all arbitrageurs
    'accumulated_slippage': 0, #total slippage cost of all normal traders (i.e., excluding arbitrageurs)
    'trading_fee' : 0.003
}