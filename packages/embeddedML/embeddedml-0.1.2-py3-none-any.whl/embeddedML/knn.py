class KNN:
    def euclidian_distance(self,row1,row2):
        distance=0.0
        length=len(row1)
        for i in range(length-1):
            distance+=(row1[i]-row2[i])**2
        return distance**0.5
    def knn(self,train_dataset,row,k):
        distances=[]
        for train_row in train_dataset:
            distance=self.euclidian_distance(train_row,row)
            distances.append((train_row,distance))
        distances.sort(key=lambda x:x[1])
        neighbours=[]
        for i in range(k):
            neighbours.append(distances[i][0])
        return neighbours
    def predict(self,train_dataset,dataset,k):
        y_precict=[]
        for row in dataset:
            neighbours=self.knn(train_dataset,row,k)
            values=[i[-1] for i in neighbours]
            zero=0.0
            one=0.0
            for j in range(k):
                if values[j]==1.0:
                    one=one+1.0
                else:
                    zero=zero+1.0
            if one>zero:
                y_precict.append(1.00)
            else:
                y_precict.append(0.00)
        return y_precict