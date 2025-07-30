# TIBacktester
> A fork of Pybroker, to add more analysis features and focusing on backtesting.



> Why a new fork of pybroker, pybroker is a great backtest library,
> we forcked it to bring more flexibility and features to customize and meet our needs. 


## Algorithmic Trading in Python with Machine Learning

Are you looking to enhance your trading strategies with the power of Python and
machine learning? Then you need to check out **TIBacktester**! This Python framework
is designed for developing algorithmic trading strategies, with a focus on
strategies that use machine learning. With TIBacktester, you can easily create and
fine-tune trading rules, build powerful models, and gain valuable insights into
your strategy’s performance.



## Key Features

- A super-fast backtesting engine built in [NumPy](https://numpy.org/) and accelerated with [Numba](https://numba.pydata.org/).
- The ability to create and execute trading rules and models across multiple instruments with ease.
- Access to historical data from [Alpaca](https://alpaca.markets/), [Yahoo Finance](https://finance.yahoo.com/), [AKShare](https://github.com/akfamily/akshare), or from [your own data provider](https://www.TIBacktester.com/en/latest/notebooks/7.%20Creating%20a%20Custom%20Data%20Source.html).
- The option to train and backtest models using [Walkforward Analysis](https://www.TIBacktester.com/en/latest/notebooks/6.%20Training%20a%20Model.html#Walkforward-Analysis), which simulates how the strategy would perform during actual trading.
- More reliable trading metrics that use randomized [bootstrapping](https://en.wikipedia.org/wiki/Bootstrapping_(statistics)) to provide more accurate results.
- Caching of downloaded data, indicators, and models to speed up your development process.
- Parallelized computations that enable faster performance.

With TIBacktester, you'll have all the tools you need to create winning trading
strategies backed by data and machine learning. Start using TIBacktester today and
take your trading to the next level!


### Differences with PyBroker and Future Plans

- [x] uv instead of pip, to modernize the package management.
- [ ] more data sources
- [ ] multiple symbols in one strategy execution, to allow for pair trading
- [ ] more analysis toos
- [ ] consider using EagerPy to improve the performance

## Installation

TIBacktester supports Python 3.9+ on Windows, Mac, and Linux. You can install
TIBacktester using ``pip``:

```bash
   pip install -U tibacktester
```

Or you can clone the Git repository with:

```bash
   git clone https://github.com/edtechre/TIBacktester
```

## A Quick Example

Get a glimpse of what backtesting with TIBacktester looks like with these code
snippets:

**Rule-based Strategy**:

```python
   from tibacktester import Strategy, YFinance, highest

   def exec_fn(ctx):
      # Get the rolling 10 day high.
      high_10d = ctx.indicator('high_10d')
      # Buy on a new 10 day high.
      if not ctx.long_pos() and high_10d[-1] > high_10d[-2]:
         ctx.buy_shares = 100
         # Hold the position for 5 days.
         ctx.hold_bars = 5
         # Set a stop loss of 2%.
         ctx.stop_loss_pct = 2

   strategy = Strategy(YFinance(), start_date='1/1/2022', end_date='7/1/2022')
   strategy.add_execution(
      exec_fn, ['AAPL', 'MSFT'], indicators=highest('high_10d', 'close', period=10))
   # Run the backtest after 20 days have passed.
   result = strategy.backtest(warmup=20)
```

**Model-based Strategy**:

```python
   from tibacktester import Alpaca, Strategy, model

   def train_fn(train_data, test_data, ticker):
      # Train the model using indicators stored in train_data.
      ...
      return trained_model

   # Register the model and its training function with TIBacktester.
   my_model = model('my_model', train_fn, indicators=[...])

   def exec_fn(ctx):
      preds = ctx.preds('my_model')
      # Open a long position given my_model's latest prediction.
      if not ctx.long_pos() and preds[-1] > buy_threshold:
         ctx.buy_shares = 100
      # Close the long position given my_model's latest prediction.
      elif ctx.long_pos() and preds[-1] < sell_threshold:
         ctx.sell_all_shares()

   alpaca = Alpaca(api_key=..., api_secret=...)
   strategy = Strategy(alpaca, start_date='1/1/2022', end_date='7/1/2022')
   strategy.add_execution(exec_fn, ['AAPL', 'MSFT'], models=my_model)
   # Run Walkforward Analysis on 1 minute data using 5 windows with 50/50 train/test data.
   result = strategy.walkforward(timeframe='1m', windows=5, train_size=0.5)
```


