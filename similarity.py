# -*- coding: utf-8 -*-
from numpy import *
import scipy.spatial.distance as dist
### 计算pearson相关度
def sim_pearson(prefer, person1, person2):
    sim = {}
    #查找双方都评价过的项
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1           #将相同项添加到字典sim中
    #元素个数
    n = len(sim)
    if len(sim)==0:
        return -1

    # 所有偏好之和
    sum1 = sum([prefer[person1][item] for item in sim])
    sum2 = sum([prefer[person2][item] for item in sim])

    #求平方和
    sum1Sq = sum( [pow(prefer[person1][item] ,2) for item in sim] )
    sum2Sq = sum( [pow(prefer[person2][item] ,2) for item in sim] )

    #求乘积之和 ∑XiYi
    sumMulti = sum([prefer[person1][item]*prefer[person2][item] for item in sim])

    num1 = sumMulti - (sum1*sum2/n)
    num2 = sqrt( (sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if num2==0:                                                ### 如果分母为0，本处将返回0.
        return 0

    result = num1/num2
    return result

def sim_cos(vector1,vector2):
    dot_product = 0.0
    normA = 0.0
    normB = 0.0
    for a,b in zip(vector1,vector2):
        dot_product += a*b
        normA += a**2
        normB += b**2
    if normA == 0.0 or normB==0.0:
        return None
    else:
        return dot_product / ((normA*normB)**0.5)

def sim_jaccard(vector1,vector2):
    matV = [vector1,vector2]
    return dist.pdist(matV,'jaccard')[0]

if __name__ == "__main__":
    vector1 = [1,1,0,1,0,1,0,0,1]
    vector2 = [0,1,1,0,0,0,1,1,1]
    vector3 = [0,1,0,0,0]
    vector4 = [0,0,1,0,0]
    print sim_cos(vector3,vector4)