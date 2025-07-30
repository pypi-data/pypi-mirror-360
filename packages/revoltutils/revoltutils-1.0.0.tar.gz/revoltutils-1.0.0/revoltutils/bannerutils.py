from art import text2art
import random
from revoltlogger import Logger
from colorama import Fore,Style,init
init(autoreset=True)

class Banner:
    def __init__(self, tool_name: str = "RevoltSecurities", author: str = "RevoltSecurities"):
        self.tool_name = tool_name
        self.author = author
        self.fonts = ["big", "ogre", "shadow", "script", "graffiti", "slant"]
        self.logger = Logger()
        self.red = Fore.RED
        self.green = Fore.GREEN
        self.yellow = Fore.YELLOW
        self.blue = Fore.BLUE
        self.magenta = Fore.MAGENTA
        self.cyan = Fore.CYAN
        self.white = Fore.WHITE
        self.bold = Style.BRIGHT
        self.reset = Style.RESET_ALL
        self.color_list = [self.red, self.green, self.yellow, self.blue, self.magenta, self.cyan, self.white]
        self.random_color = random.choice(self.color_list)

    def render(self) -> None:
        selected_font = random.choice(self.fonts)
        banner_art = text2art(self.tool_name, font=selected_font)
        banner = f"""{self.bold}{self.random_color}{banner_art}{self.reset}
                     {self.bold}{self.white}- {self.author}{self.reset}\n"""
        self.logger.bannerlog(banner)