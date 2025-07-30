
class NaiveBayes:
    def __init__(self):
        pass
    def mean(self,array):
        return sum(array)/len(array)
    def stdev(self,array):
        average=self.mean(array)
        variance= sum((average-x)**2 for x in array)/(len(array)-1)
        return variance**0.5
    def gaussian_probability(self,x,mean,stdev):
        if stdev==0:
            return 1
        number=-1*((x-mean)**2)/(2*stdev**2)
        exponent=2.7182818284590**number
        #return 1/((((2*3.1415926535)**0.5)*stdev)*exponent)
        return exponent/(stdev*((2*3.1415926535)**0.5))
    def seperate_by_class(self,dataset):
        seperated={}
        for row in dataset:
            label=row[-1]
            if label not in seperated:
                seperated[label]=[]
            seperated[label].append(row[:-1])
        return seperated
        # {0:[[1,2,3],[4,5,6]];1:[[7,8,9],[10,11,12]]}
    def seperate_features(self,rows):
        number_of_features=len(rows[0])
        features=[[] for i in range(number_of_features)]
        for row in rows:
            for j in range(number_of_features):
                features[j].append(row[j])
        return features
        # features=[[1,4],[2,5],[3,6]]

    def naive_bayes(self,dataset):
        separated=self.seperate_by_class(dataset)
        summaries={}
        for class_value,rows in separated.items():
            features=self.seperate_features(rows)
            summaries[class_value]=[]
            for features in features:
                summaries[class_value].append((self.mean(features),self.stdev(features)))
        return summaries
        # {0:[(1,2),(3,4),(5,6)];1:[(7,8),(9,10),(11,12)]]
    def calculate_class_probabilities(self,summaries,input_vector):
        probabilities={}
        for class_value,class_summaries in summaries.items():
            probabilities[class_value]=1
            for i in range(len(class_summaries)):
                mean_x,stdev_x=class_summaries[i]
                x=input_vector[i]
                prob=self.gaussian_probability(x,mean_x,stdev_x)
                probabilities[class_value]*=prob
        return probabilities
        # {0: 6.649324552511129e-13, 1: 1.896816783869607e-13}
    def predict(self,summaries,test_data):
        array=[]
        for input_vector in test_data:
            probabilities=self.calculate_class_probabilities(summaries,input_vector)
            best_label=None
            best_prob=-1
            for class_value,probabilitie in probabilities.items():
                if probabilitie>best_prob:
                    best_prob=probabilitie
                    best_label=class_value
            array.append(best_label)
        return array







