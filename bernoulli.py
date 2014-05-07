#!/usr/bin/env python

# code for the Multivariate Bernoulli Naive Bayes classifier

from math import *

# train the classifier with a list of email objects
# this method will populate the 'termCounts' object and return it
def train(master_dict, emails):
    # reset the counts
    for t in master_dict['termCounts']:
        master_dict['termCounts'][t] = [[0,0],[0,0],[0,0],[0,0]]

    # cycle through the terms list in each email
    for e in emails:
        # save the index where the count gets added
        i = e['truthCategory']

        # process each unique term (using a frozenset because this is gonna be a static object)
        for t in frozenset(e['terms']):
            # use index 0 at the end here to get the 1st element of the list
            # since we're doing the bernoulli count
            master_dict['termCounts'][t][i][0] += 1


# classify the given email object with the format:
def classify(master_dict, email):
    email_terms = frozenset(email['terms'])

    # initialize the classification result with prior probabilities for each classification
    # which, for bernoulli, is the number of documents with each classification divided
    # by the total number of documents
    probs = [log(1.0*c/master_dict['docCount']) if c else 0 for c in master_dict['classCount']]

    # add up the conditional probabilities
    for term, counts in master_dict['termCounts'].iteritems():
        #print term, counts
        term_in_email = term in email_terms

        for i in range(len(counts)):
            # use index 0 since we're doing bernoulli
            # compute the conditional probability for this term
            val = (counts[i][0] + 1.0) / (master_dict['classCount'][i] + 2)

            # add the probability based on whether the term occurs in the email
            if term_in_email:
                probs[i] += log(val)
            else:
                probs[i] += log(1 - val)

    print probs
    # the classification is the index of the largest probability in the list
    # the enumerate will assign indices to the values, and the max function
    # will find the tuple with the maximum value (and its index will be returned)
    return max((v,i) for i,v in enumerate(probs))[1]

