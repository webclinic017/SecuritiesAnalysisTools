"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis 
#   includes use of oscillators (Stochastic, RSI, and Ultimate), 
#   momentum charting (Moving Average Convergence Divergence, 
#   Simple and Exponential Moving Averages), trend analysis (Bands, 
#   Support and Resistance, Channels), and some basic feature 
#   detection (Head and Shoulders, Pennants).
#   
"""

################################
_VERSION_ = '0.1.20'
_DATE_REVISION_ = '2019-12-01'
################################

# Imports that create final products and show progress doing so
from libs.utils import start_header, TEXT_COLOR_MAP, logo_renderer

# Imports that run operations and functions for the program
from releases.release_1 import technical_analysis as r1
from releases.prod import technical_analysis as prod 
from releases.dev import technical_analysis as dev

class App:

    normal_color = TEXT_COLOR_MAP["white"]
    prod_color = TEXT_COLOR_MAP["green"]

    def __init__(self):
        self.config = dict()
        self.isEnabled = True

    def run(self):
        logo_renderer()
        self.config = start_header(update_release=_DATE_REVISION_, version=_VERSION_, options=True)

        if 'run' in self.config['state']:
            self.config['release'] = False
            print(f"{self.prod_color}~~~~ PRODUCTION ENVIRONMENT ~~~~{self.normal_color}")
            print(" ")
            prod(self.config)

        if 'dev' in self.config['state']:
            self.config['release'] = True
            dev(self.config)

        if 'r1' in self.config['state']:
            self.config['release'] = True
            r1()

        if 'r2' in self.config['state']:
            self.config['release'] = True
            print("ERROR: release 2 has not been created yet!")

        print('Done.')



app = App()

if __name__ == '__main__':
    app.run()

