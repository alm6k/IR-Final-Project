#!/usr/bin/env python

import os

# code for the Multinomial Naive Bayes classifier
# remember to make it a method (call it 'classify' or something?) that can be called when this module is imported into the evaluation file

def train(master_dict, emails):
    # Initialize all counts to 0, as this function could be called more
    # than once, and should count up from 0
    for t in master_dict['termCounts']
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


def classify(master_dict, emails):
    #TODO: write this
    pass

