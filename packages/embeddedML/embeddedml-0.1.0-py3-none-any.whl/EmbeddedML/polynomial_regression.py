class PolynomialRegression:
    def transpoze(self,X):
        X_transpoze=[]
        row=len(X)
        col=len(X[0])
        for i in range(col):
            X_=[]
            for j in range(row):
                X_.append(X[j][i])
            X_transpoze.append(X_)
        return X_transpoze
    def matrix(self,X,XX):
        row=len(X)
        col=len(X[0])
        col2=len(XX[0])
        X_matrix=[]
        for i in range(row):
            X_=[]
            for j in range(col2):
                sum = 0
                for k in range(col):
                    sum+=X[i][k]*XX[k][j]
                X_.append(sum)
            X_matrix.append(X_)
        return X_matrix
    def inverse(self,X):
        X_copy=[]
        I = []
        row=len(X)
        col=len(X[0])
        for i in range(row):
            X_=[]
            I_ = []
            for j in range(col):
                X_.append(X[i][j])
                if i==j:
                    I_.append(1)
                else:
                    I_.append(0)
            X_copy.append(X_)
            I.append(I_)
        for i in range(row):
            if X_copy[i][i]!=0:
                factor=X_copy[i][i]
                for j in range(row):
                    X_copy[i][j]/=factor
                    I[i][j]/=factor
                for k in range(row):
                    if k!=i:
                        factor=X_copy[k][i]
                        for p in range(row):
                            X_copy[k][p]-=factor*X_copy[i][p]
                            I[k][p] -= factor * I[i][p]
        return I
    def poly(self, X, degree):
        XX = []
        row = len(X)
        col = len(X[0])
        for i in range(row):
            XXX = [1]
            for j in range(1, col):  # 0. index bias, tekrar eklemeyelim
                for k in range(1, degree + 1):
                    XXX.append(X[i][j] ** k)
            for j in range(1, col):
                for k in range(j + 1, col):
                    XXX.append(X[i][j] * X[i][k])
            XX.append(XXX)
        return XX
    def polynomial_regression(self, X, y,degree=2):
        X_poly = self.poly(X, degree)
        y = [[yi] for yi in y]
        X_transpose = self.transpoze(X_poly)
        XTX = self.matrix(X_transpose, X_poly)
        XTX_inv = self.inverse(XTX)
        XTY = self.matrix(X_transpose, y)
        coefficients = self.matrix(XTX_inv, XTY)
        return coefficients
    def predict(self, X, coefficients,degree=2):
        X_poly = self.poly(X, degree)
        predictions = []
        for row in X_poly:
            y_pred = 0
            for xi, w in zip(row, coefficients):
                y_pred += xi * w[0]
            predictions.append(y_pred)
        return predictions