import sys, os
#from sklearn.feature_extraction.text import TfidfVectorizer

def calc_similarity(filenames):
    documents = [open(f) for f in text_files]
    tfidf = TfidfVectorizer().fit_transform(documents)
    # no need to normalize, since Vectorizer will return normalized tf-idf
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir")
    args = parser.parse_args()

    for root, folders, files in os.walk(args.src_dir):
        print root, folders, files






