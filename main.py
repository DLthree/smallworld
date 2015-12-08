import os
from sklearn.feature_extraction.text import HashingVectorizer
import cPickle as pickle
import scandir # pip install scandir
from collections import defaultdict
import scipy
import scipy.spatial

def file_connectivity(x, y, threshold, samples):
    # todo normalize this to 0..1
    # todo return 1 - x because 0.0 entries are ignored in sparse matrix
    d = scipy.spatial.distance.euclidean(x, y)
    print d
    if d < threshold:
        return d

    # if scipy.sp
    # sqthreshold = threshold**2
    # sqdistance = scipy.spatial.distance.sqeuclidean(x[:samples],y[:samples])
    # if sqdistance < sqthreshold:


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

def build_distance_matrix(dt, threshold, cache_file=None, force=False):
    if cache_file and os.path.exists(cache_file) and not force:
        print "using distance matrix cache %s" % cache_file
        with open(cache_file) as f:
            mat = pickle.load(f)
    else:
        print "calculating connectivity matrix"
        n = dt.shape[0]
        mat = scipy.sparse.lil_matrix( (n, n) )
        for i,x in enumerate(dt):
            xd = x.todense()
            for j,y in enumerate(dt):
                yd = y.todense()
                print i,j,
                d = file_connectivity(xd,yd,threshold=threshold, samples=1)
                if d is not None:
                    print "!"
                    mat[i,j] = d
        if cache_file:
            print "writing cache file %s" % cache_file
            with open(cache_file, "w") as f:
                pickle.dump(mat, f, -1)
    return mat

def calc_similarity(filenames, threshold, force=False):
    sig = hash(tuple(filenames))
    dt = build_feature_matrix(filenames, force=force, cache_file="features-%x.npy" % sig)
    mat = build_distance_matrix(dt, threshold, force=force, cache_file="distance-%x.npy" % sig)
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
    parser.add_argument("--threshold", type=float, default=0.5)
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
    sim = calc_similarity(all_files, threshold=args.threshold, force=args.force)

    # TODO pkg_connectivity(a,b) = (num similar files over thresold) / min(num a files, num b files)

    coo = sim.tocoo()
    for i,j,v in zip(coo.row, coo.col, coo.data):
        pkg_a = file_owners[ all_files[i] ]
        pkg_b = file_owners[ all_files[j] ]
        pkg_a.similar_count[pkg_b] += 1
        print i, j, v

    for pkg_a in packages:
        print pkg_a.name
        for pkg_b, count in pkg_a.similar_count.iteritems():
            print "  %-20s : %d" % (pkg_b.name, count)






