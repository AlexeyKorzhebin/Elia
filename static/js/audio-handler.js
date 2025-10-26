/**
 * Модуль работы с аудиофайлами
 */

const AudioHandler = {
    appointmentId: null,
    audioData: null,
    hasGeneratedConversation: false,
    
    /**
     * Инициализация
     */
    init(appointmentId) {
        this.appointmentId = appointmentId;
        this.hasGeneratedConversation = false;
        this.checkExistingAudio();
    },
    
    /**
     * Проверить, есть ли уже загруженный аудиофайл или транскрипция
     */
    async checkExistingAudio() {
        try {
            // Пытаемся получить данные о существующем аудиофайле
            const response = await fetch(`/api/appointments/${this.appointmentId}`);
            if (!response.ok) {
                this.renderInitialUI();
                return;
            }
            
            const appointment = await response.json();
            
            // Проверяем, есть ли у приёма аудиофайл через CRUD
            // Пока просто рендерим начальный UI
            this.renderInitialUI();
            
        } catch (error) {
            console.error('Ошибка проверки аудио:', error);
            this.renderInitialUI();
        }
    },
    
    /**
     * Отрендерить начальный UI с кнопкой генерации
     */
    renderInitialUI() {
        const html = `
            <!-- Кнопка генерации mock-разговора -->
            <div class="mb-6">
                <button id="generate-conversation-btn" class="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:from-purple-600 hover:to-blue-600 font-medium transition-all flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                        <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                    </svg>
                    <span>Сгенерировать разговор (AI)</span>
                </button>
                <p class="mt-2 text-xs text-gray-500 text-center">Или загрузите аудиофайл ниже</p>
            </div>
            
            <div id="transcription-display" class="hidden mb-6"></div>
            
            <div id="upload-section">
                ${this.getUploadFormHTML()}
            </div>
            
            <div id="audio-player-section" class="hidden"></div>
        `;
        
        $('#audio-upload-section').html(html);
        
        // Обработчик кнопки генерации
        $('#generate-conversation-btn').on('click', () => {
            this.generateConversation();
        });
        
        this.initUploadHandlers();
    },
    
    /**
     * Получить HTML формы загрузки
     */
    getUploadFormHTML() {
        return `
            <div id="upload-area" class="drop-zone">
                <input type="file" id="audio-file-input" accept="audio/mp3,audio/wav" class="hidden">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
                <p class="mt-2 text-sm text-gray-600">Перетащите аудиофайл сюда или</p>
                <button type="button" id="select-file-btn" class="mt-2 px-4 py-2 text-sm text-elia-lavender hover:text-opacity-80 font-medium">
                    Выберите файл
                </button>
                <p class="mt-2 text-xs text-gray-500">Поддерживаются форматы: MP3, WAV (макс. 50MB)</p>
            </div>
        `;
    },
    
    /**
     * Сгенерировать разговор через OpenAI
     */
    async generateConversation() {
        const btn = $('#generate-conversation-btn');
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Генерация разговора через AI...</span>
        `);
        
        try {
            const response = await fetch(`/api/audio/generate-mock-conversation?appointment_id=${this.appointmentId}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка генерации разговора');
            }
            
            const result = await response.json();
            
            Utils.showToast('Разговор успешно сгенерирован!', 'success');
            
            // Сохраняем данные о "виртуальном" аудиофайле
            this.hasGeneratedConversation = true;
            
            // Находим ID созданного аудиофайла через повторный запрос appointment
            const appointmentResponse = await fetch(`/api/appointments/${this.appointmentId}`);
            if (appointmentResponse.ok) {
                const appointment = await appointmentResponse.json();
                // Здесь нужно получить audio_id, но пока используем result
            }
            
            // Отображаем транскрипцию
            this.displayTranscription(result.transcription_text);
            
            // Скрываем кнопку генерации
            btn.parent().remove();
            
        } catch (error) {
            console.error('Ошибка генерации:', error);
            Utils.showToast(error.message || 'Ошибка генерации разговора', 'error');
            btn.prop('disabled', false).html(`
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                    <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                </svg>
                <span>Сгенерировать разговор (AI)</span>
            `);
        }
    },
    
    /**
     * Отобразить транскрипцию с кнопкой извлечения анамнеза
     */
    displayTranscription(text) {
        const html = `
            <div class="bg-white border-2 border-purple-200 rounded-lg p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="mr-2 text-purple-500">
                            <path fill-rule="evenodd" d="M7 2a1 1 0 011 1v1h3a1 1 0 110 2H9.578a18.87 18.87 0 01-1.724 4.78c.29.354.596.696.914 1.026a1 1 0 11-1.44 1.389c-.188-.196-.373-.396-.554-.6a19.098 19.098 0 01-3.107 3.567 1 1 0 01-1.334-1.49 17.087 17.087 0 003.13-3.733 18.992 18.992 0 01-1.487-2.494 1 1 0 111.79-.89c.234.47.489.928.764 1.372.417-.934.752-1.913.997-2.927H3a1 1 0 110-2h3V3a1 1 0 011-1zm6 6a1 1 0 01.894.553l2.991 5.982a.869.869 0 01.02.037l.99 1.98a1 1 0 11-1.79.894L15.383 16h-4.764l-.723 1.447a1 1 0 11-1.788-.894l.99-1.98.019-.038 2.99-5.982A1 1 0 0113 8zm-1.382 6h2.764L13 11.236 11.618 14z" clip-rule="evenodd"/>
                        </svg>
                        Транскрипция разговора
                    </h3>
                    <span class="badge badge-cyan">Сгенерировано AI</span>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 mb-4 max-h-96 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-sm text-gray-700 font-mono">${text}</pre>
                </div>
                <button id="extract-anamnesis-btn" class="w-full px-6 py-3 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg hover:from-green-600 hover:to-teal-600 font-medium transition-all flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                        <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                    </svg>
                    <span>Извлечь анамнез из разговора</span>
                </button>
            </div>
        `;
        
        $('#transcription-display').removeClass('hidden').html(html);
        
        // Скрываем секцию загрузки файлов
        $('#upload-section').hide();
        
        // Обработчик кнопки извлечения анамнеза
        $('#extract-anamnesis-btn').on('click', async () => {
            await this.extractAnamnesis();
        });
    },
    
    /**
     * Извлечь анамнез из транскрипции
     */
    async extractAnamnesis() {
        const btn = $('#extract-anamnesis-btn');
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Анализ разговора и извлечение данных...</span>
        `);
        
        try {
            // Сначала нужно получить audio_id
            // Для этого запросим appointment и найдём связанный audio
            const appointmentResponse = await fetch(`/api/appointments/${this.appointmentId}`);
            if (!appointmentResponse.ok) {
                throw new Error('Не удалось получить данные приёма');
            }
            
            // Получаем audio_id через поиск (временное решение)
            // В идеале нужно добавить audio_file в ответ appointment
            // Пока используем прямой запрос с проверкой существования
            
            // Попробуем получить аудио напрямую (предполагаем, что оно есть)
            // Используем fetch с обработкой ошибки
            let audioId = null;
            
            // Здесь нужен более элегантный способ получения audio_id
            // Пока сделаем через попытку извлечения напрямую с appointment_id
            const response = await fetch(`/api/audio/extract-anamnesis-by-appointment?appointment_id=${this.appointmentId}`, {
                method: 'POST'
            });
            
            // Если такого endpoint нет, используем обходной путь
            if (response.status === 404) {
                // Создаём временный endpoint или используем существующую логику
                throw new Error('Не удалось найти аудиофайл для извлечения анамнеза');
            }
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка извлечения анамнеза');
            }
            
            const report = await response.json();
            
            // Обновляем данные отчёта в PatientCard
            PatientCard.reportData = report;
            
            Utils.showToast('Анамнез успешно извлечён и сохранён!', 'success');
            
            btn.html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="text-green-200">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span>Анамнез успешно извлечён</span>
            `);
            
            // Добавляем подсказку о переходе на вкладку Анамнез
            const hint = `
                <div class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p class="text-sm text-green-800 mb-2">
                        <strong>Данные успешно извлечены и сохранены!</strong>
                    </p>
                    <p class="text-xs text-gray-600 mb-3">
                        • Цель обращения: заполнена<br>
                        • Жалобы пациента: заполнены<br>
                        • Анамнез: заполнен
                    </p>
                    <button id="goto-anamnesis-btn" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium">
                        Перейти к анамнезу
                    </button>
                </div>
            `;
            
            $('#transcription-display').append(hint);
            
            $('#goto-anamnesis-btn').on('click', () => {
                PatientCard.switchTab('anamnesis');
            });
            
        } catch (error) {
            console.error('Ошибка извлечения анамнеза:', error);
            Utils.showToast(error.message || 'Ошибка извлечения анамнеза', 'error');
            btn.prop('disabled', false).html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                    <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                </svg>
                <span>Извлечь анамнез из разговора</span>
            `);
        }
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
                        <svg class="w-10 h-10 text-elia-lavender" fill="currentColor" viewBox="0 0 20 20">
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

