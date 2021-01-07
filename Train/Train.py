import pandas as pd
from snownlp import SnowNLP
from snownlp import sentiment

def train_model():
    data= pd.read_csv(r"./Train/weibo_senti_100k/weibo_senti_100k.csv",header=0)
    data = data.sample(frac = 1)
    train = data.iloc[:110000,[0,1]]
    test = data.iloc[110000:,[0,1]]
    train_neg = train.iloc[:, 1][train.label == 0]
    train_pos = train.iloc[:, 1][train.label == 1]
    train_neg.to_csv(r"./Train/weibo_senti_100k/neg.csv", index=0, header=0)
    train_pos.to_csv(r"./Train/weibo_senti_100k/pos.csv", index=0, header=0)
    test.to_csv(r"./Train/weibo_senti_100k/test.csv",index=0,columns=['label','review'])
    sentiment.train(r'./Train/weibo_senti_100k/neg.csv',r'./Train/weibo_senti_100k/pos.csv')
    sentiment.save(r'C:/Users/RA1LGUN/Anaconda3/Lib/site-packages/snownlp/sentiment/newsentiment.marshal')

def test_model():
    test=pd.read_csv(r"./Train/weibo_senti_100k/test.csv")
    review_list=[review for review in test['review']]
    label_list=[label for label in test['label']]
    list_test=[(label,review) for label,review in list(zip(label_list,review_list)) if type(review)!=float]

    for j in list_test:
        print(j[1],j[0],SnowNLP(j[1]).sentiments)


    senti=[SnowNLP(review).sentiments for label,review in list_test]

    newsenti=[]
    for i in senti:  #预测结果为pos的概率,大于0.6我们认定为积极评价
        if(i>=0.6):
            newsenti.append(1)
        else:
            newsenti.append(0)

    counts=0
    for i in range(len(list_test)):
            if(newsenti[i]==list_test[i][0]):
                counts+=1

    accuracy=float(counts)/float(len(list_test))
    print("准确率为:%.2f" %accuracy)