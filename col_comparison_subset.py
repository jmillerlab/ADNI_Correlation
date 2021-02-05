"""Re-runs the comparisons that were below the bonferroni alpha on a sub set of the individuals in the data set """

from sys import argv
from os import listdir, mkdir
from os.path import join, isdir
from pickle import load, dump
from pandas import read_csv, DataFrame

from utils import (
    get_filter_alpha, BONFERRONI_ALPHA, ALPHA_FILTERED_DIR, compare, get_col_types, SUBSET_PATH, SUBSET_COMP_DICTS_PATH
)


def main():
    """Main method"""

    idx: int = int(argv[1])
    subset: str = argv[2]

    comp_dicts_path: str = SUBSET_COMP_DICTS_PATH.format(subset)

    if not isdir(comp_dicts_path):
        mkdir(comp_dicts_path)

    alpha: float = get_filter_alpha(alpha=BONFERRONI_ALPHA)
    alpha_filtered_dir: str = ALPHA_FILTERED_DIR.format(alpha)

    col_types: dict = get_col_types()
    new_comps: dict = {}
    filtered_comps: list = sorted(listdir(alpha_filtered_dir))
    filtered_comps: str = filtered_comps[idx]

    assert filtered_comps.endswith('.p')

    filtered_comps: str = join(alpha_filtered_dir, filtered_comps)
    filtered_comps: dict = load(open(filtered_comps, 'rb'))
    dataset_cols: dict = get_dataset_cols(subset=subset, filtered_comps=filtered_comps)

    for (feat1, feat2), p in filtered_comps.items():
        assert p < alpha

        key: tuple = tuple(sorted([feat1, feat2]))
        new_comps[key] = compare(header1=feat1, header2=feat2, dataset_cols=dataset_cols, col_types=col_types)

    new_comps_path: str = '{}.p'.format(idx)
    new_comps_path: str = join(comp_dicts_path, new_comps_path)
    dump(new_comps, open(new_comps_path, 'wb'))


def get_dataset_cols(subset: str, filtered_comps: dict) -> dict:
    """Gets the columns from the subset to be used in the new comparisons"""

    filtered_headers: set = set()

    for feat1, feat2 in filtered_comps.keys():
        filtered_headers.add(feat1)
        filtered_headers.add(feat2)

    subset_path: str = SUBSET_PATH.format(subset)
    subset: DataFrame = read_csv(subset_path, usecols=filtered_headers)
    dataset_cols: dict = {}

    for header in filtered_headers:
        dataset_cols[header] = list(subset[header])

    return dataset_cols


if __name__ == '__main__':
    main()
