"""Makes a mapping from feature to the number of its comparisons that have a maximum significance (lowest possible p)"""

from os import listdir
from os.path import join
from pickle import load
from pandas import DataFrame
from sys import argv
from tqdm import tqdm

from utils import ALPHA_FILTERED_DIR, get_significant_alpha

FEAT_KEY: str = 'Feature'
FREQ_KEY: str = 'Frequency'


def main():
    """Main method"""

    alpha: str = argv[1]

    alpha: float = get_significant_alpha(alpha=alpha)
    alpha_filtered_dir: str = ALPHA_FILTERED_DIR.format(alpha)
    filtered_dicts: list = (listdir(alpha_filtered_dir))
    significance_frequencies: dict = {}

    for filtered_dict in tqdm(filtered_dicts):
        filtered_dict: str = join(alpha_filtered_dir, filtered_dict)
        filtered_dict: dict = load(open(filtered_dict, 'rb'))

        for (feat1, feat2), p in filtered_dict.items():
            assert p < alpha

            add_frequency(feat=feat1, significance_frequencies=significance_frequencies)
            add_frequency(feat=feat2, significance_frequencies=significance_frequencies)

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


def add_frequency(feat: str, significance_frequencies: dict):
    """Increments the frequency for a given feature"""

    if feat in significance_frequencies:
        significance_frequencies[feat] += 1
    else:
        significance_frequencies[feat] = 1


if __name__ == '__main__':
    main()
