import numpy as np
from configs.policies import *

def update_prices(params, step, sL, s, _input):
    prices = s['token_prices']
    fluctuation = _input['fluctuation_p']
    prices *= np.array(fluctuation)
    return ('token_prices', prices)

def update_weights(params, step, sL, s, _input):
    votes = s['votes']
    weights = np.sum(votes ,0)/np.sum(votes)
    return ('weights', weights)

def update_past_volumes(params, step, sL, s, _input):
    balances = s['deposit_balances']
    weights = s['weights']
    volumes = s['past_trade_volumes']

    #execute normal trades
    i,o = _input['pair']
    A_i =  _input['n_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    volumes[i] += A_i
    volumes[o] += A_o
    
    #execute arbitrageurs trades
    i,o = _input['arbitrageur_pair']
    A_i =  _input['arbitrageurs_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    volumes[i] += A_i
    volumes[o] += A_o
    return ('past_trade_volumes', volumes)

def update_current_volumes(params, step, sL, s, _input):
    weights = s['weights']
    volumes = s['current_trade_volumes']
    fluctuation = _input['fluctuation_v']
    n_tokens = s['n_tokens']
    return ('current_trade_volumes', volumes)

def update_votes(params, step, sL, s, _input):
    votes = s['votes']
    delta = _input['delta_votes']
    m = _input['maker']
    votes[m,:] += delta
    return ('votes', votes)

def update_balances(params, step, sL, s, _input):
    balances = s['deposit_balances']
    weights = s['weights']
    
    #execute normal trades
    i,o = _input['pair']
    A_i =  _input['n_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    balances[i] += A_i
    balances[o] -= A_o
    
    #execute arbitrageurs trades
    i,o = _input['arbitrageur_pair']
    A_i =  _input['arbitrageurs_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    balances[i] += A_i
    balances[o] -= A_o
    return ('deposit_balances', balances)

def update_fees_gathered(params, step, sL, s, _input):
    balances = s['deposit_balances']
    weights = s['weights']
    fees_gathered = s['fees_gathered']
    token_prices = s['token_prices']
    trading_fee = s['trading_fee']
    votes = s['votes']
    
    #execute normal trades
    i,o = _input['pair']
    A_i =  _input['n_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    fees_i = (trading_fee/2)*A_i*token_prices[i]*(votes[:,i]/np.sum(votes[:,i]))
    fees_o = (trading_fee/2)*A_o*token_prices[o]*(votes[:,o]/np.sum(votes[:,o]))
    fees_gathered += fees_i
    fees_gathered += fees_o
    
    #execute arbitrageurs trades
    i,o = _input['arbitrageur_pair']
    A_i =  _input['arbitrageurs_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    fees_i = (trading_fee/2)*A_i*token_prices[i]*(votes[:,i]/np.sum(votes[:,i]))
    fees_o = (trading_fee/2)*A_o*token_prices[o]*(votes[:,o]/np.sum(votes[:,o]))
    fees_gathered += fees_i
    fees_gathered += fees_o
    return ('fees_gathered', fees_gathered)

def update_arbitrageurs_revenue(params, step, sL, s, _input):
    balances = s['deposit_balances']
    weights = s['weights']
    fees_gathered = s['fees_gathered']
    token_prices = s['token_prices']
    arb_ervenue = s['arbitrageurs_revenue']
    trading_fee = s['trading_fee']
    
    #execute arbitrageurs trades
    i,o = _input['arbitrageur_pair']
    A_i =  _input['arbitrageurs_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    A_o *= (1-trading_fee) #0.3% fee stays in the system
    arb_ervenue += A_o*token_prices[o] - A_i*token_prices[i]
    return ('arbitrageurs_revenue', arb_ervenue)


def update_slippage(params, step, sL, s, _input):
    balances = s['deposit_balances']
    weights = s['weights']
    token_prices = s['token_prices']
    trading_fee = s['trading_fee']
    i,o = _input['pair']
    A_i =  _input['n_tokens_in']
    A_o = balances[o]*(1 - (balances[i]/(balances[i]+A_i))**(weights[i]/weights[o]))
    A_o *= (1-trading_fee)
    slippage = s['accumulated_slippage']
    slippage += A_i*token_prices[i] - A_o*token_prices[o]
    return ('accumulated_slippage', slippage)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

partial_state_update_blocks = [
    { 
        'policies': { # The following policy functions will be evaluated and their returns will be passed to the state update functions
            'random_trader': traders,
            'arbitrageur': arbitrageur,
            'market_fluctuation': market_fluctuations,
            'revoting_maker': makers
        },
        'variables': { # The following state variables will be updated simultaneously
            'token_prices': update_prices,
            'past_trade_volumes': update_past_volumes,
            'current_trade_volumes' : update_current_volumes,
            'weights' : update_weights,
            'votes': update_votes,
            'deposit_balances': update_balances,
            'fees_gathered': update_fees_gathered,
            'arbitrageurs_revenue': update_arbitrageurs_revenue,
            'accumulated_slippage': update_slippage,
        }
    }
]