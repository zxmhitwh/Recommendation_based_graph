#coding:utf-8
import networkx as nx
import similarity as sim
import MySQLdb

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
	for line in open("test222.txt").readlines():
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
	for line in open("../example2/item.txt").readlines():
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

def get_items(simfile,scorethreald):
	item_edges = set()
	for line in open(simfile).readlines():
		item1 = line.split()[0]
		item2 = line.split()[1]
		score = float(line.split()[2])
		if score >= scorethreald:
			item_edges.add((item1,item2))
			item_edges.add((item2,item1))
	#for line in open("item_item_part1.txt").readlines():
	#	item_edges.add((line.split()[1],line.split()[0]))
			
	return item_edges

def graph_pagerank(recommend_num=3):
	mygraph = nx.DiGraph()
	predict_dic = get_predict()
	nodes,pre_recommend_dic = get_node(predict_dic)
	mygraph.add_nodes_from(nodes)
	user_edges = get_sns()
	item_edges = get_items("sim_cos_score111",0.3)
	print len(user_edges),len(item_edges)
	graph_edge_set = set()
	num = 0
	for user1,user2 in user_edges:
		num += 1
		#print "user"+ str(num)
		user1_node = []
		user2_node = []
		for node in nodes:
			if node[0] == user1:
				user1_node.append(node)
			if node[0] == user2:
				user2_node.append(node)
		for node1 in user1_node:
			for node2 in user2_node:
				graph_edge_set.add((node1,node2))
	num = 0
	for item1,item2 in item_edges:
		num += 1
		#print "item" + str(num)
		item1_node = []
		item2_node = []
		for node in nodes:
			if node[1] == item1:
				item1_node.append(node)
			if node[1] == item2:
				item2_node.append(node)
		for node1 in item1_node:
			for node2 in item2_node:
				graph_edge_set.add((node1,node2))
			
	print "graph_edge_set:",len(graph_edge_set)
	mygraph.add_edges_from(graph_edge_set)
	pr = nx.pagerank(mygraph)
	return pr,pre_recommend_dic,nodes

def compute_predict(pr,pre_recommend_dic,nodes):
	new_pr = {}
	for key in pr.keys():
		new_pr[key] = pr[key]+pre_recommend_dic[key[0]][key[1]]
	print 333
	#test_dic = get_testdic()
	predict_dic = {}
	for user in pre_recommend_dic.keys():
		mylist = []
		a = []
		for node in mygraph.nodes():
			if node[0] == user:
				a.append((node[1],new_pr[node]))
		a.sort(key=lambda x:x[1],reverse=True)
		mylist = [x[0] for x in a]
		if len(mylist) > recommend_num:
			predict_dic[user] = mylist[0:recommend_num]
		else:
			predict_dic[user] = mylist
	return predict_dic

def get_best_factor(pagerank,pre_recommend_dic,nodes,recommend_num):

	new_pr = {}
	for i in range(11):
		print i
		for key in pagerank.keys():
			new_pr[key] = i*pagerank[key]+(10-i)*pre_recommend_dic[key[0]][key[1]]
		#test_dic = get_testdic()
		predict_dic = {}
		for user in pre_recommend_dic.keys():
			mylist = []
			a = []
			for node in nodes:
				if node[0] == user:
					a.append((node[1],new_pr[node]))
			a.sort(key=lambda x:x[1],reverse=True)
			mylist = [x[0] for x in a]
			if len(mylist) > recommend_num:
				predict_dic[user] = mylist[0:recommend_num]
			else:
				predict_dic[user] = mylist
		evaluate(predict_dic)


def evaluate(predict_dic):
    mydic = predict_dic

    real_dic = {}
    for line in open("../example2/KDD_Track1_solution.csv").readlines():
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


if __name__ == '__main__':
	
	#item_sim_cos("test_111.txt","sim_cos_score111")
	pagerank,pre_recommend_dic,nodes = graph_pagerank()
	get_best_factor(pagerank,pre_recommend_dic,nodes,3)



