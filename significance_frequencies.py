"""Makes a mapping from feature to the number of its comparisons that have a maximum significance (lowest possible p)"""

from pandas import DataFrame
from sys import argv

from utils import iterate_filtered_dicts

FEAT_KEY: str = 'Feature'
FREQ_KEY: str = 'Frequency'


def main():
    """Main method"""

    alpha: str = argv[1]

    significance_frequencies: dict = {}
    iterate_filtered_dicts(alpha=alpha, func=add_frequencies, significance_frequencies=significance_frequencies)

    significance_frequencies: list = [
        (key, significance_frequencies[key]) for key in sorted(
            significance_frequencies, key=significance_frequencies.get, reverse=True
        )
    ]

    print('Number Of Features That Show Up In At Least One Significance Comparison: {} | For Alpha: {}'.format(
        len(significance_frequencies), alpha
    ))

    table: DataFrame = DataFrame(columns=[FEAT_KEY, FREQ_KEY])

    for feat, frequency in significance_frequencies:
        row: dict = {
            FEAT_KEY: feat,
            FREQ_KEY: frequency,
        }
        table: DataFrame = table.append(row, ignore_index=True)

    table_path: str = 'data/significance-frequencies-{}.csv'.format(alpha)
    table.to_csv(table_path, index=False)


def add_frequencies(feat1: str, feat2: str, significance_frequencies: dict):
    """Increments the frequencies of two features in a comparison"""

    add_frequency(feat=feat1, significance_frequencies=significance_frequencies)
    add_frequency(feat=feat2, significance_frequencies=significance_frequencies)


def add_frequency(feat: str, significance_frequencies: dict):
    """Increments the frequency for a given feature"""

    if feat in significance_frequencies:
        significance_frequencies[feat] += 1
    else:
        significance_frequencies[feat] = 1


if __name__ == '__main__':
    main()
