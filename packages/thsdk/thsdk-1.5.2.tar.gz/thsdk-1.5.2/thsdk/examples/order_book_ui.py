# 在命令行中显示UI

import asyncio
import time
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from colorama import init
from thsdk import THS

# 初始化colorama（确保Windows命令行颜色兼容）
init(autoreset=True)

# 初始化rich console
console = Console()

# 设置THS实例
ths = THS()


def get_stock_quotes_ths(stocks):
    """
    使用THS获取多只股票的实时盘口数据
    stocks: 股票代码列表，例如 ['USZA000001', 'USHA600519']
    """
    all_data = []
    for stock in stocks:
        try:
            # 获取实时盘口数据
            response = ths.depth(stock)
            time.sleep(0.1)  # 避免API请求过频
            df = pd.DataFrame(response.get_result())
            # 检查THS API返回的字段，尝试从常见字段获取名称
            stock_name = df.get('名称', df.get('name', ['']))[0]
            current_price = float(df['买1价'].iloc[0])
            pre_close = float(df['昨收价'].iloc[0])

            # 判断涨跌并设置标题颜色（rich样式）
            if current_price > pre_close:
                title_color = "red"
            elif current_price < pre_close:
                title_color = "green"
            else:
                title_color = "white"

            # 提取买1-5档和卖1-5档
            bid_data = []
            ask_data = []
            for i in range(1, 6):
                bid_price = df[f'买{i}价'].iloc[0] if f'买{i}价' in df else 'N/A'
                bid_volume = df[f'买{i}量'].iloc[0] if f'买{i}量' in df else 'N/A'
                ask_price = df[f'卖{i}价'].iloc[0] if f'卖{i}价' in df else 'N/A'
                ask_volume = df[f'卖{i}量'].iloc[0] if f'卖{i}量' in df else 'N/A'
                bid_data.append([f'Buy {i}', bid_price, bid_volume])
                ask_data.append([f'Sell {i}', ask_price, ask_volume])

            stock_data = {
                'code': stock,
                'name': stock_name,
                'title_color': title_color,
                'bids': bid_data,
                'asks': ask_data
            }
            all_data.append(stock_data)

        except Exception as e:
            console.print(f"[yellow]Failed to get data for {stock}: {e}[/yellow]")

    return all_data


def create_display_content(stocks_data):
    """
    创建rich表格和动态更新时间，包装在Panel中
    """
    # 创建rich表格
    table = Table(show_header=True, header_style="bold magenta", border_style="cyan", padding=(0, 1))
    table.add_column("Level", justify="center", width=8, style="cyan")

    # 动态调整列宽，根据最长股票代码+名称计算，增加缓冲
    max_code_name_length = max(len(f"{stock['code']} {stock['name']}") for stock in stocks_data)
    price_width = max(15, max_code_name_length + 2)  # 增加2字符缓冲
    volume_width = max(12, max_code_name_length // 2 + 2)  # 增加2字符缓冲

    # 为每只股票添加价格和数量列，使用Text对象应用颜色和换行
    for stock in stocks_data:
        header_text = Text()
        header_text.append(f"{stock['code']} ", style=stock['title_color'])
        header_text.append(f"{stock['name']}\n", style=stock['title_color'])
        header_text.append("Price", style=stock['title_color'])
        table.add_column(header_text, justify="center", width=price_width)

        volume_text = Text()
        volume_text.append(f"{stock['name']}\n", style=stock['title_color'])
        volume_text.append("Volume", style=stock['title_color'])
        table.add_column(volume_text, justify="center", width=volume_width)

    # 卖档倒序（Sell 5到Sell 1）
    for i in range(4, -1, -1):
        row = [f"[red]Sell {i + 1}[/red]"]
        for stock in stocks_data:
            row.extend([f"[red]{stock['asks'][i][1]}[/red]", f"[red]{stock['asks'][i][2]}[/red]"])
        table.add_row(*row)

    # 买档正序（Buy 1到Buy 5）
    for i in range(5):
        row = [f"[green]Buy {i + 1}[/green]"]
        for stock in stocks_data:
            row.extend([f"[green]{stock['bids'][i][1]}[/green]", f"[green]{stock['bids'][i][2]}[/green]"])
        table.add_row(*row)

    # 创建动态更新时间
    update_time = Text(f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}", style="cyan bold")

    # 将表格和更新时间包装在Panel中，增加内边距
    panel = Panel(
        table,
        border_style="cyan",
        title="[bold magenta]Stock Order Book[/]",
        title_align="center",
        padding=(1, 2),  # 增加内边距
        subtitle=update_time,
        subtitle_align="right"
    )
    return panel


async def refresh_display(stocks, refresh_interval=5):
    """
    使用rich.live.Live动态刷新盘口数据和更新时间
    """
    with Live(console=console, auto_refresh=False) as live:
        while True:
            stocks_data = get_stock_quotes_ths(stocks)
            if stocks_data:
                panel = create_display_content(stocks_data)
                live.update(panel)
            else:
                live.update(Text("No stock data", style="yellow bold"))
            live.refresh()
            await asyncio.sleep(refresh_interval)


async def main():
    ths.connect()
    try:
        stock_list = ['USZA000001', 'USHA600519', 'USZA300033', "USHA601138"]
        await refresh_display(stock_list, refresh_interval=5)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Stopped refreshing[/]")
    finally:
        ths.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
