import random
class LogisticRegression():
    def sigmoid(self, number):
        return 1 / (1 + 2.7182818284590 ** (-1 * number))

    def predict_for(self, liste, weights, bias):
        value = bias
        for i in range(len(weights)):
            value += weights[i] * liste[i]
        return self.sigmoid(value)

    def logistic_regression(self, train_dataset, epochs=10, lr=0.1):
        length = len(train_dataset[0]) - 1
        weights = [0.0 for _ in range(length)]
        bias = 0.0
        for _ in range(epochs):
            #random.shuffle(train_dataset)
            for row in train_dataset:
                x = row[:-1]
                y = row[-1]
                y_prediction = self.predict_for(x, weights, bias)
                error = y - y_prediction
                for k in range(length):
                    weights[k] += lr * error * x[k]
                bias += lr * error
        return weights, bias

    def evaluate_model(self, validation_dataset, weights, bias):
        y_true = [i[-1] for i in validation_dataset]
        predicted = [self.predict_for(j[:-1], weights, bias) for j in validation_dataset]
        correct = 0
        for i in range(len(y_true)):
            if y_true[i] == (1 if predicted[i] > 0.5 else 0):
                correct += 1
        return (correct / len(y_true)) * 100.0
    def predict(self,validation_dataset, weights, bias):
        predicted = [self.predict_for(j, weights, bias) for j in validation_dataset]
        liste=[]
        for i in predicted:
            if i>0.5:
                liste.append(1)
            else:
                liste.append(0)
        return liste
