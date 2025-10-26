/**
 * Модуль работы с аудиофайлами
 */

const AudioHandler = {
    appointmentId: null,
    audioData: null,
    
    /**
     * Инициализация
     */
    init(appointmentId) {
        this.appointmentId = appointmentId;
        this.checkExistingAudio();
    },
    
    /**
     * Проверить, есть ли уже загруженный аудиофайл
     */
    async checkExistingAudio() {
        try {
            const response = await fetch(`/api/appointments/${this.appointmentId}`);
            if (!response.ok) return;
            
            const appointment = await response.json();
            
            // Проверяем, есть ли аудиофайл (нужно добавить это поле в API)
            // Пока просто рендерим форму загрузки
            this.renderUploadForm();
            
        } catch (error) {
            console.error('Ошибка проверки аудио:', error);
            this.renderUploadForm();
        }
    },
    
    /**
     * Отрендерить форму загрузки
     */
    renderUploadForm() {
        const html = `
            <div id="upload-area" class="drop-zone mb-6">
                <input type="file" id="audio-file-input" accept="audio/mp3,audio/wav" class="hidden">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
                <p class="mt-2 text-sm text-gray-600">Перетащите аудиофайл сюда или</p>
                <button type="button" id="select-file-btn" class="mt-2 px-4 py-2 text-sm text-elia-purple hover:text-elia-purple-700 font-medium">
                    Выберите файл
                </button>
                <p class="mt-2 text-xs text-gray-500">Поддерживаются форматы: MP3, WAV (макс. 50MB)</p>
            </div>
            
            <div id="audio-player-section" class="hidden">
                <!-- Плеер появится после загрузки -->
            </div>
            
            <div id="transcription-section" class="hidden mt-6">
                <!-- Транскрипция появится после обработки -->
            </div>
        `;
        
        $('#audio-upload-section').html(html);
        this.initUploadHandlers();
    },
    
    /**
     * Инициализировать обработчики загрузки
     */
    initUploadHandlers() {
        const dropZone = $('#upload-area');
        const fileInput = $('#audio-file-input');
        
        // Клик по кнопке выбора файла
        $('#select-file-btn').on('click', () => {
            fileInput.click();
        });
        
        // Клик по drop zone
        dropZone.on('click', (e) => {
            if (e.target.id !== 'select-file-btn') {
                fileInput.click();
            }
        });
        
        // Выбор файла через input
        fileInput.on('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadFile(file);
            }
        });
        
        // Drag & Drop
        dropZone.on('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.addClass('drag-over');
        });
        
        dropZone.on('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.removeClass('drag-over');
        });
        
        dropZone.on('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.removeClass('drag-over');
            
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });
    },
    
    /**
     * Загрузить файл на сервер
     */
    async uploadFile(file) {
        // Проверка формата
        const allowedTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/wave'];
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav)$/i)) {
            Utils.showToast('Неподдерживаемый формат файла. Используйте MP3 или WAV', 'error');
            return;
        }
        
        // Проверка размера (50MB)
        if (file.size > 52428800) {
            Utils.showToast('Файл слишком большой. Максимальный размер: 50MB', 'error');
            return;
        }
        
        const uploadArea = $('#upload-area');
        uploadArea.html(`
            <div class="text-center py-8">
                <div class="spinner mx-auto mb-4"></div>
                <p class="text-gray-600">Загрузка файла...</p>
                <div class="progress-bar mt-4 max-w-xs mx-auto">
                    <div class="progress-bar-fill" style="width: 0%"></div>
                </div>
            </div>
        `);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`/api/audio/upload?appointment_id=${this.appointmentId}`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка загрузки файла');
            }
            
            this.audioData = await response.json();
            Utils.showToast('Файл успешно загружен', 'success');
            
            this.renderAudioPlayer();
            
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            Utils.showToast(error.message || 'Ошибка загрузки файла', 'error');
            this.renderUploadForm();
        }
    },
    
    /**
     * Отрендерить аудиоплеер
     */
    renderAudioPlayer() {
        $('#upload-area').remove();
        
        const html = `
            <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <svg class="w-10 h-10 text-elia-purple" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                        </svg>
                        <div>
                            <p class="font-medium text-gray-900">${this.audioData.filename}</p>
                            <p class="text-sm text-gray-500">${(this.audioData.file_size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                    </div>
                </div>
                
                <audio controls class="w-full mb-4">
                    <source src="/api/audio/${this.audioData.id}/download" type="audio/mpeg">
                    Ваш браузер не поддерживает аудио элемент.
                </audio>
                
                <button id="transcribe-btn" class="btn-gradient w-full">
                    <span>Транскрибировать</span>
                </button>
            </div>
            
            <div id="transcription-result" class="hidden"></div>
        `;
        
        $('#audio-player-section').removeClass('hidden').html(html);
        
        // Обработчик кнопки транскрибации
        $('#transcribe-btn').on('click', () => {
            this.transcribeAudio();
        });
    },
    
    /**
     * Транскрибировать аудио
     */
    async transcribeAudio() {
        const btn = $('#transcribe-btn');
        btn.prop('disabled', true);
        
        // Показываем прогресс
        const progressHtml = `
            <div class="bg-white border border-gray-200 rounded-lg p-6">
                <div class="flex items-center space-x-4 mb-4">
                    <div class="spinner"></div>
                    <div class="flex-1">
                        <p class="font-medium text-gray-900">Обработка аудио...</p>
                        <p class="text-sm text-gray-500">Это может занять несколько секунд</p>
                    </div>
                </div>
                <div class="progress-bar">
                    <div id="transcribe-progress" class="progress-bar-fill" style="width: 0%"></div>
                </div>
            </div>
        `;
        
        $('#transcription-result').removeClass('hidden').html(progressHtml);
        
        // Анимация прогресса
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 2;
            if (progress <= 100) {
                $('#transcribe-progress').css('width', `${progress}%`);
            }
        }, 120);
        
        try {
            const response = await fetch(`/api/audio/${this.audioData.id}/transcribe`, {
                method: 'POST'
            });
            
            clearInterval(progressInterval);
            $('#transcribe-progress').css('width', '100%');
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка транскрибации');
            }
            
            const result = await response.json();
            Utils.showToast(result.message, 'success');
            
            this.renderTranscription(result.transcription_text);
            
        } catch (error) {
            clearInterval(progressInterval);
            console.error('Ошибка транскрибации:', error);
            Utils.showToast(error.message || 'Ошибка транскрибации', 'error');
            $('#transcription-result').addClass('hidden');
            btn.prop('disabled', false);
        }
    },
    
    /**
     * Отрендерить транскрипцию
     */
    renderTranscription(text) {
        const html = `
            <div class="bg-white border border-gray-200 rounded-lg p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">Транскрипция</h3>
                    <span class="badge badge-cyan">Обработано (MVP)</span>
                </div>
                <div class="prose max-w-none">
                    <pre class="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">${text || 'Транскрипция пуста'}</pre>
                </div>
            </div>
        `;
        
        $('#transcription-result').html(html);
        $('#transcribe-btn').remove();
    }
};

