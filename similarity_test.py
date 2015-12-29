import argparse
import itertools

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from scipy.sparse import coo_matrix


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    vec = HashingVectorizer(input="filename", encoding="latin-1", decode_error="replace",
                            binary=False, ngram_range=(4, 4))
    print vec

    x = vec.fit_transform(args.files)
    print x

    z = pairwise_distances(x, metric='cosine', n_jobs=-1)
    print z

    m = coo_matrix(z)
    print m

    for i, j, v in itertools.izip(m.row, m.col, m.data):
        if i <= j:
            print "%-20s %-20s %-10s" % (args.files[i], args.files[j], v)



