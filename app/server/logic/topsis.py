import numpy as np
import pandas as pd

class TOPSIS:
    def __init__(self, decision_matrix, weights, criteria_types):
        """
        decision_matrix: Ma trận quyết định (m x n)
        weights: Trọng số các tiêu chí (n,)
        criteria_types: List loại tiêu chí ['benefit', 'cost', ...]
        """
        self.matrix = np.array(decision_matrix)
        self.weights = np.array(weights)
        self.criteria_types = criteria_types
        self.normalized_matrix = None
        self.weighted_matrix = None
        
    def vector_normalization(self):
        """Chuẩn hóa vector"""
        squared = self.matrix ** 2
        sum_squared = np.sum(squared, axis=0)
        self.normalized_matrix = self.matrix / np.sqrt(sum_squared)
        return self.normalized_matrix
    
    def apply_weights(self):
        """Áp dụng trọng số"""
        self.weighted_matrix = self.normalized_matrix * self.weights
        return self.weighted_matrix
    
    def find_ideal_solutions(self):
        """Tìm giải pháp lý tưởng tốt nhất và xấu nhất"""
        ideal_best = []
        ideal_worst = []
        
        for j, criterion_type in enumerate(self.criteria_types):
            column = self.weighted_matrix[:, j]
            
            if criterion_type == 'benefit':
                ideal_best.append(np.max(column))
                ideal_worst.append(np.min(column))
            else:  # cost criterion
                ideal_best.append(np.min(column))
                ideal_worst.append(np.max(column))
                
        return np.array(ideal_best), np.array(ideal_worst)
    
    def find_ideal_solutions_raw(self):
        """Tìm giải pháp lý tưởng tốt nhất và xấu nhất"""
        ideal_best = []
        ideal_worst = []
        
        for j, criterion_type in enumerate(self.criteria_types):
            column = self.matrix[:, j]
            
            if criterion_type == 'benefit':
                ideal_best.append(np.max(column))
                ideal_worst.append(np.min(column))
            else:  # cost criterion
                ideal_best.append(np.min(column))
                ideal_worst.append(np.max(column))
                
        return np.array(ideal_best), np.array(ideal_worst)
    
    def calculate_distances(self, ideal_best, ideal_worst):
        """Tính khoảng cách tới các giải pháp lý tưởng"""
        n_alternatives = self.weighted_matrix.shape[0]
        distances_best = np.zeros(n_alternatives)
        distances_worst = np.zeros(n_alternatives)
        
        for i in range(n_alternatives):
            distances_best[i] = np.sqrt(np.sum(
                (self.weighted_matrix[i] - ideal_best) ** 2
            ))
            distances_worst[i] = np.sqrt(np.sum(
                (self.weighted_matrix[i] - ideal_worst) ** 2
            ))
            
        return distances_best, distances_worst
    
    def calculate_scores(self, distances_best, distances_worst):
        """Tính điểm TOPSIS"""
        return distances_worst / (distances_best + distances_worst)
    
    def solve(self):
        """Thực hiện toàn bộ quy trình TOPSIS"""
        self.vector_normalization()
        
        self.apply_weights()
        
        ideal_best, ideal_worst = self.find_ideal_solutions()
        
        dist_best, dist_worst = self.calculate_distances(ideal_best, ideal_worst)
        
        scores = self.calculate_scores(dist_best, dist_worst)
        
        return scores
#
# # Ví dụ sử dụng
# if __name__ == "__main__":
#     # Dữ liệu đầu vào
#     decision_matrix = np.array([
#         [250, 16, 12, 5],   # Laptop A: giá, RAM, SSD, trọng lượng
#         [200, 16, 8, 3],    # Laptop B
#         [300, 32, 16, 4],   # Laptop C
#         [275, 32, 8, 2]     # Laptop D
#     ])
#
#     # Trọng số: [giá, RAM, SSD, trọng lượng]
#     weights = [0.3, 0.25, 0.25, 0.2]
#
#     # Loại tiêu chí: 'cost' cho giá và trọng lượng, 'benefit' cho RAM và SSD
#     criteria_types = ['cost', 'benefit', 'benefit', 'cost']
#
#     # Thực hiện TOPSIS
#     topsis = TOPSIS(decision_matrix, weights, criteria_types)
#     scores = topsis.solve()
#
#     # Kết quả
#     alternatives = ['Laptop A', 'Laptop B', 'Laptop C', 'Laptop D']
#     results = pd.DataFrame({
#         'Alternative': alternatives,
#         'TOPSIS Score': scores,
#         'Rank': np.argsort(scores)[::-1] + 1
#     })
#
#     print(results.sort_values('Rank'))