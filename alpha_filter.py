"""Filters the comparisons with p values that are above a given alpha"""

from sys import argv
from os import mkdir
from os.path import isdir, join
from pickle import dump

from utils.utils import get_comp_key
from utils.iterate_comp_dicts import IterByIdx


def main():
    """Main method"""

    comp_dict_dir: str = argv[1]
    alpha: float = float(argv[2])
    idx: int = int(argv[3])
    section_size: int = int(argv[4])
    alpha_filtered_dir: str = argv[5]

    if not isdir(alpha_filtered_dir):
        mkdir(alpha_filtered_dir)

    filtered_comparisons: dict = {}

    comp_dict_iter: IterByIdx = IterByIdx(
        comp_dict_dir=comp_dict_dir, func=filter_by_alpha, idx=idx, section_size=section_size, alpha=alpha,
        filtered_comparisons=filtered_comparisons
    )

    start_idx: int = comp_dict_iter.start_idx
    stop_idx: int = comp_dict_iter.stop_idx
    comp_dict_iter()
    print('Number of filtered comparisons:', len(filtered_comparisons))
    filtered_comparisons_path: str = join(alpha_filtered_dir, '{}-{}.p'.format(start_idx, stop_idx))
    dump(filtered_comparisons, open(filtered_comparisons_path, 'wb'))


def filter_by_alpha(feat1: str, feat2: str, p: float, alpha: float, filtered_comparisons: dict):
    """Adds a comparison to a dictionary of filtered comparisons if its p value is lower than a given alpha"""

    if p < alpha:
        key: tuple = get_comp_key(feat1=feat1, feat2=feat2)
        filtered_comparisons[key] = p


if __name__ == '__main__':
    main()
