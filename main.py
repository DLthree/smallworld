import os
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import pairwise_distances
import cPickle as pickle
import scandir # pip install scandir
from collections import defaultdict
import numpy as np

def build_feature_matrix(filenames, cache_file=None, force=False):
    if cache_file and os.path.exists(cache_file) and not force:
        print "using feature matrix cache %s" % cache_file
        with open(cache_file) as f:
            x = pickle.load(f)
    else:
        print "calculating feature vector"
        x = HashingVectorizer(input="filename", encoding="latin-1", decode_error="replace",
                               binary=False, ngram_range=(4,4))\
            .fit_transform(filenames)
        if cache_file:
            print "writing cache file %s" % cache_file
            with open(cache_file, "w") as f:
                pickle.dump(x, f, -1)
    return x

def build_distance_matrix(x, y, cache_file=None, force=False):
    if cache_file and os.path.exists(cache_file) and not force:
        print "using distance matrix cache %s" % cache_file
        with open(cache_file) as f:
            z = pickle.load(f)
    else:
        print "calculating connectivity matrix"
        z = pairwise_distances(x,y, metric='cosine', n_jobs=-1)
        if cache_file:
            print "writing cache file %s" % cache_file
            with open(cache_file, "w") as f:
                pickle.dump(z, f, -1)
    return z

def calc_similarity(x, y, threshold, force=False):
    z = build_distance_matrix(x, y, force=force)
    return z

def subfiles(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        files = [os.path.join(root, f) for f in files if not f.startswith('.')]
        # don't visit hidden files
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        all_files.extend(files)
    return all_files

def subdirs(path):
    return [ entry.path for entry in scandir.scandir(path) if entry.is_dir() ]

def iterarray(arr):
    it = np.nditer(arr, flags=['multi_index'])
    while not it.finished:
        i,j = it.multi_index
        v = it[0]
        yield i,j,v
        it.iternext()

class SrcPackage(object):
    def __init__(self, root_dir):
        self.name = os.path.basename(root_dir)
        self.path = root_dir
        self.files = list(subfiles(root_dir))
        self.similar_count = defaultdict(int)

    def __str__(self):
        return "%s (%d files)" % (self.name, len(self.files))

    def build_feature_matrix(self, force=False):
        self.features = build_feature_matrix(self.files, force=force)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir")
    parser.add_argument("--force", action="store_true", default=False)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()

    packages = [ SrcPackage(path) for path in subdirs(args.src_dir) ]
    for pkg in packages:
        print pkg
        pkg.build_feature_matrix(force=args.force)

    # file_owners = {}
    # for package in packages:
    #     for file in package.files:
    #         file_owners[file] = package
    #

    for a in packages:
        for b in packages:
            if a == b: continue
            similar = calc_similarity(a.features, b.features, threshold=0.2)
            import pdb; pdb.set_trace()


    # TODO pkg_connectivity(a,b) = (num similar files over thresold) / min(num a files, num b files)

    for i,j,v in iterarray(sim):
        if abs(v) > args.threshold: continue
        if i == j: continue

        print all_files[i], all_files[j]
        print i, j, v
        pkg_a = file_owners[ all_files[i] ]
        pkg_b = file_owners[ all_files[j] ]
        pkg_a.similar_count[pkg_b] += 1

    for pkg_a in packages:
        print pkg_a.name
        for pkg_b, count in pkg_a.similar_count.iteritems():
            print "  %-20s : %d" % (pkg_b.name, count)






