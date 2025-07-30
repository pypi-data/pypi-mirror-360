class Metrics:
    def r2_score(self,y_true,y_predict):
        mean_y_true=sum(y_true)/len(y_true)
        ss_total=sum((y_true[i] - mean_y_true)**2 for i in range(len(y_true)))
        ss_res=sum((y_true[i] - y_predict[i])**2 for i in range(len(y_true)))
        return 1 - (ss_res/ss_total)
    def mean_squared_error(self,y_true,y_predict):
        return sum(((y_true[i] - y_predict[i])**2 for i in range(len(y_true))))/len(y_true)
    def root_mean_squared_error(self,y_true,y_predict):
        return self.mean_squared_error(y_true,y_predict)**0.5
    def mean_absolute_error(self,y_true,y_predict):
        return sum((abs((y_true[i] - y_predict[i])) for i in range(len(y_true)))) / len(y_true)
    def accuracy(self,y_true,y_predict):
        length=len(y_true)
        correct=0.0
        for i in range(length):
            if y_true[i]==y_predict[i]:
                correct+=1
        return (correct/float(length))*100.0
    def confusion_matrix_counts(self, y_true, y_pred,svm_=False):
        true_positive,false_positive,true_negative,false_negative=0,0,0,0
        if svm_==False:
            for yt, yp in zip(y_true, y_pred):
                if yt == 1 and yp == 1:
                    true_positive += 1
                elif yt == 0 and yp == 0:
                    true_negative += 1
                elif yt == 0 and yp == 1:
                    false_positive += 1
                elif yt == 1 and yp == 0:
                    false_negative += 1
        else:
            for yt, yp in zip(y_true, y_pred):
                if yt == 1 and yp == 1:
                    true_positive += 1
                elif yt == -1 and yp == -1:
                    true_negative += 1
                elif yt == -1 and yp == 1:
                    false_positive += 1
                elif yt == 1 and yp == -1:
                    false_negative += 1
        return true_positive,false_positive,true_negative,false_negative
    def precision(self, y_true, y_pred,svm_=False):
        true_positive, false_positive, _, _ = self.confusion_matrix_counts(y_true, y_pred,svm_)
        if true_positive + false_positive == 0:
            return 0.0
        return true_positive / (true_positive + false_positive)
    def recall(self, y_true, y_pred,svm_=False):
        true_positive,_,_,false_negative = self.confusion_matrix_counts(y_true, y_pred,svm_)
        if true_positive + false_negative == 0:
            return 0.0
        return true_positive / (true_positive + false_negative)
    def f1_score(self, y_true, y_pred,svm_=False):
        precision = self.precision(y_true, y_pred,svm_)
        recall = self.recall(y_true, y_pred,svm_)
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)