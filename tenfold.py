#!/usr/bin/env python

import parse as p
import bernoulli as b
import pprint

# code for the ten-fold cross validator being used to evaluate the classifiers
# this code will call the "classify" method for each group
# and display the average accuracy for both classifiers

pp = pprint.PrettyPrinter(indent=4)

stuff = p.parse_emails()
print pp.pprint(stuff)

b.train_bernoulli(stuff, stuff['emails'][1:])

b.classify_bernoulli(stuff, stuff['emails'][0])


