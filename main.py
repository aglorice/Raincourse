from rich.console import Console

from api.api import RainAPI
from logic import select_menu

console = Console(width=120, log_time_format="[%Y-%m-%d %H:%M:%S.%f]")
# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    try:
        rain = RainAPI(console=console)
        while True:
            rain.login()
            select_menu(console, rain)
    except Exception as e:
        console.print(f"[red]Error: {e}")
        console.print("[red]Please try again later.")
