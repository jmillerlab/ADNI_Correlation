"""Makes a mapping from a feature to the features that it is significantly correlated with"""

from sys import argv
from pickle import dump

from utils.iterate_comp_dicts import BasicDictIter
from utils.utils import get_domain, get_col_types, MRI_KEY


def main():
    """Main method"""

    comp_dict_dir: str = argv[1]
    file_path: str = argv[2]
    alpha: float = None

    if len(argv) > 3:
        alpha: float = float(argv[3])

    significance_feats: dict = {}
    col_types: dict = get_col_types()

    comp_dict_iter: BasicDictIter = BasicDictIter(
        comp_dict_dir=comp_dict_dir, use_p=True, func=add_feats,
        significance_feats=significance_feats, col_types=col_types, alpha=alpha
    )

    comp_dict_iter()
    dump(significance_feats, open(file_path, 'wb'))


def add_feats(feat1: str, feat2: str, p: float, significance_feats: dict, col_types: dict, alpha: float):
    """Appends to the list of strongly correlated features for the two features in a comparison"""

    add_feat(
        feat=feat1, other=feat2, significance_feats=significance_feats, col_types=col_types, p=p,
        alpha=alpha
    )

    add_feat(
        feat=feat2, other=feat1, significance_feats=significance_feats, col_types=col_types, p=p,
        alpha=alpha
    )


def add_feat(feat: str, other: str, significance_feats: dict, col_types: dict, p: float, alpha: float):
    """Appends to the list of features that are strongly correlated with a given feature"""

    if alpha is not None:
        # If there is an alpha specified, ensure the p value meets the alpha
        if p > alpha:
            return

    domain: str = get_domain(feat=feat, col_types=col_types)

    if domain == MRI_KEY:
        # Do not list MRI features
        return

    other_domain: str = get_domain(feat=other, col_types=col_types)

    if other_domain == MRI_KEY:
        # The other feature should not be MRI either to save space
        return

    if feat in significance_feats:
        significance_feats[feat].append(other)
    else:
        significance_feats[feat] = [other]


if __name__ == '__main__':
    main()
