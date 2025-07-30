class MultipleLinearRegression:
    def transpoze(self,X):
        row=len(X)
        col=len(X[0])
        X_transpoze=[]
        for i in range(col):
            X_=[]
            for j in range(row):
                X_.append(X[j][i])
            X_transpoze.append(X_)
        return X_transpoze
    def matrix(self,X,X_):
        row=len(X)
        col=len(X[0])
        yeni=[]
        for p in range(row):
            yeni2=[]
            for i in range(len(X_[0])):
                sum = 0
                for z in range(col):
                    value=X[p][z]*X_[z][i]
                    sum+=value
                yeni2.append(sum)
            yeni.append(yeni2)
        return yeni
    def inverse(self,X):
        number=len(X)
        I=[]
        XX=[]
        for i in range(number):
            XX__=[]
            for j in range(number):
                XX__.append(X[i][j])
            XX.append(XX__)
        for i in range(number):
            yeni = []
            for j in range(number):
                if i==j:
                    yeni.append(1)
                else:
                    yeni.append(0)
            I.append(yeni)
        for i in range(number):
            factor=XX[i][i]
            if factor!=0:
                for j in range(number):
                    XX[i][j]/=factor
                    I[i][j]/=factor
                for k in range(number):
                    if k!=i:
                        factor=XX[k][i]
                        for j in range(number):
                            XX[k][j]-=factor*XX[i][j]
                            I[k][j]-=factor*I[i][j]
        return I
    def multiple_linear_regression(self,X,y):
        X_transpoze=self.transpoze(X)
        X_matrix_multication=self.matrix(X_transpoze,X)
        X_y_matrix_multicaiton=self.matrix(X_transpoze,[[yi] for yi in y])
        X_matrix_multication_inverse=self.inverse(X_matrix_multication)
        X_matrix_multication_inverse_y=self.matrix(X_matrix_multication_inverse,X_y_matrix_multicaiton)
        return  X_matrix_multication_inverse_y
    def predict(self,X,B):
        y_pred=[]
        values=self.matrix(X,B)
        for value in values:
            y_pred.append(value[0])
        return y_pred