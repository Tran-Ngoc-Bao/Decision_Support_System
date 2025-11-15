document.addEventListener('DOMContentLoaded', () => {
    const amenitiesContainer = document.getElementById('amenities-container');

    // Hàm để lấy danh sách tiện ích từ API
    async function fetchAmenities() {
        try {
            const response = await fetch('http://localhost:8000/api/item/amenities');

            if (!response.ok) {
                throw new Error(`Lỗi API: ${response.statusText}`);
            }

            const amenities = await response.json();
            populateAmenities(amenities);

        } catch (error) {
            console.error('Không thể tải danh sách tiện ích:', error);
            amenitiesContainer.innerHTML = '<p style="color: red;">Không thể tải danh sách tiện ích. Vui lòng kiểm tra lại API.</p>';
        }
    }

    // Hàm để hiển thị tiện ích và thanh trượt trọng số
    function populateAmenities(amenities) {
        amenitiesContainer.innerHTML = ''; // Xóa nội dung cũ

        amenities.forEach(amenity => {
            const amenityDiv = document.createElement('div');
            amenityDiv.className = 'amenity';

            amenityDiv.innerHTML = `
                <input type="checkbox" id="amenity-${amenity.id}" name="amenity_${amenity.id}">
                <label for="amenity-${amenity.id}">${amenity.category}: ${amenity.value}</label>
                <input type="number" id="weight-${amenity.id}" name="weight_${amenity.id}" min="0" max="100" step="1" value="50" disabled>
            `;

            amenitiesContainer.appendChild(amenityDiv);

            // Thêm sự kiện để bật/tắt và di chuyển mục được chọn lên đầu
            const checkbox = amenityDiv.querySelector(`#amenity-${amenity.id}`);
            const weightInput = amenityDiv.querySelector(`#weight-${amenity.id}`);

            checkbox.addEventListener('change', () => {
                weightInput.disabled = !checkbox.checked;
                if (checkbox.checked) {
                    amenitiesContainer.prepend(amenityDiv);
                }
            });
        });
    }

    fetchAmenities();

    const form = document.getElementById("compare-form");
    const resultsDiv = document.getElementById("results");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Lấy house_rent_ids từ URL
        const params = new URLSearchParams(window.location.search);
        const idsParam = params.get("ids");
        const houseIds = idsParam ? idsParam.split(",").map(Number) : [];

        // Lấy danh sách amenities được chọn và trọng số tương ứng
        const checkedAmenities = Array.from(document.querySelectorAll('#amenities-container input[type="checkbox"]:checked'));
        const amenities = checkedAmenities.map(cb => {
            const id = parseInt(cb.id.replace("amenity-", ""));
            return id;
        });

        const weights = checkedAmenities.map(cb => {
            const id = parseInt(cb.id.replace("amenity-", ""));
            const weight = parseFloat(document.querySelector(`#weight-${id}`).value);
            return isNaN(weight) ? 0 : weight;
        });

        if (amenities.length === 0) {
            alert("Vui lòng chọn ít nhất một tiêu chí để so sánh!");
            return;
        }

        const payload = {
            house_rent_ids: houseIds,
            amenities: amenities,
            weights: weights,
            topsis_weight: [] // nếu bạn cần trọng số TOPSIS riêng thì thêm sau
        };

        console.log("📤 Gửi dữ liệu:", payload);

        try {
            const response = await fetch("http://localhost:8000/api/dss/compare", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Lỗi API: ${response.statusText}`);
            }

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            console.error("❌ Lỗi khi gọi API so sánh:", error);
            resultsDiv.innerHTML = `<p style="color:red;">Không thể so sánh: ${error.message}</p>`;
        }
    });

    function renderResults(data) {
        const houses = data.ranked_houses || [];
        const idealBest = data.ideal_best;
        const idealWorst = data.ideal_worst;

        if (houses.length === 0) {
            resultsDiv.innerHTML = "<p>Không có dữ liệu kết quả.</p>";
            return;
        }

        let idealCriteriaHtml = '';
        if (idealBest && idealWorst) {
            idealCriteriaHtml = `
                <div class="collapsible-section">
                    <h2 class="collapsible-header">Tiêu chí lý tưởng và tồi nhất <span class="toggle-icon">-</span></h2>
                    <div class="collapsible-content" style="display: block;">
                        <div class="ideal-criteria">
                            <div class="ideal-card">
                                <h3>Lý tưởng (Ideal Best)</h3>
                                <p><strong>Giá:</strong> ${idealBest.price.toFixed(2)} triệu</p>
                                <p><strong>Diện tích:</strong> ${idealBest.acreage.toFixed(2)} m²</p>
                                <p><strong>Tỉ lệ diện tích/giá:</strong> ${idealBest.acreage_ratio.toFixed(3)}</p>
                                <p><strong>Điểm tiện ích:</strong> ${idealBest.amenities_w.toFixed(3)}</p>
                                <p><strong>Tỉ lệ tiện ích/giá:</strong> ${idealBest.amenities_ratio.toFixed(3)}</p>
                            </div>
                            <div class="ideal-card">
                                <h3>Tồi nhất (Ideal Worst)</h3>
                                <p><strong>Giá:</strong> ${idealWorst.price.toFixed(2)} triệu</p>
                                <p><strong>Diện tích:</strong> ${idealWorst.acreage.toFixed(2)} m²</p>
                                <p><strong>Tỉ lệ diện tích/giá:</strong> ${idealWorst.acreage_ratio.toFixed(3)}</p>
                                <p><strong>Điểm tiện ích:</strong> ${idealWorst.amenities_w.toFixed(3)}</p>
                                <p><strong>Tỉ lệ tiện ích/giá:</strong> ${idealWorst.amenities_ratio.toFixed(3)}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        const tableHtml = `
            <div class="collapsible-section">
                <h2 class="collapsible-header">Kết quả xếp hạng <span class="toggle-icon">-</span></h2>
                <div class="collapsible-content" style="display: block;">
                    <table class="results-table">
                        <thead>
                            <tr>
                                <th>Id   </th>
                                <th>Hạng</th>
                                <th>Tiêu đề</th>
                                <th>Giá (triệu)</th>
                                <th>Diện tích (m²)</th>
                                <th>Điểm diện tích (m²/triệu)</th>
                                <th>Phù hợp tiện ích</th>
                                <th>Điểm tiện ích (/triệu)</th>
                                <th>Điểm TOPSIS</th>
                                <th>Tiện ích phù hợp</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${houses.map(h => {
                                const availableAmenitiesHtml = (h.environments || [])
                                    .map(amenity => {
                                        // Đánh dấu các tiện ích khớp với lựa chọn của người dùng
                                        const isMatched = (h.matched_amenities || []).some(matched => matched.id === amenity.id);
                                        return `<span class="amenity-tag ${isMatched ? 'matched' : ''}">${amenity.value}</span>`;
                                    })
                                    .join(', ');

                                return `
                                <tr>
                                    <td>${h.id}   </td>
                                    <td>${h.rank}</td>
                                    <td title="${h.address}">${h.title}</td>
                                    <td>${h.price}</td>
                                    <td>${h.acreage}</td>
                                    <td>${h.acreage_ratio.toFixed(3)}</td>
                                    <td>${h.amenities_w.toFixed(3)}</td>
                                    <td>${h.amenities_ratio.toFixed(3)}</td>
                                    <td>${h.topsis_score.toFixed(3)}</td>
                                    <td>
                                        <div class="amenities-list">
                                            ${availableAmenitiesHtml || 'Không có thông tin'}
                                        </div>
                                    </td>
                                </tr>
                                `;
                            }).join("")}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Hiển thị tiêu chí lý tưởng trước, sau đó đến bảng kết quả
        resultsDiv.innerHTML = idealCriteriaHtml + tableHtml;
    }

    // Thêm event listener cho các mục có thể thu gọn/mở rộng
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('collapsible-header')) {
            const header = event.target;
            const content = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');

            if (content.style.display === "block") {
                content.style.display = "none";
                icon.textContent = '+';
            } else {
                content.style.display = "block";
                icon.textContent = '-';
            }
        }
    });
});
