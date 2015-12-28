import os
import errno
import logging
import cPickle as pickle

from util import list_dirs, list_files_recursive

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from scipy.sparse import coo_matrix


class Source(object):
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = os.path.abspath(path)
        self.files = list_files_recursive(path)
        self.features = None
        logging.info(str(self))

    def __str__(self):
        return "Source(%s, %d files)" % (self.name, len(self.files))

    def build_features(self):
        logging.debug("calculating features for %s" % self.name)
        x = HashingVectorizer(input="filename", encoding="latin-1", decode_error="replace",
                              binary=False, ngram_range=(4, 4))\
            .fit_transform(self.files)
        logging.debug(repr(x))
        self.features = x

    def load_features(self, filename):
        logging.debug("loading features for %s from %s" % (self.name, filename))
        with open(filename) as f:
            x = pickle.load(f)
        logging.debug(repr(x))
        self.features = x

    def save_features(self, filename):
        assert self.features is not None
        logging.debug("saving features for %s to %s" % (self.name, filename))
        with open(filename, "w") as f:
            pickle.dump(self.features, f, -1)

    def build_distance_matrix(self, other):
        assert self.features is not None
        assert other.features is not None
        logging.debug("calculating distance %s to %s" % (self.name, other.name))
        z = pairwise_distances(self.features, other.features, metric='cosine', n_jobs=-1)
        return z

    def build_similarity_matrix(self, other, threshold):
        z = self.build_distance_matrix(other)
        return coo_matrix(z < threshold)


class Smallworld(object):
    def __init__(self, path, cache_path=None):
        self.path = os.path.abspath(path)
        self.dirs = list_dirs(path)
        self.sources = [Source(p) for p in self.dirs]

        if cache_path is not None:
            self.cache_path = cache_path
        else:
            self.cache_path = os.path.join(path, '.smallworld')
        logging.debug('using cache_path %s' % self.cache_path)

        # mkdir cache_path
        try:
            os.mkdir(self.cache_path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        logging.info(str(self))

    def __str__(self):
        return "Smallworld(%s, %d sources)" % (self.path, len(self.sources))

    def resume(self):
        # load or calculate features for each source
        for src in self.sources:
            path = os.path.join(self.cache_path, "%s.features" % src.name)
            if os.path.exists(path):
                src.load_features(path)
            else:
                src.build_features()
                src.save_features(path)

        # load similarity results
        pass  # TODO

    def save(self):
        # save similarity results
        pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('-v', '--verbose', action='count')
    args = parser.parse_args()

    if args.verbose <= 0:
        loglevel = logging.WARN
    elif args.verbose == 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format="%(message)s")

    s = Smallworld(args.path)
    s.resume()
    for a in s.sources:
        for b in s.sources:
            if a == b: continue
            a.build_distance_matrix(b)
            # d[a.name, b.name] = a.build_similarity_matrix(b, threshold)

    s.save()
