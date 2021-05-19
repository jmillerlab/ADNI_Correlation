"""Contains functionality for iterating through comparison dictionaries"""

from os import listdir
from os.path import join
from pickle import load
from tqdm import tqdm

from utils.utils import get_significant_alpha, ALPHA_FILTERED_DIR


def iterate_comp_dicts(outer_func: callable, inner_func: callable, outer_kwargs: dict, inner_kwargs: dict):
    """Iterates through comparison dictionaries in a specified fashion"""

    outer_func(**outer_kwargs, )


def iterate_by_idx(comp_dict_dir: str, idx: int, section_size: int, func: callable, **kwargs) -> tuple:
    """Iterates through the comparison dictionaries in a given section and performs a given function on them"""

    comp_dict_dir: str = join('../data', comp_dict_dir)
    comp_dicts: list = listdir(comp_dict_dir)

    # Remove the files that aren't comparison dictionaries
    new_comp_dicts: list = []

    for comp_dict in comp_dicts:
        if comp_dict.endswith('.p'):
            new_comp_dicts.append(comp_dict)

    comp_dicts: list = sorted(new_comp_dicts)
    del new_comp_dicts

    n_dicts: int = len(comp_dicts)
    start_idx: int = idx * section_size

    assert start_idx >= n_dicts

    stop_idx: int = min(start_idx + section_size, n_dicts)
    comp_dicts: list = comp_dicts[start_idx:stop_idx]

    for comp_dict in comp_dicts:
        comp_dict: str = join(comp_dict_dir, comp_dict)
        comp_dict: dict = load(open(comp_dict, 'rb'))

        for (feat1, feat2), p in comp_dict.items():
            func(feat1=feat1, feat2=feat2, p=p, **kwargs)

    return start_idx, stop_idx


def iterate_filtered_dicts(alpha: str, func: callable, use_p: bool = False, **kwargs) -> str:
    """Iterates through the comparisons that were filtered for a given alpha"""

    alpha: float = get_significant_alpha(alpha=alpha)
    alpha_filtered_dir: str = ALPHA_FILTERED_DIR.format(alpha)
    filtered_dicts: list = (listdir(alpha_filtered_dir))

    for filtered_dict in tqdm(filtered_dicts):
        filtered_dict: str = join(alpha_filtered_dir, filtered_dict)
        filtered_dict: dict = load(open(filtered_dict, 'rb'))

        for (feat1, feat2), p in filtered_dict.items():
            assert p < alpha

            if use_p:
                func(feat1=feat1, feat2=feat2, p=p, **kwargs)
            else:
                func(feat1=feat1, feat2=feat2, **kwargs)

    return alpha_filtered_dir
