"""Re-runs the comparisons that were below the bonferroni alpha on a sub set of the individuals in the data set"""

from sys import argv
from os import listdir, mkdir
from os.path import join, isdir
from pickle import load, dump
from pandas import read_csv, DataFrame
from tqdm import tqdm
from time import time

from utils.utils import compare, get_col_types, SUBSET_PATH, get_comp_key, SUBSET_COMP_DICTS_PATH


def main():
    """Main method"""

    idx: int = int(argv[1])
    subset: str = argv[2]
    comp_dir: str = argv[3]

    comp_dicts_path: str = SUBSET_COMP_DICTS_PATH.format(subset)

    if not isdir(comp_dicts_path):
        mkdir(comp_dicts_path)

    col_types: dict = get_col_types()
    new_comps: list = sorted(listdir(comp_dir))

    for i, file_name in enumerate(list(new_comps)):
        if not file_name.endswith('.p'):
            del new_comps[i]

    new_comps: str = new_comps[idx]

    assert new_comps.endswith('.p')

    new_comps: str = join(comp_dir, new_comps)
    print('Loading Filtered Comparisons at:', new_comps)
    new_comps: dict = load(open(new_comps, 'rb'))
    original_len: int = len(new_comps)
    print('Number Of Filtered Comparisons (Original Length):', original_len)
    t1: float = time()
    dataset_cols: dict = get_dataset_cols(subset=subset, filtered_comps=new_comps)
    print('Time Extracting The Data Set Columns: {:.2f} Minutes'.format((time() - t1) / 60))
    print('Number Of Features To Re-Analyze:', len(dataset_cols))
    n_skipped: int = 0
    t1: float = time()

    for (feat1, feat2), p in tqdm(list(new_comps.items())):
        key: tuple = get_comp_key(feat1=feat1, feat2=feat2)

        if dataset_cols[feat1] is None or dataset_cols[feat2] is None:
            # We can't compare features that have only one unique value as a result of the sub setting
            n_skipped += 1
            del new_comps[key]
        else:
            p: float = compare(header1=feat1, header2=feat2, dataset_cols=dataset_cols, col_types=col_types)

            if p == float('inf'):
                n_skipped += 1
                del new_comps[key]
            else:
                new_comps[key] = p

    new_len: int = len(new_comps)

    assert new_len + n_skipped == original_len

    print('Time Re-Analyzing On The Sub Set: {:.2f} Minutes'.format((time() - t1) / 60))
    print('Number Of Comparisons Skipped Due To One Unique Value In Sub Set:', n_skipped)
    print('Number Of Comparisons Left (New Length):', new_len)
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
        col: list = list(subset[header])

        if len(set(col)) == 1:
            # We can't compare features that have only one unique value as a result of the sub setting
            dataset_cols[header] = None
        else:
            dataset_cols[header] = col

    return dataset_cols


if __name__ == '__main__':
    main()
