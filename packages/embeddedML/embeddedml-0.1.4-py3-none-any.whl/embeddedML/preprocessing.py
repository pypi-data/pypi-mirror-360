import random
class Preprocessing:
    def min_max_scaler(self,liste):
        length2=len(liste[0])
        for i in range(length2-1):# length2-1
            col=[j[i] for j in liste]
            min_col,max_col=min(col),max(col)
            if max_col==min_col:
                continue
            for k in liste:
                k[i]=(k[i]-min_col)/(max_col-min_col)
        return liste
    def standard_scaler(self, liste):
        length2 = len(liste[0])
        for i in range(length2-1):
            col = [j[i] for j in liste]
            mean = sum(col) / len(col)
            std = (sum((x - mean) ** 2 for x in col) / len(col)) ** 0.5
            if std == 0:
                continue
            for k in liste:
                k[i] = (k[i] - mean) / std
        return liste
    def poly_for_svm(self,data,degree):
        col=len(data[0])
        row=len(data)
        XX=[]
        for i in range(row):
            X=[]
            for j in range(col):
                for k in range(1,degree+1):
                    X.append(data[i][j]**k)
            for j in range(col):
                for p in range(col):
                    if j!=p:
                        X.append(data[i][j]*data[i][p])
            XX.append(X)
        return XX
    def label_transformation(self,labels):
        return [1 if int(label)==1 else -1 for label in labels]
    def train_validation_split(self,data,train_rate=0.7,is_shuffle=True):
        length=len(data)
        if is_shuffle==True:
            random.shuffle(data)
        train_dataset=data[:int(length*train_rate)]
        validation_dataset=data[int(length*train_rate):]
        return train_dataset,validation_dataset
    def get_true_ones(self,dataset):
        return [i[-1] for i in dataset]
