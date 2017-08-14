#!/usr/bin/env python
# -*- coding: utf-8 -*-

import conf
import predict
import evaluate

if __name__ == '__main__':

    
    if conf.do_training:
    
        print 'Training...'
        predict.predict(conf.paths['train_dataset'],
                        conf.paths['test_dataset'],
                        conf.paths['predict_output'])
        
    if conf.do_evaluate:
        print 'Computing mAP@3...'
        predict_dic = evaluate.get_predict_dic(conf.paths['predict_output'])
        #evaluate.mapat3(predict_dic)
        evaluate.compute_mAP_and_rank(predict_dic)