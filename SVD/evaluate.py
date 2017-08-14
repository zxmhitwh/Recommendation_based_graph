#!/usr/bin/env python
# -*- coding: utf-8 -*-
import conf
import os
#import rank_data
from data_reader import Reader

def mapat3(predict_dic,recommend_num=3):
    mydic = {}

    for user in predict_dic.keys():
        a = predict_dic[user].items()
        a.sort(key=lambda x:x[1],reverse=True)
        item_list = [x[0] for x in a]
        if len(item_list) > recommend_num:
            mydic[user] = item_list[0:recommend_num]
        else:
            mydic[user] = item_list

    real_dic = {}
    for line in open('../../example2/KDD_Track1_solution.csv').readlines():
        #print line.split(",")[2]
        #if line.split(",")[2] == "Private\n":
        #if line.split(",")[2] == "Public\n":
        #real_dic[line.split(",")[0]] = line.split(",")[1].split()
        if line.split(",")[0] in mydic:
            if line.split(",")[0] in real_dic:
                real_dic[line.split(",")[0]].extend(line.split(",")[1].split())
            else:
                real_dic[line.split(",")[0]] = line.split(",")[1].split()
    print len(real_dic)
    N = 0
    total_value = 0
    for userid in mydic:
        #print mydic[userid],real_dic[userid]
        if len(real_dic[userid]) == 0:
            N += 1
        else:
            N += 1
            num = 0
            corrnum = 0
            fenmu = 0
            for itemid in mydic[userid]:
                num += 1 
                if str(itemid) in real_dic[userid]:
                    corrnum += 1
                    fenmu += float(corrnum)/num
            if corrnum != 0:
                total_value += fenmu/corrnum

    print "total_user:" + str(N)
    print "precious:",total_value/N
    return total_value/N,mydic,real_dic

def get_predict_dic(predict_path):
    predict_dic = {}
    for line in open(predict_path).readlines():
        userid = line.split()[0]
        item = line.split()[1]
        score = float(line.split()[2])
        predict_dic.setdefault(userid, {})    
        predict_dic[userid][item] = score
    return predict_dic



def get_rank(val, type):
    ranks = rank_data.__dict__[type.lower()]
    rank = 1
    for map3 in ranks:
        if val < map3:
            rank += 1
        else:
            break
    return rank

def compute_mAP_and_rank(predict_dic):
    mAP = mapat3(predict_dic)
    #print 111
    #print "rank: %3d  \tmAP@3: %.5f" % (get_rank(mAP - 0.03, "public"), mAP)