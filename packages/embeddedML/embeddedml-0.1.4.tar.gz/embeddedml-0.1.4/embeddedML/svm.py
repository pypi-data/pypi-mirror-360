class SVM:
    def dot_product(self,data,weigths):
        return sum(data_*weigth_ for data_,weigth_ in zip(data,weigths))

    def svm(self,train_data,label,epochs,learning_rate,lambda_param,beta):
        number_of_features=len(train_data[0])
        weigths=[0.0]*number_of_features
        bias=0.0
        momentum_weights=[0.0]*number_of_features
        momentum_bias=0.0
        for epoch in range(epochs):
            for id, data in enumerate(train_data):
                value=label[id]*(self.dot_product(data,weigths)+bias)
                if value>=1:
                    gradiant_weigths=[2*lambda_param*weight for weight in weigths]
                    gradiant_bias=0.0
                else:
                    gradiant_weigths=[2*lambda_param*weight -label[id]*datam for datam,weight in zip(data,weigths)]
                    gradiant_bias = -label[id]
                momentum_weights=[beta*momentum_weight + (1-beta)*gradiant_weigth for momentum_weight,gradiant_weigth in zip(momentum_weights,gradiant_weigths)]
                momentum_bias=beta*momentum_bias+(1-beta)*gradiant_bias
                weigths=[weigth-learning_rate*momentum_weight for weigth,momentum_weight in zip(weigths,momentum_weights)]
                bias=bias-learning_rate*momentum_bias
        return weigths,bias

    def predict(self,datas,weigths,bias):
        return [1 if (self.dot_product(data,weigths)+bias>=0) else -1 for data in datas]



