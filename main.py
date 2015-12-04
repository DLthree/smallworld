import sys, os
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.neighbors import LSHForest

import scandir # pip install scandir

def calc_similarity(filenames):
    dt = HashingVectorizer(input="filename", encoding="latin-1", decode_error="replace",
                           binary=True, ngram_range=(4,4))\
        .fit_transform(filenames)
    lshf = LSHForest()
    lshf.fit(dt)
    return lshf.radius_neighbors_graph(radius=0.5, mode='connectivity')
    # tfidf = TfidfVectorizer(input="filename", encoding="latin-1", decode_error="replace", ).fit_transform(filenames)
    # pairwise_similarity = tfidf * tfidf.T
    # return pairwise_similarity

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

    def __str__(self):
        return "%s (%d files)" % (self.name, len(self.files))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir")
    args = parser.parse_args()


    packages = [ SrcPackage(path) for path in subdirs(args.src_dir) ]
    for package in packages:
        print package

    all_files = sum([package.files for package in packages], [])
    print calc_similarity(all_files)






