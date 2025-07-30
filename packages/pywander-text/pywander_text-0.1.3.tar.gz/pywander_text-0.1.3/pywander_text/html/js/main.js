 // 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const inputText = document.getElementById('input-text');
    const resultContainer = document.getElementById('result-container');
    const convertBtn = document.getElementById('convert-btn');
    const clearBtn = document.getElementById('clear-btn');
    const copyBtn = document.getElementById('copy-btn');
    const charCount = document.getElementById('char-count');
    const convertStatus = document.getElementById('convert-status');
    const convertTime = document.getElementById('convert-time');
    const convertCount = document.getElementById('convert-count');
    const tradToSimpBtn = document.getElementById('trad-to-simp');
    const simpToTradBtn = document.getElementById('simp-to-trad');

    // 转换计数器和类型
    let count = 0;
    let convertType = 't2s'; // 默认繁体转简体

    // 更新字符计数
    inputText.addEventListener('input', function() {
        charCount.textContent = inputText.value.length;
    });

    // 清空按钮事件
    clearBtn.addEventListener('click', function() {
        inputText.value = '';
        resultContainer.innerHTML = '<p class="text-gray-400 italic">转换结果将显示在这里...</p>';
        charCount.textContent = '0';
        convertStatus.textContent = '準備就緒';
        convertTime.textContent = '0.00s';
        inputText.focus();
    });

    // 复制结果按钮事件
    copyBtn.addEventListener('click', function() {
        const textToCopy = resultContainer.textContent.trim();
        if (textToCopy && textToCopy !== '转换结果将显示在这里...') {
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    const originalText = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fa fa-check mr-1"></i>已复制';
                    copyBtn.classList.add('bg-green-50', 'text-green-700', 'border-green-300');

                    setTimeout(() => {
                        copyBtn.innerHTML = originalText;
                        copyBtn.classList.remove('bg-green-50', 'text-green-700', 'border-green-300');
                    }, 2000);
                })
                .catch(err => {
                    console.error('复制失败: ', err);
                    alert('复制失败，请手动复制');
                });
        }
    });

    // 转换类型切换
    tradToSimpBtn.addEventListener('click', function() {
        if (convertType !== 't2s') {
            convertType = 't2s';
            tradToSimpBtn.classList.add('bg-primary', 'text-white');
            tradToSimpBtn.classList.remove('hover:bg-gray-200');
            simpToTradBtn.classList.remove('bg-primary', 'text-white');
            simpToTradBtn.classList.add('hover:bg-gray-200');
            inputText.placeholder = '請輸入繁體中文...';
            if (inputText.value.trim() === '') {
                resultContainer.innerHTML = '<p class="text-gray-400 italic">转换结果将显示在这里...</p>';
            }
        }
    });

    simpToTradBtn.addEventListener('click', function() {
        if (convertType !== 's2t') {
            convertType = 's2t';
            simpToTradBtn.classList.add('bg-primary', 'text-white');
            simpToTradBtn.classList.remove('hover:bg-gray-200');
            tradToSimpBtn.classList.remove('bg-primary', 'text-white');
            tradToSimpBtn.classList.add('hover:bg-gray-200');
            inputText.placeholder = '请输入简体中文...';
            if (inputText.value.trim() === '') {
                resultContainer.innerHTML = '<p class="text-gray-400 italic">转换结果将显示在这里...</p>';
            }
        }
    });

    // 转换按钮事件
    convertBtn.addEventListener('click', function() {
        const text = inputText.value.trim();
        if (!text) {
            alert('请输入要转换的文字');
            return;
        }

        // 更新状态
        convertStatus.textContent = '轉換中...';
        convertStatus.classList.add('text-yellow-500');
        convertStatus.classList.remove('text-gray-500', 'text-green-500', 'text-red-500');
        convertTime.textContent = '处理中...';
        resultContainer.innerHTML = '<p class="text-gray-500">正在进行转换，请稍候...</p>';

        // 记录开始时间
        const startTime = performance.now();

        // 发送请求到后端
        fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                direction: convertType
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('转换服务出错');
            }
            return response.json();
        })
        .then(data => {
            // 计算转换时间
            const endTime = performance.now();
            const duration = ((endTime - startTime) / 1000).toFixed(2);

            // 更新结果和状态
            resultContainer.textContent = data.converted_text;
            convertStatus.textContent = '轉換成功';
            convertStatus.classList.remove('text-yellow-500');
            convertStatus.classList.add('text-green-500');
            convertTime.textContent = `${duration}s`;
            convertCount.textContent = ++count;

            // 为结果添加高亮动画
            resultContainer.classList.add('bg-yellow-50');
            setTimeout(() => {
                resultContainer.classList.remove('bg-yellow-50');
            }, 1000);
        })
        .catch(error => {
            console.error('转换出错:', error);
            resultContainer.innerHTML = `<p class="text-red-500">转换出错: ${error.message}</p>`;
            convertStatus.textContent = '轉換失敗';
            convertStatus.classList.remove('text-yellow-500');
            convertStatus.classList.add('text-red-500');
        });
    });

    // 为输入框添加粘贴事件处理
    inputText.addEventListener('paste', function() {
        setTimeout(() => {
            charCount.textContent = inputText.value.length;
        }, 10);
    });

    // 为输入区域添加拖放支持
    inputText.addEventListener('dragover', function(e) {
        e.preventDefault();
        inputText.classList.add('border-dashed', 'border-primary');
    });

    inputText.addEventListener('dragleave', function() {
        inputText.classList.remove('border-dashed', 'border-primary');
    });

    inputText.addEventListener('drop', function(e) {
        e.preventDefault();
        inputText.classList.remove('border-dashed', 'border-primary');

        const data = e.dataTransfer;
        if (data.items) {
            // 处理文本数据
            if (data.items[0].kind === 'string') {
                data.items[0].getAsString(function(str) {
                    inputText.value = str;
                    charCount.textContent = inputText.value.length;
                });
            }
        }
    });

    // 设置焦点到输入框
    inputText.focus();
});