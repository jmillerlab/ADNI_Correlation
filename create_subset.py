"""Creates a subset of the data set by only including patients that have a particular value of a nominal feature"""

from sys import argv
from pickle import load

from utils.utils import SUBSET_PATH


def main():
	"""MAIN"""

	original_data_file: str = argv[1]
	feat_map: str = argv[2]
	cohort: str = argv[3]

	feat_map: str = 'data/feat-maps/{}/{}.p'.format(cohort, feat_map)

	with open(feat_map, 'rb') as f:
		feat_map: dict = load(f)

	unique_values: list = sorted(set(feat_map.values()))
	print('The Feature\'s Unique Values:', *unique_values)
	n_subsets: int = len(unique_values)
	subsets: list = [[] for _ in range(n_subsets)]

	with open(original_data_file, 'r') as f:
		headers: str = next(f)

		for line in f:
			row: list = line.strip().split(',')
			ptid: str = row[0]
			val = feat_map[ptid]
			idx: int = unique_values.index(val)
			subsets[idx].append(line)

	for i in range(n_subsets):
		val = unique_values[i]

		if type(val) is str:
			val = val.lower()

		subset_path: str = SUBSET_PATH.format(val)
		write_file(subset_path=subset_path, subset=subsets[i], headers=headers)


def write_file(subset_path: str, subset: list, headers: str):
	"""Saves the subset after the correct patients have been selected"""

	with open(subset_path, 'w') as f:
		f.write(headers)

		for line in subset:
			f.write(line)


if __name__ == '__main__':
	main()
