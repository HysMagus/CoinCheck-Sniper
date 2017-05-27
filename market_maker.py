import Settings
from api import *
from coincheck import order,market

order_api = order.Order(access_key=Settings.access_token, secret_key=Settings.access_key)
#order_api.create(rate=1, amount=0.01, order_type='buy', pair='btc_jpy')

bid_id = ''
ask_id = ''
def loop():
  global bid_id, ask_id
  start_time = time.time()
  
  if bid_id != '':
    order_api.cancel(bid_id)
  if ask_id != '':
    order_api.cancel(ask_id)

  order_book = coincheckapi.get_orderbook(count=5)
  best_bid = int(float(order_book['bids'][0][0]))
  best_ask = int(float(order_book['asks'][0][0]))
  algorithim_best_bid = best_bid + Settings.increment
  algorithim_best_ask = best_ask - Settings.increment
  while algorithim_best_ask - algorithim_best_bid < Settings.minimum_yen_spread:
    algorithim_best_bid -= Settings.increment
    algorithim_best_ask += Settings.increment

  position_data = coincheckapi.accounts_balance()
  net_holdings = float(position_data['btc']) + float(position_data['btc_reserved'])
  position = round(net_holdings - Settings.bitcoin, 3)
  non_bitcoin_balance = float(position_data['jpy']) + float(position_data['jpy_reserved']) + (position * best_bid)
  if position > 0:
    buy_amount = Settings.order_size
    sell_amount = round(Settings.order_size + abs(position), 2)
  elif position < 0:
    buy_amount = round(Settings.order_size + abs(position), 2)
    sell_amount = Settings.order_size
  else:
    buy_amount = Settings.order_size
    sell_amount = Settings.order_size
  if position >= Settings.max_position:
    buy_amount = 0
  if position <= -Settings.max_position:
    sell_amount = 0

  buy_order = order_api.create(rate=algorithim_best_bid, amount=buy_amount, order_type='buy', pair='btc_jpy')
  sell_order = order_api.create(rate=algorithim_best_ask, amount=sell_amount, order_type='sell', pair='btc_jpy')
  
  try:
    bid_id = str(buy_order['id'])
  except:
    pass
  
  try:
    ask_id = str(sell_order['id'])
  except:
    pass


  print("{}@{} \t \t \t {}@{} \t \t \t {} \t \t \t {}".format(buy_amount, algorithim_best_bid, sell_amount, algorithim_best_ask, position, non_bitcoin_balance))
  latency = int((time.time() - start_time) * 1000)
  print("{} milliseconds".format(latency))

#print(order_api.create(rate=1000, amount=0.005, order_type='buy', pair='btc_jpy')['id'])
#raise SystemExit
while True:
  loop()