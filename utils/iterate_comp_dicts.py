"""Contains functionality for iterating through comparison dictionaries"""

from os import listdir
from os.path import join
from pickle import load
from tqdm import tqdm


class CompDictIter:
    """A base class for iterating through comparison dictionaries"""

    def __init__(self, comp_dict_dir: str, func: callable, **kwargs: dict):
        self.comp_dict_dir: str = comp_dict_dir
        self.func: callable = func
        self.kwargs: dict = kwargs
        self._remove_non_comp_files()

    def _remove_non_comp_files(self):
        """Removes files from the list of comparisons dictionaries that are not comparison dictionaries"""

        comp_dicts: list = listdir(self.comp_dict_dir)
        new_comp_dicts: list = []

        for comp_dict in comp_dicts:
            if comp_dict.endswith('.p'):
                new_comp_dicts.append(comp_dict)

        comp_dicts: list = sorted(new_comp_dicts)
        self.comp_dicts: list = comp_dicts

    def _do_iter(self, feat1: str, feat2: str, p: float):
        """The functionality to perform on a given comparison in an iteration"""

        raise NotImplementedError

    def __call__(self):
        for comp_dict in tqdm(self.comp_dicts):
            comp_dict: str = join(self.comp_dict_dir, comp_dict)
            comp_dict: dict = load(open(comp_dict, 'rb'))

            for (feat1, feat2), p in comp_dict.items():
                self._do_iter(feat1=feat1, feat2=feat2, p=p)


class IterByIdx(CompDictIter):
    """Iterates through the comparison dictionaries in a given section and performs a given function on them"""

    def __init__(self, comp_dict_dir: str, func: callable, idx: int, section_size: int, **kwargs: dict):
        super().__init__(comp_dict_dir=comp_dict_dir, func=func, **kwargs)
        n_dicts: int = len(self.comp_dicts)
        self.start_idx: int = idx * section_size

        assert self.start_idx < n_dicts

        self.stop_idx: int = min(self.start_idx + section_size, n_dicts)
        self.comp_dicts: list = self.comp_dicts[self.start_idx:self.stop_idx]

    def _do_iter(self, feat1: str, feat2: str, p: float):
        """Implements abstract method"""

        self.func(feat1=feat1, feat2=feat2, p=p, **self.kwargs)


class BasicDictIter(CompDictIter):
    """Iterates through all the comparisons in a directory and performs a function on them"""

    def __init__(self, comp_dict_dir: str, use_p: bool, func: callable, **kwargs: dict):
        super().__init__(comp_dict_dir=comp_dict_dir, func=func, **kwargs)
        self.use_p: bool = use_p

    def _do_iter(self, feat1: str, feat2: str, p: float):
        """Implements abstract method"""

        if self.use_p:
            self.func(feat1=feat1, feat2=feat2, p=p, **self.kwargs)
        else:
            self.func(feat1=feat1, feat2=feat2, **self.kwargs)
