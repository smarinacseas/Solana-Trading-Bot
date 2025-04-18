import asyncio
from termcolor import cprint
from backend.app.data_import.binance.base_stream import BaseBinanceStream

class StandardBinanceStream(BaseBinanceStream):
    def __init__(self, symbol, trades_file, min_display, bold_amt, color_amt, websocket_url):
        super().__init__(symbol, trades_file, websocket_url, channel='@aggTrade')
        self.min_display = min_display
        self.bold_amt = bold_amt
        self.color_amt = color_amt

    async def handle_connection(self, ws):
        while True:
            try:
                msg = await ws.recv()
                # Use the base class helper to parse the message.
                data = self.parse_trade_message(msg)
                if not data:
                    continue

                # Format the event time using the base class helper.
                readable_time = self.format_time(data.get('event_time', 0))
                asset_symbol = data.get('symbol', 'N/A')
                agg_trade_id = data.get('agg_trade_id', 0)
                price = data.get('price', 0)
                quantity = data.get('quantity', 0)
                first_trade_id = data.get('first_trade_id', 0)
                trade_time = data.get('trade_time', 'N/A')
                is_buyer_maker = data.get('is_buyer_maker', False)

                usd_size = price * quantity
                display_symbol = self.get_display_symbol()

                if usd_size >= self.min_display:
                    trade_type = 'SELL' if is_buyer_maker else 'BUY'
                    attrs = []
                    if usd_size >= self.bold_amt:
                        attrs.append("bold")
                    if usd_size >= self.color_amt:
                        color = "magenta" if trade_type == "SELL" else "blue"
                    else:
                        color = "red" if trade_type == "SELL" else "green"

                    price_str = f"@${price:,.2f}"
                    total_str = f"({usd_size:,.0f})"
                    output = (f"{readable_time:<10} "
                              f"{display_symbol:<4} "
                              f"{trade_type:<5} "
                              f"{price_str:>12} "
                              f"{total_str:>10}")
                    cprint(output, "white", "on_" + color, attrs=attrs)

                    output_path = self.get_output_file_path()
                    with open(output_path, 'a') as f:
                        f.write(f'{readable_time}, {asset_symbol.upper()}, {agg_trade_id}, '
                                f'{price}, {first_trade_id}, {trade_time}, {is_buyer_maker}\n')
            except Exception as e:
                print(f'Error: {e}')
                await asyncio.sleep(1) 