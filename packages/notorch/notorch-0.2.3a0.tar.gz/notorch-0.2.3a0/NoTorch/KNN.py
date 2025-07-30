import numpy as np
from collections import defaultdict

class KNN():
    """
    K-Nearest Neighbors (KNN) classifier.

    Parameters
    ----------
    n_neighbors : int
        The number of nearest neighbors to use for classification.
    """
    
    def __init__(self, n_neighbors):
        self.n_neighbors = n_neighbors
        self.data = []

    def fit(self, cords, label):
        if(len(cords) != len(label)):
            print("Error: Labels vector and cords vector are not the same length")

        for i in range(len(cords)):
            self.data.append((cords[i], label[i]))
    
    def predict(self, predict):
        results = []

        for test in predict:
            vec = []

            for entry, label in self.data:
                distance = self.euclidean_distance(test, entry)
                vec.append((distance, label))

            vec.sort(key=lambda x: x[0])

            label_counts = defaultdict(int)
            for i in range(self.n_neighbors):
                _, label = vec[i]
                label_counts[label] += 1

            predicted_label = max(label_counts.items(), key=lambda x: x[1])[0]
            results.append(predicted_label)

        return results
            

    def euclidean_distance(self, point1, point2):
        return np.linalg.norm(np.array(point1) - np.array(point2))