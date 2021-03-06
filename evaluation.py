#!/usr/bin/env python

# code for the ten-fold cross validator being used to evaluate the classifiers
# this code will call the "classify" method for each group
# and display the average accuracy for both classifiers
# in addition, the average rand index across the groups will be calculated

import parse as p
import bernoulli as b
import multinomial as m
import pprint
import itertools as it
import math

# pretty printer
pp = pprint.PrettyPrinter(indent=4)

# parse the emails
master_dict = p.parse_emails()

print "# emails per class:", master_dict['classCount']
print "Vocabulary size: %d" % master_dict['vocabSize']

# average successful classification rate for the ten-fold CV
bernAvg = 0.0
multAvg = 0.0

# average rand index for each model
bernRandAvg = 0.0
multRandAvg = 0.0

# make the 10 groups of emails
groups = [master_dict['emails'][i::10] for i in xrange(10)]

# test each group against the other groups
for i in xrange(1, len(groups)+1):
    # test group is the ith group
    testGroup = groups[i-1]
    testTruths = [k['truthCategory'] for k in testGroup]
    testSize = len(testTruths)

    # holds the classification results of each model
    testBClass = []
    testMClass = []

    # training group is all the other groups
    # flattened into one list
    trainGroup = list(it.chain.from_iterable(groups[0:i-1] + groups[i:10]))

    # train with the training group
    b.train(master_dict, trainGroup)
    m.train(master_dict, trainGroup)

    print "\n\033[1;32m----- TEST GROUP %d -----\033[0m" % i
    # classify each item in the test group
    for item in testGroup:
        testBClass.append(b.classify(master_dict, item))
        testMClass.append(m.classify(master_dict, item))

    # debug print resulting classifications
    print "  truth:", testTruths
    print "b-class:", testBClass
    print "m-class:", testMClass

    # compute the score for this iteration
    print "\033[1;33mBern\033[0m accuracy: %.4f" % (1.0*sum([x[0] == x[1] for x in it.izip(testTruths, testBClass)]) / testSize)
    bernAvg += 1.0*sum([x[0] == x[1] for x in it.izip(testTruths, testBClass)]) / testSize
    print "\033[1;31mMult\033[0m accuracy: %.4f" % (1.0*sum([x[0] == x[1] for x in it.izip(testTruths, testMClass)]) / testSize)
    multAvg += 1.0*sum([x[0] == x[1] for x in it.izip(testTruths, testMClass)]) / testSize

    """
    RI = (A + D) / (A + B + C + D)
    A = same truth, same clust
    B = same truth, diff clust
    C = diff truth, same clust
    D = diff truth, diff clust
    """
    # compute the rand index for this iteration of bernoulli classifier
    A = B = C = D = 0
    for x in it.izip(it.combinations(testTruths, 2), it.combinations(testBClass, 2)):
        #print x
        t = x[0] # truth pair
        c = x[1] # class pair

        # increment the right set
        # corresponding to the rules above
        if t[0] == t[1] and c[0] == c[1]:
            A += 1
        elif t[0] == t[1] and c[0] != c[1]:
            B += 1
        elif t[0] != t[1] and c[0] == c[1]:
            C += 1
        elif t[0] != t[1] and c[0] != c[1]:
            D += 1

    #print "Bern RI vals for %d:" % i, A, B, C, D
    try:
        print "\033[1;33mBern\033[0m RI score: %.4f" % (1.0*(A+D)/(A+B+C+D))
        bernRandAvg += 1.0*(A+D)/(A+B+C+D)
    except:
        pass

    # repeat for the multinomial classifier
    A = B = C = D = 0
    for x in it.izip(it.combinations(testTruths, 2), it.combinations(testMClass, 2)):
        #print x
        t = x[0] # truth pair
        c = x[1] # class pair

        # increment the right set
        # corresponding to the rules above
        if t[0] == t[1] and c[0] == c[1]:
            A += 1
        elif t[0] == t[1] and c[0] != c[1]:
            B += 1
        elif t[0] != t[1] and c[0] == c[1]:
            C += 1
        elif t[0] != t[1] and c[0] != c[1]:
            D += 1

    #print "Mult RI vals for %d:" % i, A, B, C, D
    try:
        print "\033[1;31mMult\033[0m RI score: %.4f" % (1.0*(A+D)/(A+B+C+D))
        multRandAvg += 1.0*(A+D)/(A+B+C+D)
    except:
        pass


# print the results
print "\n\n\033[1;35m*** Results ***\033[0m\n-----"
print "Mean \033[1;33mBern\033[0m Accuracy:   %.4f" % (bernAvg / 10.0)
print "Mean \033[1;31mMult\033[0m Accuracy:   %.4f" % (multAvg / 10.0)

print "-----"
print "Mean \033[1;33mBern\033[0m Rand Index: %.4f" % (bernRandAvg / 10.0)
print "Mean \033[1;31mMult\033[0m Rand Index: %.4f" % (multRandAvg / 10.0)

