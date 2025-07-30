class SimpleLinearRegression:
    def linear_regression(self,X,y):
        length=len(X)
        sum_x=sum(X)
        sum_y=sum(y)
        sum_xx=sum([x_ * x_ for x_ in X])
        sum_xy=sum([X[i] * y[i] for i in range(length)])
        m=(length * sum_xy - sum_x * sum_y) / (length * sum_xx - sum_x ** 2)
        n=(sum_y - m * sum_x)/length
        return m , n
    def predict(self,m,n,X):
        return [(m * x_ + n) for x_ in X]

