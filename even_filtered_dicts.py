"""temp"""

from sys import argv
from os import mkdir, listdir, rename
from os.path import isdir
from shutil import rmtree
from pickle import dump
from math import ceil

from utils import iterate_filtered_dicts, get_comp_key, BONFERRONI_ALPHA, MAXIMUM_ALPHA

N_OUTPUT_DICTS: int = 4000
LOADED_KEY: str = 'total-len-loaded'
SAVED_KEY: str = 'total-len-saved'
NEXT_DICT_KEY: str = 'next-dict'
N_COMPS_PER_FILE_KEY: str = 'n-comps-per-file'
IDX_KEY: str = 'idx'
TMP_DIR: str = '.tmp/'


def main():
    """Main method"""

    alpha: str = argv[1]

    assert alpha == BONFERRONI_ALPHA or alpha == MAXIMUM_ALPHA

    total_len: int = 52416186173 if alpha == BONFERRONI_ALPHA else 89523104

    local_vars: dict = {
        LOADED_KEY: 0,
        SAVED_KEY: 0,
        NEXT_DICT_KEY: {},
        IDX_KEY: 0
    }

    if isdir(TMP_DIR):
        rmtree(TMP_DIR)

    mkdir(TMP_DIR)
    n_comps_per_file: int = ceil(total_len / N_OUTPUT_DICTS)

    alpha_filtered_dir: str = iterate_filtered_dicts(
        alpha=alpha, func=add_save, use_p=True, n_comps_per_file=n_comps_per_file, local_vars=local_vars
    )

    next_dict: dict = local_vars[NEXT_DICT_KEY]

    assert len(next_dict) <= n_comps_per_file
    assert local_vars[SAVED_KEY] <= local_vars[LOADED_KEY]

    save(next_dict=next_dict, local_vars=local_vars)

    assert local_vars[LOADED_KEY] == local_vars[SAVED_KEY]
    assert local_vars[LOADED_KEY] == total_len
    assert len(listdir(TMP_DIR)) == N_OUTPUT_DICTS
    assert local_vars[IDX_KEY] == N_OUTPUT_DICTS

    rmtree(alpha_filtered_dir)
    rename(src=TMP_DIR, dst=alpha_filtered_dir)


def add_save(feat1: str, feat2: str, p: float, n_comps_per_file: int, local_vars: dict):
    """Adds the next comparison to the next dictionary and saves the next dictionary if it reaches average length"""

    local_vars[LOADED_KEY] += 1
    next_dict: dict = local_vars[NEXT_DICT_KEY]
    key: tuple = get_comp_key(feat1=feat1, feat2=feat2)
    next_dict[key] = p

    if len(next_dict) == n_comps_per_file:
        save(next_dict=next_dict, local_vars=local_vars)


def save(next_dict: dict, local_vars: dict):
    """Saves the next dictionary"""

    idx: int = local_vars[IDX_KEY]
    path: str = TMP_DIR + '{}.p'.format(idx)
    local_vars[IDX_KEY] = idx + 1
    dump(next_dict, open(path, 'wb'))
    local_vars[SAVED_KEY] += len(next_dict)
    local_vars[NEXT_DICT_KEY] = {}


if __name__ == '__main__':
    main()
