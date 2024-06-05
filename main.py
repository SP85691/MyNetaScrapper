import pathlib
from ConstituencyExtractor import ConstExtractor
from Hit_and_trail import ProperComparisonChartExtractor
from ContestingDataExtractor import ContestingDataExtractor

STATES = [
            'ArunachalPradesh',
            'Odisha',
            'Sikkim',
            'AndhraPradesh',
            'LokSabha'
        ]

if __name__ == '__main__':
    BASE_PATH = pathlib.Path(__file__).parent / 'data'
    ConstExtractor(states=STATES, BASE_PATH=BASE_PATH)
    ProperComparisonChartExtractor(states=STATES, BASE_PATH=BASE_PATH)
    ContestingDataExtractor(states=STATES)