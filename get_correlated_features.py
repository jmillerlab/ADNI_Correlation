"""Gets all the features that are correlated with a given feature for a given alpha"""

from utils import iterate_filtered_dicts

from sys import argv
from pickle import dump, load
from os import mkdir
from os.path import isdir, join

PRINT_MODE: str = 'print'
GET_MODE: str = 'get'
CORRELATED_FEATS_DIR: str = 'data/correlated-feats'


def main():
    """Main method"""

    header: str = argv[1]
    alpha: str = argv[2]
    mode: str = argv[3]

    assert mode == PRINT_MODE or mode == GET_MODE

    header: str = header.upper()
    save_path: str = join(CORRELATED_FEATS_DIR, 'correlated-feats-{}-{}.p'.format(header, alpha))

    if mode == PRINT_MODE:
        correlated_feats: list = load(open(save_path, 'rb'))

        for feat in correlated_feats:
            print(feat)
    else:
        correlated_feats: list = []
        iterate_filtered_dicts(alpha=alpha, func=check_comparison, header=header, correlated_feats=correlated_feats)

        assert header not in correlated_feats
        assert len(correlated_feats) > 0
        assert len(set(correlated_feats)) == len(correlated_feats)

        if not isdir(CORRELATED_FEATS_DIR):
            mkdir(CORRELATED_FEATS_DIR)

        dump(correlated_feats, open(save_path, 'wb'))


def check_comparison(feat1: str, feat2: str, header: str, correlated_feats: list):
    """Adds the other feature to the list if it is correlated"""

    if feat1 == header or feat2 == header:
        if feat1 == header:
            correlated_feats.append(feat2)
        elif feat2 == header:
            correlated_feats.append(feat1)


if __name__ == '__main__':
    main()
