 // 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const inputText = document.getElementById('input-text');
    const resultContainer = document.getElementById('result-container');
    const processBtn = document.getElementById('process-btn');
    const clearBtn = document.getElementById('clear-btn');
    const copyBtn = document.getElementById('copy-btn');
    const charCount = document.getElementById('char-count');
    const processStatus = document.getElementById('process-status');
    const processTime = document.getElementById('process-time');
    const processCount = document.getElementById('process-count');
    const tradToSimpBtn = document.getElementById('trad-to-simp');
    const simpToTradBtn = document.getElementById('simp-to-trad');
    const tradToSimpLabel = tradToSimpBtn.parentElement;
    const simpToTradLabel = simpToTradBtn.parentElement;
    // 获取导航栏父元素
    const functionTabs = document.getElementById('functionTabs');
    const hyphenInput = document.getElementById('hyphen');
    const isCountryAbbrCheckbox = document.getElementById('is_country_abbr');
const regexInput = document.getElementById('regex-input');
    const replaceInput = document.getElementById('replace-input');

    // 转换计数器和类型
    let count = 0;
    let convertType = 't2s'; // 默认繁体转简体
    let processType = 'tc_sc'; // 默认繁简转换
    let pinyinHyphen = hyphenInput.value;
    let isCountryAbbr = isCountryAbbrCheckbox.checked;

    // 监听输入事件
        hyphenInput.addEventListener('input', function () {
            // 获取输入框的当前值
            const currentValue = this.value;
            // 修改变量的值
            pinyinHyphen = currentValue;
        });
// 监听 change 事件
        isCountryAbbrCheckbox.addEventListener('change', function () {
            // 更新变量的值
            isCountryAbbr = this.checked;
        });

    // 监听导航栏的 'shown.bs.tab' 事件
    functionTabs.addEventListener('shown.bs.tab', function (event) {
        // 获取当前激活的选项卡按钮
        const activeTab = event.target;
        // 获取当前激活选项卡的 ID
        const activeTabId = activeTab.id;

        switch (activeTabId) {
            case 'tab-s2t':
                processType = 'tc_sc';
                break;
            case 'tab-pinyin':
                processType = 'pinyin';
                break;
            case 'tab-abbr':
                processType = 'country_zh_abbr';
                break;
            case 'tab-regex':
                processType = 'regex';
                break;
            case 'tab-encoding':
                processType = 'encoding';
                break;
            default:
                processType = 'unknow';
        }

        // 打印处理类型，你可以根据需求进行其他操作
        console.log('当前处理类型:', processType);
    });


    // 更新字符计数
    inputText.addEventListener('input', function() {
        charCount.textContent = inputText.value.length;
    });

    // 清空按钮事件
    clearBtn.addEventListener('click', function() {
        inputText.value = '';
        resultContainer.innerHTML = '<p class="text-muted fst-italic">转换结果将显示在这里...</p>';
        charCount.textContent = '0';
        processStatus.textContent = '准备就绪';
        processTime.textContent = '0.00s';
        inputText.focus();
    });

    // 复制结果按钮事件
    copyBtn.addEventListener('click', function() {
        const textToCopy = resultContainer.textContent.trim();
        if (textToCopy && textToCopy !== '转换结果将显示在这里...') {
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    const originalText = copyBtn.innerHTML;
                    copyBtn.innerHTML = '已复制';
                    copyBtn.classList.add('bg-success', 'text-white', 'border-success');

                    setTimeout(() => {
                        copyBtn.innerHTML = originalText;
                        copyBtn.classList.remove('bg-success', 'text-white', 'border-success');
                    }, 2000);
                })
                .catch(err => {
                    console.error('复制失败: ', err);
                    alert('复制失败，请手动复制');
                });
        }
    });

    // 转换类型切换
    tradToSimpBtn.addEventListener('change', function() {
        if (this.checked) {
            convertType = 't2s';
            tradToSimpLabel.classList.add('btn-primary');
            tradToSimpLabel.classList.add('active');
            tradToSimpLabel.classList.remove('btn-outline-primary');
            simpToTradLabel.classList.remove('btn-primary');
            simpToTradLabel.classList.remove('active');
            simpToTradLabel.classList.add('btn-outline-primary');
            inputText.placeholder = '請輸入繁體中文...';
            if (inputText.value.trim() === '') {
                resultContainer.innerHTML = '<p class="text-muted fst-italic">转换结果将显示在这里...</p>';
            }
        }
    });

    simpToTradBtn.addEventListener('change', function() {
        if (this.checked) {
            convertType = 's2t';
            simpToTradLabel.classList.add('btn-primary');
            simpToTradLabel.classList.add('active');
            simpToTradLabel.classList.remove('btn-outline-primary');
            tradToSimpLabel.classList.remove('btn-primary');
            tradToSimpLabel.classList.remove('active');
            tradToSimpLabel.classList.add('btn-outline-primary');
            inputText.placeholder = '请输入简体中文...';
            if (inputText.value.trim() === '') {
                resultContainer.innerHTML = '<p class="text-muted fst-italic">转换结果将显示在这里...</p>';
            }
        }
    });

    // 转换按钮事件
    processBtn.addEventListener('click', function() {
        const text = inputText.value.trim();
        if (!text) {
            alert('请输入要转换的文字');
            return;
        }

        // 更新状态
        processStatus.textContent = '轉換中...';
        processStatus.classList.add('text-warning');
        processStatus.classList.remove('text-muted', 'text-success', 'text-danger');
        processTime.textContent = '处理中...';
        resultContainer.innerHTML = '<p class="text-muted">正在进行转换，请稍候...</p>';

        // 记录开始时间
        const startTime = performance.now();

        if (processType === 'regex') {
            const regex = new RegExp(regexInput.value, 'g');
            const replacedText = text.replace(regex, replaceInput.value);

            // 计算转换时间
            const endTime = performance.now();
            const duration = ((endTime - startTime) / 1000).toFixed(2);

            // 更新结果和状态
            resultContainer.textContent = replacedText;
            processStatus.textContent = '轉換成功';
            processStatus.classList.remove('text-warning');
            processStatus.classList.add('text-success');
            processTime.textContent = `${duration}s`;
            processCount.textContent = ++count;

            // 为结果添加高亮动画
            resultContainer.classList.add('bg-warning-subtle');
            setTimeout(() => {
                resultContainer.classList.remove('bg-warning-subtle');
            }, 1000);
        } else {
        // 发送请求到后端
        fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                direction: convertType,
                ptype: processType,
                pinyinHyphen: pinyinHyphen,
                isCountryAbbr: isCountryAbbr
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
            resultContainer.value = data.converted_text;
            processStatus.textContent = '轉換成功';
            processStatus.classList.remove('text-warning');
            processStatus.classList.add('text-success');
            processTime.textContent = `${duration}s`;
            processCount.textContent = ++count;

            // 为结果添加高亮动画
            resultContainer.classList.add('bg-warning-subtle');
            setTimeout(() => {
                resultContainer.classList.remove('bg-warning-subtle');
            }, 1000);
        })
        .catch(error => {
            console.error('转换出错:', error);
            resultContainer.innerHTML = `<p class="text-danger">转换出错: ${error.message}</p>`;
            processStatus.textContent = '轉換失敗';
            processStatus.classList.remove('text-warning');
            processStatus.classList.add('text-danger');
        });
        }
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