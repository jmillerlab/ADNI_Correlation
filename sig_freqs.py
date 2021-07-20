"""Makes a mapping from feature to the number of its comparisons that have a maximum significance (lowest possible p)"""

from sys import argv
from tqdm import tqdm
from pickle import dump

from utils.iterate_comp_dicts import BasicDictIter

from utils.utils import (
    get_domain, get_col_types, ADNIMERGE_FREQ_KEY,
    EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, TOTAL_FREQ_KEY, ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY
)

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
