#!/usr/bin/env python

from math import log
import copy

# code for the Multinomial Naive Bayes classifier
# remember to make it a method (call it 'classify' or something?) that can be called when this module is imported into the evaluation file

# list telling how many terms (includes duplicate occurrences) appear in each
# category - this is used in the classify function.
num_terms_in_category = None
# Prior probabilities for each category (this is the number of documents in
# a given category divided by the total number of documents). We Should only
# need to calculate this once, so we keep it as a global
priors = None

def train(master_dict, emails):
    """ TODO: Doc string """

    # Initialize all counts to 0, as this function could be called more
    # than once, and should count up from 0
    for t in master_dict['termCounts']:
        for derp in xrange(4):
            master_dict['termCounts'][t][derp][1] = 0

    for e in emails:
        # save the index where the count gets added
        i = e['truthCategory']

        for t in e['terms']:
            # use index 1 at the end here to get the 2nd element of the list
            # since we're doing the multinomial count
            master_dict['termCounts'][t][i][1] += 1
#END train_multinomial()


def classify(master_dict, email):
    """ TODO: Doc string """

    global num_terms_in_category
    global priors

    # Initialize the prior probabilities for each classification, which is
    # the number of documents with each classification divided by the
    # total number of documents
    if priors is None:
        priors = [log(1.0*c/master_dict['docCount']) if c else 0 for c in master_dict['classCount']]

    # Only once should you need to determine the number of terms (including
    # repeats) per category - you can reuse this for each call to classify()
    if num_terms_in_category is None:
        num_terms_in_category = [0,0,0,0]
        for email in master_dict['emails']:
            num_terms_in_category[email['truthCategory']] += len(email['terms'])

    # Determine vocabulary size (number of unique terms across all the
    # categories) - this should be the vocabSize value contained in
    # master_dict, with the possible addition of terms from the given email
    vocab_size = master_dict['vocabSize']
    for term in frozenset(email['terms']): # don't check the same term >1 time
        if term not in master_dict['termCounts']:
            vocab_size += 1

    # Calculate probabilities of the email being in each category
    probs = copy.deepcopy(priors)
    for i_cat in range(len(master_dict['classCount'])):
        for term in email['terms']:
            probs[i_cat] += log((master_dict['termCounts'][term][i_cat][1] + 1.0) / (num_terms_in_category[i_cat] + vocab_size))
   
    # Return the index of the category with the largest probability
    return max((v,i) for i,v in enumerate(probs))[1]
#END classify()
