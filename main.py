import sys, os
from sklearn.feature_extraction.text import TfidfVectorizer

import scandir # pip install scandir

def calc_similarity(filenames):
    documents = [open(f).read() for f in filenames]
    tfidf = TfidfVectorizer().fit_transform(documents)
    # no need to normalize, since Vectorizer will return normalized tf-idf
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity

def subfiles(path):
    for entry in scandir.scandir(path):
        if not entry.name.startswith('.') and not entry.is_dir():
            yield entry.path

def subdirs(path):
    return [ os.path.join(path, dirname) for dirname in os.listdir(path) ]

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
    print all_files

    print calc_similarity(all_files)










