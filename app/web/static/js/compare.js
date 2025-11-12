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
});
