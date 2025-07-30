import random
class K_Means:
    def euclidian_distance(self,list1,list2):
        return sum((a-b)**2 for a,b in zip(list1,list2))**0.5
    def find_new_centroids(self,cluster):
        length=len(cluster)
        return [sum(i)/length for i in zip(*cluster)]

    def k_means(self,data,k,max_iteration):
        centroids=random.sample(data,k)
        for iteration in range(max_iteration):
            clusters = [[] for i in range(k)]
            for data_ in data:
                distances=[self.euclidian_distance(data_,centroid) for centroid in centroids]
                distance_index=distances.index(min(distances))
                clusters[distance_index].append(data_)
            new_centroids=[self.find_new_centroids(cluster) for cluster in clusters]
            if new_centroids==centroids:
                break
            centroids=new_centroids
        return centroids,clusters

    def predict(self,data,centroids):
        distance_index=[]
        for data_ in data:
            distances=[self.euclidian_distance(data_,centroid) for centroid in centroids]
            distance_index.append(distances.index(min(distances)))
        return distance_index