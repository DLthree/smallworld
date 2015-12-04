from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer
import timeit
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    vectorizer_params = { "hashing":HashingVectorizer, "tfidf":TfidfVectorizer }
    ngram_params = { "1gram": (1,1), "4gram": (4,4) }
    binary_params = { "binary": True, "count": False}
    for vecname, vec in vectorizer_params.iteritems():
        for ngramname, ngram in ngram_params.iteritems():
            for binaryname, binary in binary_params.iteritems():

                v = vec(input="filename", encoding="latin-1", decode_error="replace",
                        binary=binary, ngram_range=ngram)
                s = timeit.timeit(lambda: v.fit_transform(args.files), number=1000)
                print "%s %s %s vectorizer: %d s" % (vecname, ngramname, binaryname, s)


