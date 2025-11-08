# # import numpy as np
#
# def calculate_topsis(data, weights, impacts):
#     """
#     Hàm tính toán TOPSIS.
#
#     :param data: Ma trận dữ liệu (numpy array), mỗi hàng là một lựa chọn, mỗi cột là một tiêu chí.
#     :param weights: Trọng số của các tiêu chí (list hoặc numpy array).
#     :param impacts: Loại tác động của tiêu chí ('+' cho lợi ích, '-' cho chi phí).
#     :return: Tuple chứa điểm TOPSIS và thứ hạng.
#     """
#     # 1. Chuẩn hóa ma trận quyết định
#     norm_data = data / np.sqrt(np.sum(data**2, axis=0))
#
#     # 2. Tính ma trận quyết định đã được chuẩn hóa và có trọng số
#     weighted_data = norm_data * weights
#
#     # 3. Xác định giải pháp lý tưởng (A+) và giải pháp tồi tệ nhất (A-)
#     ideal_best = np.zeros(len(weights))
#     ideal_worst = np.zeros(len(weights))
#
#     for i in range(len(weights)):
#         if impacts[i] == '+':
#             ideal_best[i] = np.max(weighted_data[:, i])
#             ideal_worst[i] = np.min(weighted_data[:, i])
#         else: # impact is '-'
#             ideal_best[i] = np.min(weighted_data[:, i])
#             ideal_worst[i] = np.max(weighted_data[:, i])
#
#     # 4. Tính khoảng cách đến giải pháp lý tưởng và giải pháp tồi tệ nhất
#     dist_best = np.sqrt(np.sum((weighted_data - ideal_best)**2, axis=1))
#     dist_worst = np.sqrt(np.sum((weighted_data - ideal_worst)**2, axis=1))
#
#     # 5. Tính điểm tương đối gần với giải pháp lý tưởng
#     # Thêm một số rất nhỏ (epsilon) để tránh chia cho 0
#     topsis_score = dist_worst / (dist_best + dist_worst + 1e-9)
#
#     # 6. Xếp hạng các lựa chọn
#     # argsort trả về chỉ số của các phần tử đã sắp xếp, [::-1] để đảo ngược (giảm dần)
#     ranks = np.argsort(np.argsort(-topsis_score)) + 1
#
#     return topsis_score, ranks
#
# def prepare_and_run_topsis(house_data: list):
#     """
#     Chuẩn bị dữ liệu và chạy thuật toán TOPSIS
#     """
#     if not house_data:
#         return []
#
#     # Định nghĩa các tiêu chí, trọng số và tác động
#     # Ở đây ta chọn 2 tiêu chí đơn giản: Giá (càng thấp càng tốt) và Diện tích (càng cao càng tốt)
#     # Bạn có thể mở rộng với nhiều tiêu chí hơn.
#     criteria_keys = ['price', 'acreage']
#     weights = [0.5, 0.5]  # Giả sử trọng số bằng nhau
#     impacts = ['-', '+']   # '-' cho giá, '+' cho diện tích
#
#     # Tạo ma trận dữ liệu từ danh sách các phòng trọ
#     matrix = np.array([[item[key] for key in criteria_keys] for item in house_data])
#
#     # Chạy TOPSIS
#     scores, ranks = calculate_topsis(matrix, weights, impacts)
#
#     # Gắn kết quả TOPSIS vào dữ liệu gốc
#     results_with_topsis = []
#     for i, item in enumerate(house_data):
#         # Tạo một bản sao của item để không thay đổi dữ liệu gốc
#         result_item = item.copy()
#         result_item['topsis_score'] = scores[i]
#         result_item['rank'] = int(ranks[i])
#         results_with_topsis.append(result_item)
#
#     # Sắp xếp kết quả cuối cùng theo rank
#     sorted_results = sorted(results_with_topsis, key=lambda x: x['rank'])
#
#     return sorted_results
