const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const uploadContent = document.querySelector('.upload-content');

// 拖放功能
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropArea.classList.add('highlight');
}

function unhighlight(e) {
    dropArea.classList.remove('highlight');
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// 文件选择按钮
document.querySelector('.select-btn').addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', function() {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        // 显示上传的图片
        const file = files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadContent.innerHTML = `
                <img src="${e.target.result}" alt="上传的图片" class="uploaded-image">
            `;
        };
        reader.readAsDataURL(file);
        showActionButtons();
    }
}

function showUploadProgress() {
    uploadContent.innerHTML = `
        <div class="progress-bar">
            <div class="progress"></div>
        </div>
    `;
}

function showActionButtons() {
    document.querySelector('.button-group').style.display = 'flex';
}

async function detectObjects() {
    const file = fileInput.files[0];
    if (!file) {
        alert('请选择图片文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        showResults(data);
        showDownloadButton();

    } catch (error) {
        console.error('Error:', error);
        alert('识别过程中出现错误');
    }
}

function showResults(data) {
    const resultArea = document.querySelector('.result-area');
    resultArea.innerHTML = `
        <img src="data:image/jpeg;base64,${data.image}" alt="识别结果" class="result-image" style="display: block;">
        <div class="detection-results" style="display: block; margin-top: 20px;">
            <h3>检测结果：</h3>
            ${data.results.map(result => `
                <div class="detection-item">
                    <p>类型: ${result.class}</p>
                    <p>检测置信度: ${(result.confidence * 100).toFixed(2)}%</p>
                    <p>车牌号码: ${result.plate_number}</p>
                    <p>文字识别置信度: ${(result.ocr_confidence * 100).toFixed(2)}%</p>
                    <p>边界框坐标: [${result.bbox.join(', ')}]</p>
                </div>
            `).join('')}
        </div>
    `;
}

function showDownloadButton() {
    document.querySelector('.download-area').style.display = 'block';
}

function cancelUpload() {
    location.reload();
}

function downloadResults() {
    // 实现下载功能
    alert('下载功能待实现');
} 