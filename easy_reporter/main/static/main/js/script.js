// ====================
// 전역 상태 변수
// ====================
let userLocation = null;       // GPS 기반 위치
let recognizedPlate = null;    // OCR 번호판 결과
let selectedViolation = null;  // 선택된 위반 유형

// ====================
// 위치 가져오기
// ====================
async function setUserLocation() {
    const locationText = document.getElementById('locationText');
    const locationCard = document.getElementById('locationCard');

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;
                try {
                    const res = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=30&addressdetails=1`
                    );
                    const data = await res.json();
                    const addr = data.address;

                    console.log(addr)

                    // "대한민국 시/도 시/군/구 읍/면/동" 조합
                    userLocation = [
                        addr.country || "",        // 대한민국
                        addr.city || "",          // 대구광역시
                        addr.county || "",          // 달성군
                        addr.town || "",          // 다사읍
                        addr.postcode || "",          // 우편번호

                    ]
                        .filter(Boolean)
                        .join(" ");

                    if (!userLocation) {
                        userLocation = "위치 정보를 가져올 수 없습니다";
                    }

                    locationText.textContent = userLocation;
                    locationCard.classList.remove("hidden");
                } catch (err) {
                    console.error("역지오코딩 실패:", err);
                    locationText.textContent = "위치 정보를 가져올 수 없습니다";
                    locationCard.classList.remove("hidden");
                }
            },
            (err) => {
                console.error("위치 가져오기 실패:", err);
                locationText.textContent = "위치 정보를 가져올 수 없습니다";
                locationCard.classList.remove("hidden");
            }
        );
    } else {
        locationText.textContent = "브라우저에서 위치를 지원하지 않습니다";
        locationCard.classList.remove("hidden");
    }
}




// ====================
// 파일 업로드 처리
// ====================
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');

uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('uploadArea').classList.add('hidden');
        document.getElementById('imagePreview').classList.remove('hidden');
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('image', file);

    try {
        const res = await fetch('upload_image/', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.plate) {
            recognizedPlate = data.plate;
            document.getElementById('plateNumber').textContent = recognizedPlate;
            document.getElementById('plateResult').classList.remove('hidden');
            document.getElementById('violationSection').classList.remove('hidden');

            // 실제 위치 가져오기
            setUserLocation();
        } else {
            console.error('OCR 결과 없음:', data.error);
        }
    } catch (err) {
        console.error('서버 요청 오류:', err);
    }
});

function changeImage() {
    fileInput.click();
}

// ====================
// 위반 유형 선택
// ====================
const violationDB = {
    signal: { law: '도로교통법 제5조', fine: 60000, points: 15, desc: '신호등이 적색일 때 정지선을 넘어 진행한 경우' },
    parking: { law: '도로교통법 제32조', fine: 80000, points: 10, desc: '주정차 금지구역에 주차' },
    lane: { law: '도로교통법 제13조', fine: 60000, points: 10, desc: '중앙선 침범 또는 지정차로 위반' },
    crosswalk: { law: '도로교통법 제27조', fine: 80000, points: 10, desc: '횡단보도에서 보행자 보호의무 위반' },
    bus: { law: '도로교통법 제15조', fine: 50000, points: 10, desc: '버스전용차로 위반' },
    speed: { law: '도로교통법 제17조', fine: 100000, points: 30, desc: '제한속도 20km/h 이상 초과' }
};

document.querySelectorAll('.violation-item').forEach(item => {
    item.addEventListener('click', () => {
        // 선택 해제
        document.querySelectorAll('.violation-item').forEach(i => i.classList.remove('selected'));
        // 선택
        item.classList.add('selected');

        selectedViolation = item.dataset.type;
        const info = violationDB[selectedViolation];

        document.getElementById('lawText').textContent = info.law;
        document.getElementById('fineText').textContent = info.fine.toLocaleString() + '원';
        document.getElementById('pointsText').textContent = info.points + '점';
        document.getElementById('descText').textContent = info.desc;
        document.getElementById('violationInfo').classList.remove('hidden');

        document.getElementById('submitBtn').classList.remove('hidden');
    });
});

// ====================
// 신고 제출
// ====================
document.getElementById('submitBtn').addEventListener('click', async () => {
    if (!selectedViolation || !fileInput.files[0]) {
        alert("위반 유형과 사진을 선택해주세요.");
        return;
    }

    const payload = new FormData();
    payload.append("violation_type", selectedViolation);
    payload.append("location", userLocation);
    payload.append("plate_number", recognizedPlate);
    payload.append("image", fileInput.files[0]);  // 이미지 파일 추가

    try {
        const res = await fetch("/submit_report/", {
            method: "POST",
            body: payload,  // FormData로 전송
        });

        const data = await res.json();

        if (data.status === "success") {
            document.getElementById('reportNumber').textContent = data.report_id;
            document.getElementById('successModal').style.display = 'flex';
            setTimeout(() => location.reload(), 3000);
        } else {
            alert("신고 실패: " + data.message);
        }
    } catch (err) {
        console.error("신고 중 오류:", err);
        alert("네트워크 오류 발생!");
    }
});

// ====================
// WebSocket 채팅봇
// ====================
const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
const chatSocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/chat/");

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    addMessage(data.message, false);
};

chatSocket.onopen = function () {
    console.log("WebSocket connected");
};

chatSocket.onclose = function () {
    console.log("WebSocket disconnected");
};

function toggleChatbot() {
    const chatbot = document.getElementById('chatbot');
    chatbot.style.display = chatbot.style.display === 'flex' ? 'none' : 'flex';
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, true);
    input.value = '';

    if (chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({ message, timestamp: Date.now() }));
    } else {
        console.error('WebSocket 연결이 열려있지 않습니다.');
    }
}

function handleChatKeyPress(e) {
    if (e.key === 'Enter') sendMessage();
}

function addMessage(text, isUser) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : ''}`;
    messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
