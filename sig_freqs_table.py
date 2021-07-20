"""Creates the table from the dictionary data created by the sig-freqs script"""

from pandas import DataFrame, unique
from pickle import load
from tqdm import tqdm
from sys import argv

from utils.utils import (
    get_col_types, get_domain, TOTAL_FREQ_KEY, ADNIMERGE_FREQ_KEY, EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, DOMAIN_KEY
)

FEAT_KEY: str = 'Feature'


def main() -> DataFrame:
    """Makes the significance frequencies table from the corresponding dictionary"""

    dict_path: str = argv[1]
    table_path: str = argv[2]

    significance_frequencies: dict = load(open(dict_path, 'rb'))
    sort_func: callable = lambda key: significance_frequencies[key][TOTAL_FREQ_KEY]

    significance_frequencies: list = [(key, significance_frequencies[key]) for key in sorted(
        significance_frequencies, key=sort_func, reverse=True
    )]

    table: DataFrame = DataFrame(columns=[
        FEAT_KEY, ADNIMERGE_FREQ_KEY, EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, TOTAL_FREQ_KEY, DOMAIN_KEY
    ])

    col_types: dict = get_col_types()

    for feat, feat_freqs in tqdm(significance_frequencies):
        adnimerge_freq: int = feat_freqs[ADNIMERGE_FREQ_KEY]
        expression_freq: int = feat_freqs[EXPRESSION_FREQ_KEY]
        mri_freq: int = feat_freqs[MRI_FREQ_KEY]
        total_freq: int = feat_freqs[TOTAL_FREQ_KEY]
        domain: str = get_domain(feat=feat, col_types=col_types)

        row: dict = {
            FEAT_KEY: feat,
            ADNIMERGE_FREQ_KEY: adnimerge_freq,
            EXPRESSION_FREQ_KEY: expression_freq,
            MRI_FREQ_KEY: mri_freq,
            TOTAL_FREQ_KEY: total_freq,
            DOMAIN_KEY: domain
        }

        table: DataFrame = table.append(row, ignore_index=True)

    assert len(unique(table[FEAT_KEY])) == len(table)

    table.to_csv(table_path, index=False)


if __name__ == '__main__':
    main()
