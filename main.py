import os
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.neighbors import NearestNeighbors
import cPickle as pickle
import scandir # pip install scandir
from collections import defaultdict
import scipy

def build_feature_matrix(filenames, cache_file=None, force=False):
    if cache_file and os.path.exists(cache_file) and not force:
        print "using feature matrix cache %s" % cache_file
        with open(cache_file) as f:
            dt = pickle.load(f)
    else:
        print "calculating feature vector"
        dt = HashingVectorizer(input="filename", encoding="latin-1", decode_error="replace",
                               binary=True, ngram_range=(4,4))\
            .fit_transform(filenames)
        if cache_file:
            print "writing cache file %s" % cache_file
            with open(cache_file, "w") as f:
                pickle.dump(dt, f, -1)
    return dt

def build_distance_matrix(dt, threshold=0.5, cache_file=None, force=False):
    if cache_file and os.path.exists(cache_file) and not force:
        print "using distance matrix cache %s" % cache_file
        with open(cache_file) as f:
            mat = pickle.load(f)
    else:
        print "calculating distance matrix"

        # nn = NearestNeighbors()
        # print "  fitting"
        # nn.fit(dt)
        # print "  generating neighbor graph"
        # mat = nn.radius_neighbors_graph(radius=threshold, mode='distance')
        mat = scipy.spatial.distance.pdist(dt)


        if cache_file:
            print "writing cache file %s" % cache_file
            with open(cache_file, "w") as f:
                pickle.dump(mat, f, -1)
    return mat

def calc_similarity(filenames, force=False):
    sig = hash(tuple(filenames))
    dt = build_feature_matrix(filenames, force=force, cache_file="features-%x.npy" % sig)
    mat = build_distance_matrix(dt, threshold=0.5, force=force, cache_file="distance-%x.npy" % sig)
    return mat

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

def get_file_tree(root_dir):
    return list(subfiles(root_dir))

class SrcPackage(object):
    def __init__(self, root_dir):
        self.name = os.path.basename(root_dir)
        self.path = root_dir
        self.files = get_file_tree(root_dir)
        self.similar_count = defaultdict(int)

    def __str__(self):
        return "%s (%d files)" % (self.name, len(self.files))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir")
    parser.add_argument("--force", action="store_true", default=False)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    packages = [ SrcPackage(path) for path in subdirs(args.src_dir) ]
    for package in packages:
        print package

    file_owners = {}
    for package in packages:
        for file in package.files:
            file_owners[file] = package

    all_files = sum([package.files for package in packages], [])
    if args.limit:
        all_files = all_files[:args.limit]
        print "using limit of %d documents" % args.limit
    sim = calc_similarity(all_files, force=args.force)

    coo = sim.tocoo()
    for i,j,v in zip(coo.row, coo.col, coo.data):
        pkg_a = file_owners[ all_files[i] ]
        pkg_b = file_owners[ all_files[j] ]
        pkg_a.similar_count[pkg_b] += 1

    for pkg_a in packages:
        print pkg_a.name
        for pkg_b, count in pkg_a.similar_count.iteritems():
            print "  %-20s : %d" % (pkg_b.name, count)






