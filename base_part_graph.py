#coding:utf-8
import networkx as nx
import similarity as sim
import MySQLdb
from datetime import datetime
import threading

def get_node(predict_dic,pre_recommend_num=10):
	nodes = []
	pre_recommend_dic = {}
	for user in predict_dic:
		pre_recommend_dic[user] = {}
		mylist = []
		a = predict_dic[user].items()
		a.sort(key=lambda x:x[1],reverse=True)
		if len(a) > pre_recommend_num:
			for item,predict_score in a[0:pre_recommend_num]:
				nodes.append((user,item))
				pre_recommend_dic[user][item] = predict_score
		else:
			for item,predict_score in a:
				nodes.append((user,item))
				pre_recommend_dic[user][item] = predict_score			
	return nodes,pre_recommend_dic


####读文件获取图中的结点

def get_testdic():
	test_dic = {}
	for line in open("data/test.txt").readlines():
		test_dic.setdefault(line.split()[0], {})
		test_dic[line.split()[0]][line.split()[1]] = float(line.split()[2])
	return test_dic
###获取测试集中真实的用户对项目评分

def get_predict():
	predict_dic = {}
	for line in open("SVD/predict_based_SVD_1").readlines():
		predict_dic.setdefault(line.split()[0], {})
		predict_dic[line.split()[0]][line.split()[1]] = float(line.split()[2])
	return predict_dic
###预测的测试集中用户对项目的预测评分

def item_sim_cos(testfile,simfile):
	item_set = set()	
	for line in open(testfile).readlines():
		item_set.add(line.split()[1])

	outfile = open(simfile,"w")
	keywords_set = set()
	user_keywords = {}
	for line in open("data/item.txt").readlines():
		if line.split()[0] in item_set:
			keywords = line.split()[2].split(";")
			user_keywords[line.split()[0]] = keywords
			keywords_set =  keywords_set | set(keywords)
	keywords_set = list(keywords_set)

	for item in user_keywords.keys():
		item_vector = [0 for x in range(len(keywords_set))]
		for word in user_keywords[item]:
			item_vector[keywords_set.index(word)] = 1
		user_keywords[item] = item_vector
	pairwise = set()	
	num = 0
	item_set = list(item_set)
	for item1 in item_set:
		for item2 in item_set:
			if item1 != item2 and (item2,item1) not in pairwise:
				num += 1
				print "pairwise",num
				pairwise.add((item1,item2))
				score = sim.sim_cos(user_keywords[item1],user_keywords[item2])
				outfile.write(item1+"\t"+item2+"\t"+str(score)+"\n")
	print len(pairwise)

def get_sns():
	user_edges = set()
	for line in open("222").readlines():
		user_edges.add((line.split()[1],line.split()[0]))
	return user_edges
###得到用户之间的边，即存在好友关系的边

def get_items(simfile,scorethreald,sim_result_file):
	item_edges = set()
	outfile = open(sim_result_file,"w")
	for line in open(simfile).readlines():
		item1 = line.split()[0]
		item2 = line.split()[1]
		score = float(line.split()[2])
		if score >= scorethreald:
			outfile.write(item1+"\t"+item2+"\n")
			
	return item_edges

def find_relate_userset(user):
	user_set = set()
	user_bian = set()
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123456',db ='mygraph')
	cur = conn.cursor()
	mysql1 = "select user2 from useruser where user1 =" + user
	mysql2 = "select user1 from useruser where user2 =" + user
	cur.execute(mysql1)
	resultlist = cur.fetchall()
	for each in resultlist:
		user_set.add(each[0].strip())
		user_bian.add((user,each[0].strip()))
	cur.execute(mysql2)
	resultlist = cur.fetchall()
	for each in resultlist:
		user_set.add(each[0].strip())
		user_bian.add((each[0].strip(),user))
	cur.close()
	conn.commit()
	conn.close()
	user_set.add(user)
	return user_set,user_bian

def find_relate_itemset(items):
	item_set = set()
	item_bian = set()
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123456',db ='mygraph')
	cur = conn.cursor()
	for item in items:
		mysql1 = "select item2 from itemitem where item1 =" + item
		mysql2 = "select item1 from itemitem where item2 =" + item
		cur.execute(mysql1)
		resultlist = cur.fetchall()
		for each in resultlist:
			item_set.add(each[0].strip())
			item_bian.add((item,each[0].strip()))
		cur.execute(mysql2)
		resultlist = cur.fetchall()
		for each in resultlist:
			item_set.add(each[0].strip())
			item_bian.add((each[0].strip(),item))
		item_set.add(item)
	cur.close()
	conn.commit()
	conn.close()
	return item_set,item_bian

def find_n_relate_userset(user,depth):
	user_set = set()
	user_bian = set()
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123456',db ='mygraph')
	cur = conn.cursor()
	user_set.add(user)
	user_extend = set()
	user_extend.add(user)
	for i in range(depth):
		this_user_set = set()
		for u in user_extend:
			mysql1 = "select user2 from useruser where user1 =" + u
			mysql2 = "select user1 from useruser where user2 =" + u
			cur.execute(mysql1)
			resultlist = cur.fetchall()
			for each in resultlist:
				this_user_set.add(each[0].strip())
				user_bian.add((user,each[0].strip()))
			cur.execute(mysql2)
			resultlist = cur.fetchall()
			for each in resultlist:
				this_user_set.add(each[0].strip())
				user_bian.add((each[0].strip(),user))
		user_set = user_set | this_user_set
		user_extend = this_user_set
	cur.close()
	conn.commit()
	conn.close()
	return user_set,user_bian

def find_n_relate_itemset(items,depth):
	item_set = set()
	item_bian = set()
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123456',db ='mygraph')
	cur = conn.cursor()
	for item in items:
		item_set.add(item)
		item_extend = set()
		item_extend.add(item)
		for i in range(depth):
			this_item_set = set()
			for it in item_extend:
				mysql1 = "select item2 from itemitem where item1 =" + it
				mysql2 = "select item1 from itemitem where item2 =" + it
				cur.execute(mysql1)
				resultlist = cur.fetchall()
				for each in resultlist:
					this_item_set.add(each[0].strip())
					item_bian.add((item,each[0].strip()))
				cur.execute(mysql2)
				resultlist = cur.fetchall()
				for each in resultlist:
					this_item_set.add(each[0].strip())
					item_bian.add((each[0].strip(),item))
			item_set = item_set | this_item_set
			item_extend = this_item_set
	cur.close()
	conn.commit()
	conn.close()
	return item_set,item_bian


def compute_part_graph():
	final_predict = {}
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123456',db ='mygraph')
	cur = conn.cursor()
	predict_dic = get_predict()
	nodes,pre_recommend_dic = get_node(predict_dic)
	num = 0
	for user in pre_recommend_dic:
		starttime = datetime.now()
		items = pre_recommend_dic[user].keys()
		#user_set,user_bian = find_relate_userset(user)
		#item_set,item_bian = find_relate_itemset(items)
		user_set,user_bian = find_n_relate_userset(user,2)
		item_set,item_bian = find_n_relate_itemset(items,2)
		print len(user_bian),len(item_bian)
		user_edges = set()
		item_edges = set()
		current_edges = set()
		for user1,user2 in user_bian:
			mysql1 = "select user,item from nodes where user =" + user1
			mysql2 = "select user,item from nodes where user =" + user2
			cur.execute(mysql1)
			resultlist1 = cur.fetchall()
			cur.execute(mysql2)
			resultlist2 = cur.fetchall()
			for user_x,item_x in resultlist1:
				for user_y,item_y in resultlist2:
					current_edges.add(((user_x.strip(),item_x.strip()),(user_y.strip(),item_y.strip())))
		for item1,item2 in item_bian:
			mysql1 = "select user,item from nodes where item =" + item1
			mysql2 = "select user,item from nodes where item =" + item2
			cur.execute(mysql1)
			resultlist1 = cur.fetchall()
			cur.execute(mysql2)
			resultlist2 = cur.fetchall()
			for user_x,item_x in resultlist1:
				for user_y,item_y in resultlist2:
					current_edges.add(((user_x.strip(),item_x.strip()),(user_y.strip(),item_y.strip())))
					current_edges.add(((user_y.strip(),item_y.strip()),(user_x.strip(),item_x.strip())))
		print "current_edges:",len(current_edges)
		mygraph = nx.DiGraph()
		mygraph.add_edges_from(current_edges)
		pr = nx.pagerank(mygraph)
		a = []
		for item in items:
			a.append((item,pr[(user,item)]))
		a.sort(key=lambda x:x[1],reverse=True)
		mylist = [x[0] for x in a]
		if len(mylist) > 3:
			final_predict[user] = mylist[0:3]
		else:
			final_predict[user] = mylist
		endtime = datetime.now()
		print "user",num,endtime-starttime
		num += 1
	return final_predict

def evaluate(predict_dic):
    mydic = predict_dic

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


def test():
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123456',db ='mygraph')
	cur = conn.cursor()
	mysql = "select user,item from nodes where user = 576357"
	cur.execute(mysql)
	resultlist = cur.fetchall()
	print resultlist




if __name__ == '__main__':
	#get_items("sim_cos_score111",0.3,"sim_file_0.3")
	#compute_part_graph()
	#predict_dic = get_predict()
	#nodes,pre_recommend_dic = get_node(predict_dic)
	final_predict = compute_part_graph()
	evaluate(final_predict)