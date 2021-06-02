"""Takes comparison dictionaries from a given directory and makes them more equal in size"""

from sys import argv
from os import mkdir, rename
from os.path import isdir, join, isfile
from shutil import rmtree
from pickle import dump

from utils.utils import get_comp_key
from utils.iterate_comp_dicts import BasicDictIter

LOADED_KEY: str = 'total-len-loaded'
SAVED_KEY: str = 'total-len-saved'
NEXT_DICT_KEY: str = 'next-dict'
N_COMPS_PER_FILE_KEY: str = 'n-comps-per-file'
IDX_KEY: str = 'idx'
TMP_DIR: str = '.tmp/'


def main():
    """Main method"""

    comp_dict_dir: str = argv[1]
    n_comps_per_file: str = int(argv[2])

    local_vars: dict = {
        LOADED_KEY: 0,
        SAVED_KEY: 0,
        NEXT_DICT_KEY: {},
        IDX_KEY: 0
    }

    if isdir(TMP_DIR):
        rmtree(TMP_DIR)

    mkdir(TMP_DIR)

    comp_dict_iter: BasicDictIter = BasicDictIter(
        comp_dict_dir=comp_dict_dir, use_p=True, func=add_save, n_comps_per_file=n_comps_per_file, local_vars=local_vars
    )

    comp_dict_iter()
    next_dict: dict = local_vars[NEXT_DICT_KEY]

    assert len(next_dict) <= n_comps_per_file
    assert local_vars[SAVED_KEY] <= local_vars[LOADED_KEY]

    save(next_dict=next_dict, local_vars=local_vars)

    assert local_vars[LOADED_KEY] == local_vars[SAVED_KEY]

    copy_gitignore(tmp_dir=TMP_DIR, comp_dict_dir=comp_dict_dir)
    rmtree(comp_dict_dir)
    rename(src=TMP_DIR, dst=comp_dict_dir)


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


def copy_gitignore(tmp_dir: str, comp_dict_dir: str):
    """Copies the .gitignore file from the temporary directory to the resulting directory"""

    gitignore_path: str = join(comp_dict_dir, '.gitignore')

    if isfile(gitignore_path):
        rename(gitignore_path, join(tmp_dir, '.gitignore'))


if __name__ == '__main__':
    main()
