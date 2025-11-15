let currentPage = 1;
const PAGE_SIZE = 12; // Hiển thị 12 kết quả mỗi trang

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
    const resultsDiv = document.getElementById("results-compare");

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
            renderCardResults(data)

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

        let idealSolutionsHtml = '';
        if (idealBest && idealWorst) {
            idealSolutionsHtml = `
                <div class="collapsible-section">
                    <h2 class="collapsible-header">Bảng Tiêu Chí Lý Tưởng <span class="toggle-icon">-</span></h2>
                    <div class="collapsible-content" style="display: block;">
                        <table class="ideal-table">
                            <thead>
                                <tr>
                                    <th>Tiêu chí</th>
                                    <th>Lý tưởng (Tốt nhất)</th>
                                    <th>Tồi nhất</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Giá (triệu)</td><td>${idealBest.price.toFixed(2)}</td><td>${idealWorst.price.toFixed(2)}</td></tr>
                                <tr><td>Diện tích (m²)</td><td>${idealBest.acreage.toFixed(2)}</td><td>${idealWorst.acreage.toFixed(2)}</td></tr>
                                <tr><td>Tỉ lệ diện tích/giá</td><td>${idealBest.acreage_ratio.toFixed(3)}</td><td>${idealWorst.acreage_ratio.toFixed(3)}</td></tr>
                                <tr><td>Điểm tiện ích</td><td>${idealBest.amenities_w.toFixed(3)}</td><td>${idealWorst.amenities_w.toFixed(3)}</td></tr>
                                <tr><td>Tỉ lệ tiện ích/giá</td><td>${idealBest.amenities_ratio.toFixed(3)}</td><td>${idealWorst.amenities_ratio.toFixed(3)}</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        const resultsTableHtml = `
            <div class="collapsible-section">
                <h2 class="collapsible-header">Bảng Xếp Hạng Chi Tiết <span class="toggle-icon">-</span></h2>
                <div class="collapsible-content" style="display: block;">
                    <div class="table-scroll">
                        <table class="results-table">
                        <thead>
                            <tr>
                                <th>Hạng</th>
                                <th>Tiêu đề</th>
                                <th>Giá (triệu)</th>
                                <th>Diện tích (m²)</th>
                                <th>Điểm Diện Tích/Giá</th>
                                <th>Điểm Tiện Ích</th>
                                <th>Điểm Tiện Ích/Giá</th>
                                <th>Điểm TOPSIS</th>
                                <th>Tiện ích phù hợp</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${houses.map(h => {
                                const availableAmenitiesHtml = (h.environments || [])
                                    .map(amenity => {
                                        const isMatched = (h.matched_amenities || []).some(matched => matched.id === amenity.id);
                                        return isMatched? `<span class="amenity-tag matched">${amenity.category}: ${amenity.value}</span>`: '';
                                    })
                                    .join('');

                                return `
                                <tr>
                                    <td class="rank-cell">${h.rank}</td>
                                    <td title="${h.address}">${h.title}</td>
                                    <td>${h.price.toFixed(2)}</td>
                                    <td>${h.acreage.toFixed(2)}</td>
                                    <td>${h.acreage_ratio.toFixed(3)}</td>
                                    <td>${h.amenities_w.toFixed(3)}</td>
                                    <td>${h.amenities_ratio.toFixed(3)}</td>
                                    <td class="score-cell">${h.topsis_score.toFixed(4)}</td>
                                    <td><div class="amenities-list">${availableAmenitiesHtml || 'N/A'}</div></td>
                                </tr>
                                `;
                            }).join("")}
                        </tbody>
                    </table>
                    </div>
                </div>
            </div>
        `;
        
        // Hiển thị tiêu chí lý tưởng trước, sau đó đến bảng kết quả
        resultsDiv.innerHTML = idealSolutionsHtml + resultsTableHtml;
    }

    function renderCardResults(data) {
        const houses = data.ranked_houses || [];

        if (houses.length === 0) {
            resultsDiv.innerHTML = "<p>Không có dữ liệu kết quả.</p>";
            return;
        }

        const resultsContainer = document.getElementById('results');
        const prevButton = document.getElementById('prev-page');
        const nextButton = document.getElementById('next-page');
        const pageInfo = document.getElementById('page-info');

        // Cập nhật thông tin trang
        pageInfo.textContent = `Trang ${currentPage}`;

        // Cập nhật trạng thái nút
        prevButton.disabled = currentPage === 1;
        nextButton.disabled = houses.length < PAGE_SIZE;

        resultsContainer.innerHTML = ''; // Xóa kết quả cũ

        if (houses.length === 0) {
            resultsContainer.innerHTML = "<p>Không có dữ liệu kết quả.</p>";
            return;
        }

        houses.forEach(h => {
            const card = document.createElement('div');
            card.className = 'card';
            card.setAttribute('data-listing-id', h.id);

            const fullAddress = `${h.address}`;

            const tagsHtml = (h.environments || []).map(tag => {
                const isMatched = (h.matched_amenities || []).some(matched => matched.id === tag.id);
                return `<span class="amenity-tag ${isMatched ? 'matched' : ''}">${tag.category}: ${tag.value}</span>`;
            }).join('');

            card.innerHTML = `
                <div class="card-content">
                    <h3 class="card-title">${h.title}</h3>
                    <p class="card-info"><strong>Địa chỉ:</strong> ${fullAddress}</p>
                    <p class="card-info"><strong>Loại hình:</strong> ${h.house_type || 'N/A'}</p>
                    <p class="card-info"><strong>Hợp đồng:</strong> ${h.contract_period || 'N/A'}</p>
                    <p class="card-info"><strong>Liên hệ:</strong> ${h.phone_number || 'N/A'}</p>
                    <div class="tags-container">${tagsHtml}</div>
                </div>
                <div class="card-footer">
                    <span class="price">${h.price} triệu/tháng</span> - 
                    <span class="acreage">${h.acreage} m²</span>
                </div>            
            `;

            resultsContainer.appendChild(card);
        });
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
