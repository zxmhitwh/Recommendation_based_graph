#-*-coding:utf-8-*-  
from math import sqrt

def sim_pearson(prefer, person1, person2):
    sim = {}
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1       
    n = len(sim)
    if len(sim)==0:
        return -1
    sum1 = sum([prefer[person1][item] for item in sim])  
    sum2 = sum([prefer[person2][item] for item in sim])  
    sum1Sq = sum( [pow(prefer[person1][item] ,2) for item in sim] )
    sum2Sq = sum( [pow(prefer[person2][item] ,2) for item in sim] )

    sumMulti = sum([prefer[person1][item]*prefer[person2][item] for item in sim])

    num1 = sumMulti - (sum1*sum2/n)
    num2 = sqrt( (sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))  
    if num2==0:                                               
        return 0  
    result = num1/num2
    return result

def sim_cosin(prefer,person1,person2):
	item_list = []
	for item in prefer[person1]:
		if item in prefer[person2]:
			item_list.append(item)
	if len(item_list) == 0:
		return -1
	else:
		vector1 = [0 for i in range(len(item_list))]
		vector2 = [0 for i in range(len(item_list))]
		for item in prefer[person1]:
			if item in item_list:
				vector1[item_list.index(item)] =  prefer[person1][item]
		for item in prefer[person2]:
			if item in item_list:
				vector2[item_list.index(item)] = prefer[person2][item]
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


def topKMatches(prefer, person, itemId, k, sim = sim_pearson):
	userSet = []
	scores = []
	users = []
	for user in prefer:
		if itemId in prefer[user]:
			userSet.append(user)
	#print userSet
	for other in userSet:
		if other != person:
			#print sim(prefer, person, other)
			scores.append((sim(prefer, person, other),other))
	#print person,scores
	scores.sort()
	scores.reverse()
	if len(scores)<=k:       
		for item in scores:
			users.append(item[1])
		return users
	else:
		kscore = scores[0:k]
		for item in kscore:
			users.append(item[1])  
		return users              



def getAverage(prefer, userId):
    count = 0
    sum = 0
    for item in prefer[userId]:
        sum = sum + prefer[userId][item]
        count = count+1
    return sum/count



def getRating(prefer1, userId, itemId, knumber,similarity=sim_pearson):
    sim = 0.0
    averageOther =0.0
    jiaquanAverage = 0.0
    simSums = 0.0

    users = topKMatches(prefer1, userId, itemId, knumber, sim = sim_pearson)

    if userId not in prefer1.keys():
    	averageOfUser = 3
    else:
		averageOfUser = getAverage(prefer1, userId)     


    for other in users:
        sim = similarity(prefer1, userId, other)    
        averageOther = getAverage(prefer1, other)   
   
        simSums += abs(sim)    
        jiaquanAverage +=  (prefer1[other][itemId]-averageOther)*sim  

    if simSums==0:
        return averageOfUser
    else:
        return (averageOfUser + jiaquanAverage/simSums)  

def get_training_test():
	train_dic = {}
	test_dic = {}
	for line in open("data/train.txt").readlines():
		userid = line.split()[0]
		itemid = line.split()[1]
		score = float(line.split()[2])
		train_dic.setdefault(userid, {})
		train_dic[userid][itemid] = score
	'''
	for line in open("user_item_part1.txt").readlines():
		userid = line.split()[0]
		itemid = line.split()[0]
		train_dic.setdefault(userid, {})
		train_dic[userid][itemid] = 1.0
	'''

	for line in open("data/test.txt").readlines():
		userid = line.split()[0]
		itemid = line.split()[1]
		score = float(line.split()[2])
		test_dic.setdefault(userid, {})
		test_dic[userid][itemid] = score
	print "--------read file complete---------"   
	return train_dic,test_dic

def get_Rating(train_dic,test_dic,outfile="predict_based_user.txt",similarity=sim_pearson):
	fp = open(outfile,"w")
	predict_dic = {}
	inAllnum = 0
	for userid in test_dic:
		for item in test_dic[userid]:
			print inAllnum
			if userid not in train_dic:
				rating = 0.0
			else:
				rating = getRating(train_dic, userid, item,20)
			predict_dic.setdefault(userid, {})    
			predict_dic[userid][item] = rating
			fp.write('%s\t%s\t%s\n'%(userid, item, rating))
			inAllnum = inAllnum +1
	fp.close()
	print "-------------Completed!!-----------",inAllnum
	return predict_dic

def evaluate_RMSE(predict_dic,test_dic):
	count = 0
	total = 0
	for user in test_dic:
		for item in test_dic[user]:
			count += 1
			total += (predict_dic[user][item]-test_dic[user][item])**2
	return sqrt(total/count)

def evaluate_map1(predict_dic,test_dic,recommend_num):
	new_test_dic = {}
	for user in test_dic.keys():
		item_list = []
		for item in test_dic[user]:
			if test_dic[user][item] >= 5:
				item_list.append(item)
		new_test_dic[user] = item_list

	new_predict_dic = {}
	for user in predict_dic.keys():
		a = predict_dic[user].items()
		a.sort(key=lambda x:x[1],reverse=True)
		item_list = [x[0] for x in a]
		if len(item_list) > recommend_num:
			new_predict_dic[user] = item_list[0:recommend_num]
		else:
			new_predict_dic[user] = item_list

	N = 0
	total_value = 0
	for userid in new_predict_dic:
		if len(new_test_dic[userid]) == 0:
			N += 1
		else:
			N += 1
			num = 0
			corrnum = 0
			fenmu = 0
			for itemid in new_predict_dic[userid]:
				num += 1 
				if itemid in new_test_dic[userid]:
					corrnum += 1
					fenmu += float(corrnum)/num
			if corrnum != 0:
				total_value += fenmu/corrnum

	print "total_user:" + str(N)
	print "precious:",total_value/N

def evaluate_RMSE(predict_dic,test_dic):
	count = 0
	total = 0
	for user in test_dic:
		for item in test_dic[user]:
			count += 1
			total += (predict_dic[user][item]-test_dic[user][item])**2
	print "precious:",sqrt(total/count)
	return sqrt(total/count)

def evaluate(predict_dic,recommend_num):
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
	for line in open("data/KDD_Track1_solution.csv").readlines():
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
		print mydic[userid],real_dic[userid]
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

if __name__ == '__main__':
	train_dic,test_dic = get_training_test()
	predict_dic = get_Rating(train_dic,test_dic)
	#evaluate_map1(predict_dic,test_dic,3)
	#evaluate_RMSE(predict_dic,test_dic)
	evaluate(predict_dic,3)
