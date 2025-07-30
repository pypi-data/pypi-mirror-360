// 在文件开头添加重试函数
function retryUploadPart(client, params, maxRetries = 3) {
    let retries = 0;
    
    function attempt() {
        return client.uploadPart(params).catch(function(error) {
            retries++;
            if (retries < maxRetries) {
                console.log(`分片 ${params.partNumber} 重试第 ${retries} 次`);
                return new Promise(resolve => setTimeout(resolve, 1000 * retries))
                    .then(() => attempt());
            }
            throw error;
        });
    }
    
    return attempt();
}
// 原生全屏功能
function requestFullscreen(element) {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
}

function exitFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 为每个上传控件添加事件监听（包括只读模式）
    document.querySelectorAll('.tos-uploader-container').forEach(function(container) {
        const fileInput = container.querySelector('input[type="file"]');
        const isReadonly = container.classList.contains('readonly');
        
        // 获取隐藏的实际表单字段
        const hiddenInput = container.querySelector('.tos-uploader-hidden-input');
        // 获取显示用的文本输入框
        const displayInput = container.querySelector('.tos-uploader-display-input');
        // 获取上传路径输入框
        const pathInput = container.querySelector('.upload-path-input');
        // 获取预览相关元素
        const previewButton = container.querySelector('.preview-toggle-button');
        const previewStatus = container.querySelector('.preview-status');
        const progressContainer = container.querySelector('.progress-container');
        const progressBar = container.querySelector('.progress-bar');
        const progressText = container.querySelector('.progress-text');
        const previewContainer = container.querySelector('.preview-container');
        const fileInfo = container.querySelector('.file-info');
        
        // 分片上传配置
        const PART_SIZE = 8 * 1024 * 1024; // 8MB per part
        const MULTIPART_THRESHOLD = 16 * 1024 * 1024; // 16MB threshold for multipart upload
        
        // 存储当前的video元素引用
        let currentVideoElement = null;
        let previewLoaded = false;
        
        console.log('初始化上传控件:', {
            isReadonly,
            hiddenInput,
            displayInput,
            pathInput,
            previewButton,
            initialValue: hiddenInput ? hiddenInput.value : 'null'
        });
        
        // 初始化显示输入框的值
        if (hiddenInput && hiddenInput.value && displayInput) {
            displayInput.value = hiddenInput.value;
        }
        
        // 预览按钮点击事件
        if (previewButton) {
            previewButton.addEventListener('click', function() {
                if (!previewLoaded && hiddenInput && hiddenInput.value && hiddenInput.value.trim() !== '') {
                    loadPreview(hiddenInput.value.trim());
                }
            });
        }
        
        // 只有非只读模式才添加文件选择事件
        if (!isReadonly && fileInput) {
            // 文件选择事件
            fileInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    handleFileUpload(file);
                }
            });
        }
        
        function loadPreview(url) {
            if (previewLoaded) return;
            
            // 更新按钮状态
            if (previewButton) {
                previewButton.classList.add('loading');
                previewButton.innerHTML = '⏳ 加载中...';
            }
            if (previewStatus) {
                previewStatus.textContent = '正在加载预览...';
                previewStatus.classList.add('loading');
            }
            
            // 设置预览容器为非懒加载状态
            previewContainer.setAttribute('data-lazy', 'false');
            
            // 从URL推断文件类型
            const fileType = getFileTypeFromUrl(url);
            const fileName = getFileNameFromUrl(url);
            
            // 显示文件信息
            showFileInfoFromUrl(fileName, fileType);
            
            // 显示预览
            showPreviewFromUrl(url, fileType, fileName)
                .then(() => {
                    previewLoaded = true;
                    
                    // 更新按钮状态为已加载
                    if (previewButton) {
                        previewButton.classList.remove('loading');
                        previewButton.classList.add('loaded');
                        previewButton.innerHTML = '✅ 已加载';
                    }
                    if (previewStatus) {
                        previewStatus.textContent = '预览已加载';
                        previewStatus.classList.remove('loading');
                        previewStatus.classList.add('loaded');
                    }
                })
                .catch((error) => {
                    console.error('预览加载失败:', error);
                    
                    // 更新按钮状态为错误
                    if (previewButton) {
                        previewButton.classList.remove('loading');
                        previewButton.innerHTML = '❌ 加载失败';
                    }
                    if (previewStatus) {
                        previewStatus.textContent = '预览加载失败';
                        previewStatus.classList.remove('loading');
                        previewStatus.classList.add('error');
                    }
                    
                    // 恢复懒加载状态
                    previewContainer.setAttribute('data-lazy', 'true');
                    previewContainer.innerHTML = '';
                });
        }
        
        function handleFileUpload(file) {
            // 显示文件信息
            showFileInfo(file);
            
            // 显示进度条
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            progressText.textContent = '准备上传...';
            
            // 清空预览并重置状态
            previewContainer.innerHTML = '';
            previewContainer.setAttribute('data-lazy', 'true');
            previewLoaded = false;
            
            const stsUrl = fileInput.dataset.stsUrl;
            // 从路径输入框获取动态上传路径
            let uploadPath = 'user-uploads'; // 默认值
            if (pathInput && pathInput.value.trim()) {
                uploadPath = pathInput.value.trim();
                // 清理路径：移除开头和结尾的斜杠，替换连续斜杠
                uploadPath = uploadPath.replace(/^\/+|\/+$/g, '').replace(/\/+/g, '/');
                if (!uploadPath) {
                    uploadPath = 'user-uploads';
                }
            }
            
            console.log('使用上传路径:', uploadPath);
            
            axios.get(stsUrl)
                .then(function(response) {
                    const creds = response.data;
                    console.log('STS凭证获取成功:', creds);
                    
                    if (creds.error) {
                        throw new Error(creds.error);
                    }
                    
                    // 更新状态
                    updateFileStatus('uploading', '上传中...');
                    
                    const client = new TOS({
                        accessKeyId: creds.access_key,
                        accessKeySecret: creds.secret_key,
                        stsToken: creds.security_token,
                        region: creds.region,
                        endpoint: creds.endpoint,
                        bucket: creds.bucket
                    });
                    
                    const key = `${uploadPath}/${Date.now()}-${file.name}`;
                    console.log('文件上传key:', key);
                    
                    // 根据文件大小选择上传方式
                    if (file.size > MULTIPART_THRESHOLD) {
                        return uploadLargeFile(client, creds.bucket, key, file);
                    } else {
                        return uploadSmallFile(client, creds.bucket, key, file);
                    }
                })
                .then(function(fileUrl) {
                    console.log('上传成功:', fileUrl);
                    
                    // 同时更新隐藏字段和显示字段
                    if (hiddenInput) {
                        hiddenInput.value = fileUrl;
                        console.log('已设置隐藏字段值:', fileUrl);
                        
                        // 触发change和input事件
                        const changeEvent = new Event('change', { bubbles: true });
                        const inputEvent = new Event('input', { bubbles: true });
                        hiddenInput.dispatchEvent(changeEvent);
                        hiddenInput.dispatchEvent(inputEvent);
                    }
                    
                    if (displayInput) {
                        displayInput.value = fileUrl;
                        console.log('已设置显示字段值:', fileUrl);
                    }
                    
                    // 更新进度条
                    progressBar.style.width = '100%';
                    progressText.textContent = '✅ 上传完成';
                    progressBar.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
                    
                    // 更新状态
                    updateFileStatus('success', '上传成功');
                    
                    // 立即显示预览（上传完成后）
                    previewContainer.setAttribute('data-lazy', 'false');
                    showPreview(file, fileUrl);
                    previewLoaded = true;
                    
                    // 显示预览控制按钮
                    showPreviewControls();
                    
                    // 3秒后隐藏进度条
                    setTimeout(() => {
                        progressContainer.style.display = 'none';
                    }, 3000);
                })
                // 在handleFileUpload函数的catch部分
                .catch(function(error) {
                    console.error('上传过程失败:', error);
                    let errorMessage = '上传失败: ';
                    
                    // 根据错误类型提供更具体的错误信息
                    if (error.message.includes('parts idx invalid')) {
                        errorMessage += '分片索引错误，请重试';
                    } else if (error.message.includes('InvalidAccessKey')) {
                        errorMessage += '访问密钥无效';
                    } else if (error.message.includes('network')) {
                        errorMessage += '网络连接失败';
                    } else {
                        errorMessage += error.message;
                    }
    
    progressText.textContent = '❌ ' + errorMessage;
    progressBar.style.background = 'linear-gradient(90deg, #dc3545, #c82333)';
    updateFileStatus('error', errorMessage);
});
        }
        
        function showPreviewControls() {
            // 动态创建预览控制按钮（如果不存在）
            if (!container.querySelector('.preview-controls') && hiddenInput && hiddenInput.value) {
                const controlsHtml = `
                    <div class="preview-controls">
                        <button type="button" class="preview-toggle-button loaded" data-target="${hiddenInput.name}">
                            ✅ 已加载
                        </button>
                        <span class="preview-status loaded">预览已加载</span>
                    </div>
                `;
                
                const leftPanel = container.querySelector('.tos-uploader-left');
                const displayInputContainer = leftPanel.querySelector('div[style*="position: relative"]');
                displayInputContainer.insertAdjacentHTML('afterend', controlsHtml);
            }
        }
        
        // 小文件上传（普通上传）
        function uploadSmallFile(client, bucket, key, file) {
            progressText.textContent = '上传中...';
            
            const uploadParams = {
                bucket: bucket,
                key: key,
                body: file,
            };
            
            return client.putObject(uploadParams)
                .then(function(result) {
                    return `https://${bucket}.${client.opts.endpoint}/${key}`;
                });
        }
        
        // 大文件分片上传 - 修复版本
        function uploadLargeFile(client, bucket, key, file) {
            let uploadId = null;
            const uploadedParts = [];
            
            return client.createMultipartUpload({
                bucket: bucket,
                key: key
            })
            .then(function(response) {
                uploadId = response.data.UploadId;
                console.log('分片上传初始化成功，UploadId:', uploadId);
                
                // 计算分片数量
                const totalParts = Math.ceil(file.size / PART_SIZE);
                console.log(`文件大小: ${formatFileSize(file.size)}, 分片数量: ${totalParts}`);
                
                // 串行上传每个分片，确保索引正确
                const uploadPromises = [];
                for (let i = 0; i < totalParts; i++) {
                    const start = i * PART_SIZE;
                    const end = Math.min(start + PART_SIZE, file.size);
                    const partFile = file.slice(start, end);
                    const partNumber = i + 1; // 确保从1开始
                    
                    uploadPromises.push(
                        client.uploadPart({
                            bucket: bucket,
                            key: key,
                            uploadId: uploadId,
                            partNumber: partNumber,
                            body: partFile
                        }).then(function(result) {
                            // 存储分片信息
                            const partInfo = {
                                PartNumber: partNumber,
                                ETag: result.data.ETag
                            };
                            uploadedParts.push(partInfo);
                            
                            // 更新进度
                            const progress = Math.round((uploadedParts.length / totalParts) * 100);
                            progressBar.style.width = progress + '%';
                            progressText.textContent = `上传中... ${progress}%`;
                            
                            console.log(`分片 ${partNumber}/${totalParts} 上传完成, ETag: ${result.data.ETag}`);
                            return partInfo;
                        }).catch(function(error) {
                            console.error(`分片 ${partNumber} 上传失败:`, error);
                            throw error;
                        })
                    );
                }
                
                return Promise.all(uploadPromises);
            })
            .then(function() {
                // 合并分片前确保排序正确
                console.log('开始合并分片...');
                progressText.textContent = '合并文件中...';
                
                // 按分片号排序
                uploadedParts.sort((a, b) => a.PartNumber - b.PartNumber);
                
                // 验证分片完整性
                const expectedParts = Math.ceil(file.size / PART_SIZE);
                if (uploadedParts.length !== expectedParts) {
                    throw new Error(`分片数量不匹配: 期望 ${expectedParts}, 实际 ${uploadedParts.length}`);
                }
                
                // 验证分片索引连续性
                for (let i = 0; i < uploadedParts.length; i++) {
                    if (uploadedParts[i].PartNumber !== i + 1) {
                        throw new Error(`分片索引不连续: 期望 ${i + 1}, 实际 ${uploadedParts[i].PartNumber}`);
                    }
                }
                
                console.log('分片验证通过，开始合并:', uploadedParts);
                
                // 修复：使用正确的parts格式
                return client.completeMultipartUpload({
                    bucket: bucket,
                    key: key,
                    uploadId: uploadId,
                    parts: uploadedParts.map((part) => ({
                        eTag: part.ETag,
                        partNumber: part.PartNumber
                    }))
                });
            })
            .then(function(result) {
                console.log('分片上传完成:', result);
                return `https://${bucket}.${client.opts.endpoint}/${key}`;
            })
            .catch(function(error) {
                console.error('分片上传失败:', error);
                // 尝试取消分片上传
                if (uploadId) {
                    client.abortMultipartUpload({
                        bucket: bucket,
                        key: key,
                        uploadId: uploadId
                    }).catch(console.error);
                }
                throw error;
            });
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function showFileInfo(file) {
            const fileNameEl = container.querySelector('.file-name');
            const fileSizeEl = container.querySelector('.file-size');
            const fileIcon = container.querySelector('.file-icon');
            
            if (fileNameEl) fileNameEl.textContent = file.name;
            if (fileSizeEl) fileSizeEl.textContent = formatFileSize(file.size);
            
            // 根据文件类型设置图标
            if (fileIcon) {
                if (file.type.startsWith('image/')) {
                    fileIcon.textContent = '🖼️';
                } else if (file.type.startsWith('video/')) {
                    fileIcon.textContent = '🎥';
                } else if (file.type.startsWith('audio/')) {
                    fileIcon.textContent = '🎵';
                } else {
                    fileIcon.textContent = '📄';
                }
            }
            
            if (fileInfo) {
                fileInfo.style.display = 'flex';
            }
        }
        
        function updateFileStatus(status, message) {
            const statusEl = container.querySelector('.file-status');
            if (statusEl) {
                statusEl.textContent = message;
                statusEl.className = 'file-status ' + status;
            }
        }
        
        
        function getFileTypeFromUrl(url) {
            const extension = url.split('.').pop().toLowerCase();
            const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
            const videoExts = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'];
            const audioExts = ['mp3', 'wav', 'ogg', 'aac', 'flac'];
            
            if (imageExts.includes(extension)) {
                return 'image';
            } else if (videoExts.includes(extension)) {
                return 'video';
            } else if (audioExts.includes(extension)) {
                return 'audio';
            } else {
                return 'other';
            }
        }
        
        function getFileNameFromUrl(url) {
            return url.split('/').pop() || 'unknown';
        }
        
        function showFileInfoFromUrl(fileName, fileType) {
            const fileNameEl = container.querySelector('.file-name');
            const fileSizeEl = container.querySelector('.file-size');
            const fileIcon = container.querySelector('.file-icon');
            
            if (fileNameEl) fileNameEl.textContent = fileName;
            if (fileSizeEl) fileSizeEl.textContent = '已上传';
            
            // 根据文件类型设置图标
            if (fileIcon) {
                if (fileType === 'image') {
                    fileIcon.textContent = '🖼️';
                } else if (fileType === 'video') {
                    fileIcon.textContent = '🎥';
                } else if (fileType === 'audio') {
                    fileIcon.textContent = '🎵';
                } else {
                    fileIcon.textContent = '📄';
                }
            }
            
            if (fileInfo) {
                fileInfo.style.display = 'flex';
                updateFileStatus('success', '已上传');
            }
        }
        
        function showPreviewFromUrl(url, fileType, fileName) {
            return new Promise((resolve, reject) => {
                // 清空预览容器
                previewContainer.innerHTML = '';
                
                if (fileType === 'image') {
                    // 图片预览 - 可点击全屏
                    const img = document.createElement('img');
                    img.src = url;
                    img.alt = fileName;
                    img.style.cursor = 'pointer';
                    img.title = '点击全屏查看';
                    
                    img.onload = () => resolve();
                    img.onerror = () => reject(new Error('图片加载失败'));
                    
                    // 添加全屏按钮
                    const fullscreenBtn = document.createElement('button');
                    fullscreenBtn.type = 'button';
                    fullscreenBtn.innerHTML = '⛶';
                    fullscreenBtn.style.cssText = `
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        background: rgba(0,0,0,0.7);
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                        cursor: pointer;
                        font-size: 16px;
                        z-index: 10;
                    `;
                    fullscreenBtn.title = '全屏查看';
                    
                    const imgContainer = document.createElement('div');
                    imgContainer.style.position = 'relative';
                    imgContainer.style.display = 'inline-block';
                    imgContainer.appendChild(img);
                    imgContainer.appendChild(fullscreenBtn);
                    
                    // 点击图片或按钮都可以全屏
                    const openImageFullscreen = (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        requestFullscreen(img);
                    };
                    img.onclick = openImageFullscreen;
                    fullscreenBtn.onclick = openImageFullscreen;
                    
                    previewContainer.appendChild(imgContainer);
                } else if (fileType === 'video') {
                    // 创建单一video元素
                    currentVideoElement = createVideoElement(url, fileName);
                    previewContainer.appendChild(currentVideoElement);
                    
                    // 视频加载完成
                    const video = currentVideoElement.querySelector('video');
                    video.onloadedmetadata = () => resolve();
                    video.onerror = () => reject(new Error('视频加载失败'));
                } else {
                    // 其他文件类型显示下载链接
                    const link = document.createElement('a');
                    link.href = url;
                    link.target = '_blank';
                    link.textContent = `🔗 查看文件: ${fileName}`;
                    previewContainer.appendChild(link);
                    resolve();
                }
            });
        }

        function createVideoElement(url, fileName) {
            const video = document.createElement('video');
            video.src = url;
            video.controls = true;
            video.preload = 'metadata';
            video.style.maxWidth = '100%';
            video.style.maxHeight = '300px';
            video.style.borderRadius = '8px';
            video.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            
            // 添加全屏按钮
            const fullscreenBtn = document.createElement('button');
            fullscreenBtn.type = 'button'; // 明确指定按钮类型
            fullscreenBtn.innerHTML = '⛶';
            fullscreenBtn.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(0,0,0,0.7);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                cursor: pointer;
                font-size: 16px;
                z-index: 10;
            `;
            fullscreenBtn.title = '全屏播放';
            
            const videoContainer = document.createElement('div');
            videoContainer.style.position = 'relative';
            videoContainer.style.display = 'inline-block';
            videoContainer.appendChild(video);
            videoContainer.appendChild(fullscreenBtn);
            
            // 点击全屏按钮
            fullscreenBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                requestFullscreen(video);
            };
            
            // 双击视频全屏
            video.ondblclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                requestFullscreen(video);
            };
            
            return videoContainer;
        }

        function showPreview(file, url) {
            if (file.type.startsWith('image/')) {
                // 图片预览 - 可点击全屏
                const img = document.createElement('img');
                img.src = url;
                img.alt = file.name;
                img.style.cursor = 'pointer';
                img.title = '点击全屏查看';
                
                // 添加全屏按钮
                const fullscreenBtn = document.createElement('button');
                fullscreenBtn.type = 'button'; // 明确指定按钮类型
                fullscreenBtn.innerHTML = '⛶';
                fullscreenBtn.style.cssText = `
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    z-index: 10;
                `;
                fullscreenBtn.title = '全屏查看';
                
                const imgContainer = document.createElement('div');
                imgContainer.style.position = 'relative';
                imgContainer.style.display = 'inline-block';
                imgContainer.appendChild(img);
                imgContainer.appendChild(fullscreenBtn);
                
                // 点击图片或按钮都可以全屏
                const openImageFullscreen = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    requestFullscreen(img);
                };
                img.onclick = openImageFullscreen;
                fullscreenBtn.onclick = openImageFullscreen;
                
                previewContainer.appendChild(imgContainer);
            } else if (file.type.startsWith('video/')) {
                // 创建单一video元素
                currentVideoElement = createVideoElement(url, file.name);
                previewContainer.appendChild(currentVideoElement);
            } else {
                // 其他文件类型显示下载链接
                const link = document.createElement('a');
                link.href = url;
                link.target = '_blank';
                link.textContent = `🔗 查看文件: ${file.name}`;
                previewContainer.appendChild(link);
            }
        }
    });
});

// 全屏状态变化监听
document.addEventListener('fullscreenchange', function() {
    console.log('全屏状态变化:', document.fullscreenElement ? '进入全屏' : '退出全屏');
});

document.addEventListener('webkitfullscreenchange', function() {
    console.log('Webkit全屏状态变化:', document.webkitFullscreenElement ? '进入全屏' : '退出全屏');
});

document.addEventListener('mozfullscreenchange', function() {
    console.log('Mozilla全屏状态变化:', document.mozFullScreenElement ? '进入全屏' : '退出全屏');
});

document.addEventListener('msfullscreenchange', function() {
    console.log('MS全屏状态变化:', document.msFullscreenElement ? '进入全屏' : '退出全屏');
});