
import random  
import math  

  
class SVD():  
    def __init__(self,allfile,trainfile,testfile,factorNum):  
        #all data file  
        self.allfile=allfile  
        #training set file  
        self.trainfile=trainfile  
        #testing set file  
        self.testfile=testfile  
        #get factor number  
        self.factorNum=factorNum  
        #get user number  
        self.userNum=self.getUserNum()  
        #get item number  
        self.itemNum=self.getItemNum()  
        #learning rate  
        self.learningRate=0.01
        #the regularization lambda  
        self.regularization=0.04
        #initialize the model and parameters  
        self.initModel2()  
    #get user number function  
    def getUserNum(self):  
        file=self.allfile  
        cnt=0  
        userSet=set()  
        for line in open(file):  
            user=line.split()[0].strip()  
            if user not in userSet:  
                userSet.add(user)  
                cnt+=1  
        return cnt  
    #get item number function  
    def getItemNum(self):  
        file=self.allfile  
        cnt=0  
        itemSet=set()  
        for line in open(file):  
            item=line.split()[1].strip()  
            if item not in itemSet:  
                itemSet.add(item)  
                cnt+=1  
        return cnt  
    #initialize all parameters
    def initModel2(self):
        file = self.allfile
        self.av = self.average(self.trainfile)
        self.bu = {}
        self.bi = {}
        temp=math.sqrt(self.factorNum)
        self.pu = {}
        self.qi = {}
        for line in open(file):
            user = line.split()[0].strip()
            item = line.split()[1].strip()
            if user not in self.bu:
                self.bu[user] = 0.0
            if item not in self.bi:
                self.bi[item] = 0.0
            if user not in self.pu:
                self.pu[user] = [(random.random()/temp) for i in range(self.factorNum)]
            if item not in self.qi:
                self.qi[item] = [(random.random()/temp) for i in range(self.factorNum)]
        print "Initialize end.The user number is:%d,item number is:%d,the average score is:%f" % (self.userNum,self.itemNum,self.av)

        '''
    def initModel(self):  
        self.av=self.average(self.trainfile)  
        self.bu=[0.0 for i in range(self.userNum)]  
        self.bi=[0.0 for i in range(self.itemNum)]  
        temp=math.sqrt(self.factorNum)  
        self.pu=[[(0.1*random.random()/temp) for i in range(self.factorNum)] for j in range(self.userNum)]  
        self.qi=[[0.1*random.random()/temp for i in range(self.factorNum)] for j in range(self.itemNum)]  
        print "Initialize end.The user number is:%d,item number is:%d,the average score is:%f" % (self.userNum,self.itemNum,self.av)
        '''  
     #train model    
    def train(self,iterTimes=30):  
        print "Beginning to train the model......"  
        trainfile=self.trainfile  
        preRmse=10000.0  
        for iter in range(iterTimes):  
            fi=open(trainfile,'r')  
            #read the training file  
            for line in fi:  
                content=line.split()  
                user=content[0].strip() 
                item=content[1].strip()  
                rating=float(content[2].strip())  
                #calculate the predict score  
                pscore=self.predictScore(self.av,self.bu[user],self.bi[item],self.pu[user],self.qi[item])  
                #the delta between the real score and the predict score  
                eui=rating-pscore  
                #update parameters bu and bi(user rating bais and item rating bais)  
                self.bu[user]+=self.learningRate*(eui-self.regularization*self.bu[user])  
                self.bi[item]+=self.learningRate*(eui-self.regularization*self.bi[item])  
                for k in range(self.factorNum):  
                    temp=self.pu[user][k]  
                    #update pu,qi
                    #print user
                    self.pu[user][k]+=self.learningRate*(eui*self.qi[item][k]-self.regularization*self.pu[user][k])  
                    self.qi[item][k]+=self.learningRate*(temp*eui-self.regularization*self.qi[item][k])  
                #print pscore,eui  
            #close the file  
            fi.close()  
            #calculate the current rmse  
            curRmse=self.test(self.av,self.bu,self.bi,self.pu,self.qi)  
            print "Iteration %d times,RMSE is : %f" % (iter+1,curRmse)  
            if curRmse>preRmse:  
                break  
            else:  
                preRmse=curRmse 
            #preRmse=curRmse   
        print "Iteration finished!"
        return self.av,self.bu,self.bi,self.pu,self.qi 
    #test on the test set and calculate the RMSE  
    def test(self,av,bu,bi,pu,qi):  
        testfile=self.trainfile  
        rmse=0.0  
        cnt=0  
        fi=open(testfile)  
        for line in fi:  
            cnt+=1  
            content=line.split()  
            user=content[0].strip() 
            item=content[1].strip()
            score=float(content[2].strip())  
            pscore=self.predictScore(av,bu[user],bi[item],pu[user],qi[item])  
            rmse+=math.pow(score-pscore,2)  
        fi.close()  
        return math.sqrt(rmse/cnt)

    def get_predict_dic(self,av,bu,bi,pu,qi):
        predict_dic = {}
        for line in open(self.testfile):
            user = line.split()[0]
            item = line.split()[1]
            pscore = self.predictScore(av,bu[user],bi[item],pu[user],qi[item])
            predict_dic.setdefault(user, {})
            predict_dic[user][item] = pscore
        return predict_dic

    #calculate the average rating in the training set  
    def average(self,filename):  
        result=0.0  
        cnt=0  
        for line in open(filename):  
            cnt+=1  
            score=float(line.split()[2].strip())  
            result+=score  
        return result/cnt  
    #calculate the inner product of two vectors  
    def innerProduct(self,v1,v2):  
        result=0.0  
        for i in range(len(v1)):  
            result+=v1[i]*v2[i]  
        return result  
    def predictScore(self,av,bu,bi,pu,qi):  
        pscore=av+bu+bi+self.innerProduct(pu,qi)  
        if pscore<-1:  
            pscore=1  
        if pscore>1:  
            pscore=1  
        return pscore  


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

def get_ratings(trainfile,testfile,allfile):
    of = open(allfile,"w")
    for line in open(trainfile).readlines():
        of.write(line)
    for line in open(testfile).readlines():
        of.write(line)


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

      
if __name__=='__main__':
    get_ratings("data/train.txt","data/test.txt","ratings.txt")
    s = SVD("ratings.txt","data/train.txt","data/test.txt",60)
    print s.userNum,s.itemNum  
    print s.average("data/train.txt")
    print len(s.pu),len(s.qi) 
    av,bu,bi,pu,qi = s.train()
    predict_dic = s.get_predict_dic(av,bu,bi,pu,qi)
    evaluate(predict_dic,3)
    