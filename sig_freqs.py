"""Makes a mapping from feature to the number of its comparisons that have a maximum significance (lowest possible p)"""

from pandas import DataFrame, unique
from sys import argv
from tqdm import tqdm
from pickle import dump

from utils.iterate_comp_dicts import BasicDictIter

from utils.utils import (
    SIGNIFICANT_FREQUENCIES_CSV_PATH, get_domain, get_col_types, ADNIMERGE_FREQ_KEY,
    EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, TOTAL_FREQ_KEY, DOMAIN_KEY, ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY
)

FEAT_KEY: str = 'Feature'

DOMAIN_TO_DOMAIN_FREQ_KEY: dict = {
    ADNIMERGE_KEY: ADNIMERGE_FREQ_KEY,
    EXPRESSION_KEY: EXPRESSION_FREQ_KEY,
    MRI_KEY: MRI_FREQ_KEY
}


def main():
    """Main method"""

    comp_dict_dir: str = argv[1]
    file_path: str = argv[2]

    significance_frequencies: dict = {}
    col_types: dict = get_col_types()

    comp_dict_iter: BasicDictIter = BasicDictIter(
        comp_dict_dir=comp_dict_dir, use_p=False, func=add_frequencies,
        significance_frequencies=significance_frequencies, col_types=col_types
    )

    comp_dict_iter()
    dump(significance_frequencies, open(file_path, 'wb'))

    '''
    sort_func: callable = lambda key: significance_frequencies[key][TOTAL_FREQ_KEY]

    significance_frequencies: list = [(key, significance_frequencies[key]) for key in sorted(
        significance_frequencies, key=sort_func, reverse=True
    )]

    table: DataFrame = DataFrame(columns=[
        FEAT_KEY, ADNIMERGE_FREQ_KEY, EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, TOTAL_FREQ_KEY, DOMAIN_KEY
    ])

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
    '''


def add_frequencies(feat1: str, feat2: str, significance_frequencies: dict, col_types: dict):
    """Increments the frequencies of two features in a comparison"""

    add_frequency(feat=feat1, other=feat2, significance_frequencies=significance_frequencies, col_types=col_types)
    add_frequency(feat=feat2, other=feat1, significance_frequencies=significance_frequencies, col_types=col_types)


def add_frequency(feat: str, other: str, significance_frequencies: dict, col_types: dict):
    """Increments the frequency for a given feature"""

    other_domain: str = get_domain(feat=other, col_types=col_types)
    other_domain_freq_key: str = DOMAIN_TO_DOMAIN_FREQ_KEY[other_domain]

    if feat in significance_frequencies:
        significance_frequencies[feat][TOTAL_FREQ_KEY] += 1
        significance_frequencies[feat][other_domain_freq_key] += 1
    else:
        freqs: dict = {
            TOTAL_FREQ_KEY: 1,
            ADNIMERGE_FREQ_KEY: 0,
            EXPRESSION_FREQ_KEY: 0,
            MRI_FREQ_KEY: 0
        }

        freqs[other_domain_freq_key] = 1
        significance_frequencies[feat] = freqs


if __name__ == '__main__':
    main()