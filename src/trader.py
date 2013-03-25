#!/usr/bin/python

"""trader module, containing the main logic"""


def market_simulator(market_data):
    """Parses a market csv file into orders"""
    raise NotImplementedError


def run_trial(market_data, signal_generator,
              engine, strategy_evaluator):
    """Run the experiment with the given market data"""
    trades = []
    for order in market_simulator(market_data):
        trades.extend(engine(order))
        for algorithmic_order in signal_generator(order):
            trades.extend(engine(algorithmic_order))
    strategy_evaluator(trades)

if __name__ == '__main__':
    import doctest
    doctest.testmod()