#!/usr/bin/env python
# -*- coding: utf-8 -*-

do_training             = True
do_evaluate             = True

paths = {
    #'original_train': 'all_train_part2(1).txt',
    'original_train': '../data/train.txt',
    'original_test': '../data/test.txt',
    'original_solution': '../data/KDD_Track1_solution.csv',
    'predict_output': 'predict_based_SVD_1',
    # predicted result => submission format
    'predict_submission_output': 'new_predicted_submission.csv',
}

# dataset used for training
paths['train_dataset'] = paths['original_train']
# dataset used for predicting
paths['test_dataset'] = paths['original_test']
# dataset used for computing mAP@3
paths['solution_dataset'] = paths['original_solution']

# parameters used in Latent Factor Model
# the number of lines of random sampling in each iteration
SAMPLES_NUMBER = 400000
# maximum number of iterations
TRAIN_REPEAT   = 100
# dimension of the feature vectors (`p` and `q`)
DIMENSION      = 70
# η  -- formula between formulas (3) and (4)
# learning rate
ETA    = 0.22
# λ  -- formula between formulas (3) and (4)
# used for avoiding overfitting
LAMBDA = 0.04

