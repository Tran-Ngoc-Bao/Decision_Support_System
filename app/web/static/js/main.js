let currentPage = 1;
const PAGE_SIZE = 12; // Hiển thị 12 kết quả mỗi trang
let selectedListingIds = new Set(); 
document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const provinceSelect = document.getElementById('province_id');
    const districtSelect = document.getElementById('district_id');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    const compareButton = document.getElementById('compare-button');
    const clearSelectionButton = document.getElementById('clear-selection-btn');

    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            currentPage = 1; // Reset về trang đầu tiên khi có tìm kiếm mới
            fetchListings();
        });
    }

    if (provinceSelect) {
        provinceSelect.addEventListener('change', () => {
            const provinceId = provinceSelect.value;
            populateDistricts(provinceId);
            // Xóa danh sách phường/xã khi tỉnh thay đổi
            document.getElementById('ward_id').innerHTML = '<option value="">-- Chọn Phường/Xã --</option>';
        });
    }

    if (districtSelect) {
        districtSelect.addEventListener('change', () => {
            const districtId = districtSelect.value;
            populateWards(districtId);
        });
    }

    if (prevButton) {
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                fetchListings();
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', () => {
            currentPage++;
            fetchListings();
        });
    }

    if (compareButton) {
        compareButton.addEventListener('click', () => {
            // Tạm thời để trống action hoặc log ra console
            if (selectedListingIds.size < 2) {
                alert('Vui lòng chọn ít nhất 2 mục để so sánh.');
                return;
            }
            console.log('So sánh các ID:', Array.from(selectedListingIds));
            // TODO: Chuyển hướng đến trang so sánh với các ID đã chọn
            // window.location.href = `/compare?ids=${Array.from(selectedListingIds).join(',')}`;
        });
    }

    if (clearSelectionButton) {
        clearSelectionButton.addEventListener('click', clearAllSelections);
    }

    // Tải dữ liệu ban đầu khi trang được mở
    // Điền sẵn các giá trị mặc định vào form
    document.getElementById('min_price').value = 3.0;
    document.getElementById('max_price').value = 7.0;
    document.getElementById('min_acreage').value = 20.0;
    document.getElementById('max_acreage').value = 50.0;
    document.getElementById('contract_period').value = '6 THÁNG';
    fetchListings();
    populateProvinces();
    populateHouseTypes();
});

function fetchListings() {
    const form = document.getElementById('search-form');
    const params = new URLSearchParams();
    const offset = (currentPage - 1) * PAGE_SIZE;

    // Lấy giá trị từ các trường input
    const provinceId = form.province_id.value;
    const districtId = form.district_id.value;
    const wardId = form.ward_id.value;
    const minPrice = form.min_price.value;
    const maxPrice = form.max_price.value;
    const minAcreage = form.min_acreage.value;
    const maxAcreage = form.max_acreage.value;
    const houseType = form.house_type.value;
    const contractPeriod = form.contract_period.value;

    // Thêm vào query params nếu có giá trị
    if (provinceId) params.append('province_id', provinceId);
    if (districtId) params.append('district_id', districtId);
    if (wardId) params.append('ward_id', wardId);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    if (minAcreage) params.append('min_acreage', minAcreage);
    if (maxAcreage) params.append('max_acreage', maxAcreage);
    if (houseType) params.append('house_type', houseType);
    if (contractPeriod) params.append('contract_period', contractPeriod);
    
    params.append('limit', PAGE_SIZE);
    params.append('offset', offset);

    const queryString = params.toString();
    const url = `/api/search/house-rent?${queryString}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
            document.getElementById('results').innerHTML = `<p style="color: red;">Lỗi khi tải dữ liệu. Vui lòng kiểm tra console.</p>`;
        });
}

function displayResults(listings) {
    const resultsContainer = document.getElementById('results');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');

    // Cập nhật thông tin trang
    pageInfo.textContent = `Trang ${currentPage}`;

    // Cập nhật trạng thái nút
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = listings.length < PAGE_SIZE;

    resultsContainer.innerHTML = ''; // Xóa kết quả cũ

    if (listings.length === 0) {
        resultsContainer.innerHTML = '<p>Không tìm thấy kết quả nào phù hợp.</p>';
        return;
    }

    listings.forEach(listing => {
        const card = document.createElement('div');
        card.className = 'card';
        card.setAttribute('data-listing-id', listing.id);
        
        if (selectedListingIds.has(listing.id)) {
            card.classList.add('selected');
        }

        const fullAddress = `${listing.address}`;

        const tagsHtml = (listing.environments || [])
            .map(tag => `<span class="tag">${tag.value}</span>`)
            .join('');

        card.innerHTML = `
            <div class="card-content">
                <h3 class="card-title">${listing.title}</h3>
                <p class="card-info"><strong>Địa chỉ:</strong> ${fullAddress}</p>
                <p class="card-info"><strong>Loại hình:</strong> ${listing.house_type || 'N/A'}</p>
                <p class="card-info"><strong>Hợp đồng:</strong> ${listing.contract_period || 'N/A'}</p>
                <p class="card-info"><strong>Liên hệ:</strong> ${listing.phone_number || 'N/A'}</p>
                <div class="tags-container">${tagsHtml}</div>
            </div>
            <div class="card-footer">
                <span class="price">${listing.price} triệu/tháng</span> - 
                <span class="acreage">${listing.acreage} m²</span>
            </div>            
        `;

        // Thêm sự kiện click
        card.addEventListener('click', function() {
            handleCardClick(this, listing.id);
        });

        resultsContainer.appendChild(card);
    });
}

function handleCardClick(cardElement, listingId) {
    if (selectedListingIds.has(listingId)) {
        selectedListingIds.delete(listingId);
        cardElement.classList.remove('selected');
    } else {
        selectedListingIds.add(listingId);
        cardElement.classList.add('selected');
    }

    updateSelectionInfo();
}

function updateSelectionInfo() {
    const selectionInfo = document.getElementById('selection-info');
    const selectionCount = document.getElementById('selection-count');
    const compareButton = document.getElementById('compare-button');
    const count = selectedListingIds.size;

    if (count > 0) {
        selectionInfo.classList.add('visible');
        selectionCount.textContent = `Đã chọn: ${count}`;
    } else {
        selectionInfo.classList.remove('visible');
    }

    // Nút so sánh chỉ bật khi có từ 2 lựa chọn trở lên
    compareButton.disabled = count < 2;
}

function clearAllSelections() {
    selectedListingIds.clear();
    
    // Bỏ lớp 'selected' khỏi tất cả các card đang hiển thị
    const selectedCards = document.querySelectorAll('.card.selected');
    selectedCards.forEach(card => {
        card.classList.remove('selected');
    });

    updateSelectionInfo();
}



function populateProvinces() {
    fetch('/api/locations/provinces')
        .then(response => response.json())
        .then(provinces => {
            const select = document.getElementById('province_id');
            provinces.forEach(province => {
                const option = document.createElement('option');
                option.value = province.id;
                option.textContent = province.name;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching provinces:', error));
}

function populateDistricts(provinceId) {
    const select = document.getElementById('district_id');
    select.innerHTML = '<option value="">-- Chọn Quận/Huyện --</option>'; // Reset
    if (!provinceId) return;

    fetch(`/api/locations/districts?province_id=${provinceId}`)
        .then(response => response.json())
        .then(districts => {
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district.id;
                option.textContent = district.name;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching districts:', error));
}

function populateWards(districtId) {
    const select = document.getElementById('ward_id');
    select.innerHTML = '<option value="">-- Chọn Phường/Xã --</option>'; // Reset
    if (!districtId) return;

    fetch(`/api/locations/wards?district_id=${districtId}`)
        .then(response => response.json())
        .then(wards => {
            wards.forEach(ward => {
                const option = document.createElement('option');
                option.value = ward.id;
                option.textContent = ward.name;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching wards:', error));
}

function populateHouseTypes() {
    fetch('/api/item/house-types')
        .then(response => response.json())
        .then(houseTypes => {
            const select = document.getElementById('house_type');
            houseTypes.forEach(houseType => {
                const option = document.createElement('option');
                option.value = houseType.name;
                option.textContent = houseType.name;
                select.appendChild(option);
            });
            // Đặt giá trị mặc định sau khi đã tải xong
            select.value = 'PHÒNG TRỌ';
        })
        .catch(error => console.error('Error fetching house types:', error));
}
