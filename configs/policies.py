import numpy as np
from configs.utils import *

def traders(params, step, sL, s):
    #It models normal traders, i.e. such that perform trades just for the sake of aquiring a different token.
    #They do not try to game the system.
    volumes = s['current_trade_volumes']
    token_prices = s['token_prices']
    #traders have average pacing in the system, one trade is executed every 20 timesteps
    if get_current_timestep(step, s)%5==0:
        #choose what pair to trade according to distribution given by current volumes
        i, o = np.random.choice(s['n_tokens'],2, p = volumes/np.sum(volumes), replace = False)
        #differences in volumes are taken into account when sampling pair, 
        #so the traded amounts are modelled as the same (may change later)
        n_tokens_in = 5*np.sum(volumes)*token_prices[i]
        return({'pair': (i,o), 'n_tokens_in': n_tokens_in})
    else: 
        return({'pair': (0,0), 'n_tokens_in': 0})

def arbitrageur(params, step, sL, s):
    #arbitrageurs are the fastest actors and always execute trade on the most profitable pair (if any profitable pair exists)
    balances = s['deposit_balances']
    weights = s['weights']
#     print('    1 arb:', weights[0])
    token_prices = s['token_prices']
    n_tokens = s['n_tokens']
    trading_fee = s['trading_fee']
    #calculate spot price of every token in the system. If ratio between spot prices of two tokens differs from actual rate
    #for this pair (i.e., on external markets) by more than a trading fee, then it is an arbitrage opportunity. 
    spot_prices = (balances)/(weights)
    ratios = spot_prices*token_prices
    if np.max(ratios)/np.min(ratios) > 1+trading_fee:
        i, o  = np.argmin(ratios), np.argmax(ratios)
        pair_spot_price = (spot_prices[i]/spot_prices[o])
        target_pair_spot_price = (token_prices[o]/token_prices[i])#*(1+trading_fee)
        tokens_in = balances[i]*((target_pair_spot_price/pair_spot_price)**(weights[o]/(weights[o]+weights[i]))-1)
#         print('    2 arb:', weights[0])
        return({'arbitrageur_pair': (i, o), 'arbitrageurs_tokens_in': tokens_in})
    else:
#         print('    2 arb:', weights[0])
        return({'arbitrageur_pair': (0,0), 'arbitrageurs_tokens_in': 0})

def makers(params, step, sL, s):
    #market makers can game their fees by changing the distribution of their votes. As its a competitive market,
    #these actions are also very fast.
    n_makers = s['n_makers']
    n_tokens = s['n_tokens']
    #randomly chosen market maker will be the first to adapt to the new volumes
    m = np.random.randint(n_makers)
    volumes = s['current_trade_volumes']
    prices = s['token_prices']
    votes = s['votes']
    
    volume_vote_ratios = volumes/np.sum(votes,0)
    target_ratio = np.sum(volumes)/np.sum(votes)
    
    delta_votes = np.zeros(n_tokens)
#     undervoted_tokens = volume_vote_ratios/np.mean(volume_vote_ratios)
    if s['revoting'] and np.max(volume_vote_ratios) > 1.01*target_ratio:
        released_votes = 0
        for i in range(n_tokens):
            if volume_vote_ratios[i] < target_ratio:
                delta = np.min([votes[m,i], np.sum(votes[:,i]) - np.mean(np.sum(votes,0)) * (volumes[i]/np.mean(volumes))    ])
                delta = np.max([delta,0])
                if delta<0:
                    print('   first delta:', delta, votes[m,i], np.sum(votes[:,i]), np.mean(np.sum(votes,0)))
                delta_votes[i] -= delta
                released_votes += delta
        for i in range(n_tokens):
            if volume_vote_ratios[i] > target_ratio:
                delta = np.min([released_votes, np.mean(np.sum(votes,0)) * (volumes[i]/np.mean(volumes)) - np.sum(votes[:,i]) ])
                delta = np.max([delta,0])
                if delta<0:
                    print('   second delta:', delta, released_votes, np.sum(votes[:,i]), np.mean(np.sum(votes,0)))
                delta_votes[i] += delta
                released_votes -= delta
    return({'delta_votes': delta_votes, 'maker': m})

def market_fluctuations(params, step, sL, s):
    #current traded volumes are changing due to market fluctuations
    n_tokens = s['n_tokens']
    if get_current_timestep(step, s)%20==0:
        fluctuation_v = np.ones(n_tokens) + (np.random.dirichlet(np.ones(n_tokens),size=1)[0,:]  - 1/n_tokens)/4
        fluctuation_p = np.ones(n_tokens) + (np.random.dirichlet(np.ones(n_tokens),size=1)[0,:]  - 1/n_tokens)/8
        return({'fluctuation_v': fluctuation_v, 'fluctuation_p': fluctuation_p})
    else:
        return({'fluctuation_v': np.ones(n_tokens), 'fluctuation_p': np.ones(n_tokens)})
