/**
 * Модуль работы с аудиозаписью приёма (Demo версия)
 * Имитирует запись и транскрибацию для презентации
 */

const AudioHandler = {
    appointmentId: null,
    isRecording: false,
    recordingStartTime: null,
    timerInterval: null,
    
    /**
     * Инициализация
     */
    init(appointmentId) {
        this.appointmentId = appointmentId;
        this.isRecording = false;
        this.recordingStartTime = null;
        
        // Загружаем данные из БД
        this.loadFromDatabase();
    },
    
    /**
     * Загрузить данные из базы данных
     */
    async loadFromDatabase() {
        try {
            const audioResponse = await fetch(`/api/audio/by-appointment/${this.appointmentId}`);
            
            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                
                // Если есть транскрипция - показываем её
                if (audioData.transcription_text && audioData.transcription_status === 'completed') {
                    this.displayTranscriptionResult(audioData.transcription_text, audioData.id);
                    return;
                }
            }
            
            // Если транскрипции нет - показываем кнопку записи
            this.renderRecordingUI();
            
        } catch (error) {
            console.error('AudioHandler: ошибка загрузки из БД:', error);
            this.renderRecordingUI();
        }
    },
    
    /**
     * Отрендерить UI записи
     */
    renderRecordingUI() {
        const html = `
            <div id="recording-section" class="bg-white border-2 border-purple-200 rounded-lg p-6">
                <div class="text-center">
                    <div id="recording-indicator" class="hidden mb-6">
                        <div class="flex items-center justify-center space-x-3 mb-4">
                            <div class="recording-pulse"></div>
                            <span class="text-lg font-semibold text-red-600">Идёт запись...</span>
                        </div>
                        <div id="recording-timer" class="text-4xl font-mono font-bold text-gray-800 mb-4">00:00</div>
                        <div class="flex items-center justify-center space-x-2 text-sm text-gray-500">
                            <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" class="text-red-500">
                                <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd"/>
                            </svg>
                            <span>Записывается аудио приёма</span>
                        </div>
                    </div>
                    
                    <div id="start-recording-section">
                        <div class="mb-6">
                            <svg width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="mx-auto text-purple-400">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">Запись приёма</h3>
                        <p class="text-gray-600 mb-6">Начните запись разговора с пациентом для автоматического создания стенограммы</p>
                    </div>
                    
                    <button id="record-btn" class="w-full max-w-md px-8 py-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl hover:from-purple-600 hover:to-blue-600 font-medium transition-all flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl mx-auto">
                        <svg id="record-icon" width="24" height="24" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd"/>
                        </svg>
                        <span id="record-btn-text">Начать запись</span>
                    </button>
                </div>
            </div>
            
            <div id="transcription-display" class="hidden mt-6"></div>
        `;
        
        $('#audio-upload-section').html(html);
        
        // Обработчик кнопки записи
        $('#record-btn').on('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
    },
    
    /**
     * Начать "запись"
     */
    startRecording() {
        this.isRecording = true;
        this.recordingStartTime = Date.now();
        
        // Скрываем секцию старта, показываем индикатор
        $('#start-recording-section').addClass('hidden');
        $('#recording-indicator').removeClass('hidden');
        
        // Меняем кнопку на "Завершить"
        $('#record-btn').removeClass('from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600')
                        .addClass('from-red-500 to-red-600 hover:from-red-600 hover:to-red-700');
        $('#record-icon').html('<rect x="6" y="6" width="8" height="8" fill="currentColor"/>');
        $('#record-btn-text').text('Завершить запись');
        
        // Запускаем таймер
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            $('#recording-timer').text(`${minutes}:${seconds}`);
        }, 1000);
        
        Utils.showToast('Запись начата', 'success');
    },
    
    /**
     * Остановить "запись" и начать имитацию обработки
     */
    async stopRecording() {
        this.isRecording = false;
        
        // Останавливаем таймер
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        Utils.showToast('Запись завершена. Обработка...', 'info');
        
        // Показываем экран загрузки
        this.showProcessingScreen();
    },
    
    /**
     * Показать экран обработки с этапами (~30 секунд)
     */
    async showProcessingScreen() {
        const stages = [
            { text: 'Загрузка аудио...', duration: 8000, progress: 30 },
            { text: 'Извлечение речи...', duration: 12000, progress: 65 },
            { text: 'Формирование стенограммы...', duration: 10000, progress: 95 }
        ];
        
        const html = `
            <div class="bg-white border-2 border-purple-200 rounded-lg p-8">
                <div class="text-center">
                    <div class="mb-6">
                        <div class="processing-spinner mx-auto"></div>
                    </div>
                    
                    <h3 id="processing-stage" class="text-xl font-semibold text-gray-900 mb-2">Подготовка...</h3>
                    <p id="processing-substage" class="text-sm text-gray-500 mb-6">Инициализация системы обработки</p>
                    
                    <div class="max-w-md mx-auto mb-6">
                        <div class="progress-bar h-3 rounded-full">
                            <div id="processing-progress" class="progress-bar-fill h-full rounded-full transition-all duration-1000" style="width: 5%"></div>
                        </div>
                    </div>
                    
                    <div id="processing-log" class="text-left bg-gray-50 rounded-lg p-4 max-w-md mx-auto text-xs font-mono text-gray-600 max-h-32 overflow-y-auto">
                        <div class="log-entry">[${this.getTimestamp()}] Начало обработки...</div>
                    </div>
                </div>
            </div>
        `;
        
        $('#recording-section').html(html);
        
        // Добавляем CSS для спиннера
        if (!$('#processing-spinner-style').length) {
            $('head').append(`
                <style id="processing-spinner-style">
                    .processing-spinner {
                        width: 64px;
                        height: 64px;
                        border: 4px solid #E5E7EB;
                        border-top-color: #8B5CF6;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    }
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                    .recording-pulse {
                        width: 16px;
                        height: 16px;
                        background-color: #EF4444;
                        border-radius: 50%;
                        animation: pulse 1.5s ease-in-out infinite;
                    }
                    @keyframes pulse {
                        0%, 100% { opacity: 1; transform: scale(1); }
                        50% { opacity: 0.5; transform: scale(1.2); }
                    }
                </style>
            `);
        }
        
        // Проходим по этапам
        let currentProgress = 5;
        
        for (let i = 0; i < stages.length; i++) {
            const stage = stages[i];
            
            // Обновляем UI
            $('#processing-stage').text(stage.text);
            this.addLogEntry(stage.text);
            
            // Анимируем прогресс
            const targetProgress = stage.progress;
            const progressStep = (targetProgress - currentProgress) / (stage.duration / 500);
            
            // Добавляем промежуточные сообщения
            const substages = this.getSubstages(i);
            let substageIndex = 0;
            
            const progressInterval = setInterval(() => {
                currentProgress = Math.min(currentProgress + progressStep, targetProgress);
                $('#processing-progress').css('width', `${currentProgress}%`);
                
                // Меняем подэтап
                if (substageIndex < substages.length && Math.random() > 0.7) {
                    $('#processing-substage').text(substages[substageIndex]);
                    this.addLogEntry(substages[substageIndex]);
                    substageIndex++;
                }
            }, 500);
            
            await this.sleep(stage.duration);
            clearInterval(progressInterval);
            currentProgress = targetProgress;
            $('#processing-progress').css('width', `${currentProgress}%`);
        }
        
        // Завершение
        $('#processing-stage').text('Готово!');
        $('#processing-substage').text('Стенограмма успешно сформирована');
        $('#processing-progress').css('width', '100%');
        this.addLogEntry('Обработка завершена успешно');
        
        await this.sleep(1000);
        
        // Загружаем транскрипцию с сервера
        await this.loadMockTranscription();
    },
    
    /**
     * Получить подэтапы для каждого этапа
     */
    getSubstages(stageIndex) {
        const allSubstages = [
            // Загрузка аудио
            ['Чтение аудиопотока...', 'Конвертация формата...', 'Нормализация громкости...'],
            // Извлечение речи
            ['Определение голосов...', 'Разделение каналов...', 'Фильтрация шумов...', 'Сегментация речи...'],
            // Формирование стенограммы
            ['Распознавание слов...', 'Определение спикеров...', 'Форматирование текста...']
        ];
        return allSubstages[stageIndex] || [];
    },
    
    /**
     * Добавить запись в лог
     */
    addLogEntry(text) {
        const logEntry = `<div class="log-entry">[${this.getTimestamp()}] ${text}</div>`;
        $('#processing-log').append(logEntry);
        $('#processing-log').scrollTop($('#processing-log')[0].scrollHeight);
    },
    
    /**
     * Получить timestamp для лога
     */
    getTimestamp() {
        const now = new Date();
        return now.toTimeString().split(' ')[0];
    },
    
    /**
     * Задержка
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    /**
     * Загрузить mock-транскрипцию с сервера
     */
    async loadMockTranscription() {
        try {
            const response = await fetch(`/api/audio/mock-transcription?appointment_id=${this.appointmentId}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Ошибка загрузки транскрипции');
            }
            
            const result = await response.json();
            
            // Получаем audio_id
            const audioResponse = await fetch(`/api/audio/by-appointment/${this.appointmentId}`);
            let audioId = null;
            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                audioId = audioData.id;
            }
            
            Utils.showToast('Стенограмма успешно сформирована!', 'success');
            
            // Отображаем результат
            this.displayTranscriptionResult(result.transcription_text, audioId);
            
        } catch (error) {
            console.error('Ошибка загрузки транскрипции:', error);
            Utils.showToast('Ошибка формирования стенограммы', 'error');
            this.renderRecordingUI();
        }
    },
    
    /**
     * Отобразить результат транскрипции
     */
    displayTranscriptionResult(text, audioId) {
        const html = `
            <div class="bg-white border-2 border-purple-200 rounded-lg p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="mr-2 text-purple-500">
                            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"/>
                        </svg>
                        Стенограмма приёма
                    </h3>
                    <span class="badge badge-cyan">Распознано</span>
                </div>
                
                <!-- Редактируемая транскрипция -->
                <div class="mb-4">
                    <textarea 
                        id="transcription-text-area" 
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                        rows="15"
                        placeholder="Текст стенограммы..."
                    >${this.escapeHtml(text)}</textarea>
                </div>
                
                <!-- Кнопки действий -->
                <div class="flex flex-col lg:flex-row space-y-3 lg:space-y-0 lg:space-x-4">
                    <button id="clear-conversation-btn" class="w-full lg:w-auto px-6 py-3 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 font-medium flex items-center justify-center space-x-2">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
                        </svg>
                        <span>Очистить разговор</span>
                    </button>
                    <button id="save-transcription-btn" class="w-full lg:w-auto px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium flex items-center justify-center space-x-2">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z"/>
                        </svg>
                        <span>Сохранить изменения</span>
                    </button>
                    <button id="extract-anamnesis-btn" class="w-full lg:w-auto px-6 py-3 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg hover:from-green-600 hover:to-teal-600 font-medium flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                        </svg>
                        <span>Извлечь анамнез</span>
                    </button>
                </div>
            </div>
        `;
        
        // Очищаем контейнер
        const container = $('#audio-upload-section');
        container.html(html);
        
        // Обработчик очистки разговора
        $('#clear-conversation-btn').on('click', async () => {
            await this.clearConversation();
        });
        
        // Обработчик сохранения
        $('#save-transcription-btn').on('click', async () => {
            await this.saveTranscription(audioId);
        });
        
        // Обработчик извлечения анамнеза
        $('#extract-anamnesis-btn').on('click', async () => {
            const saved = await this.saveTranscription(audioId);
            if (saved) {
                await this.extractAnamnesis();
            }
        });
    },
    
    /**
     * Очистить разговор и вернуться к записи
     */
    async clearConversation() {
        if (!confirm('Вы уверены? Стенограмма будет удалена.')) {
            return;
        }
        
        const btn = $('#clear-conversation-btn');
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Удаление...</span>
        `);
        
        try {
            const response = await fetch(`/api/audio/by-appointment/${this.appointmentId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка удаления');
            }
            
            Utils.showToast('Стенограмма удалена', 'success');
            
            // Возвращаемся к UI записи
            this.renderRecordingUI();
            
        } catch (error) {
            console.error('Ошибка удаления:', error);
            Utils.showToast(error.message || 'Ошибка удаления', 'error');
            
            btn.prop('disabled', false).html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <span>Очистить разговор</span>
            `);
        }
    },
    
    /**
     * Экранировать HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    /**
     * Сохранить изменения в транскрипции
     */
    async saveTranscription(audioId) {
        if (!audioId) {
            Utils.showToast('Ошибка: ID аудиофайла не найден', 'error');
            return false;
        }
        
        const btn = $('#save-transcription-btn');
        const text = $('#transcription-text-area').val();
        
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Сохранение...</span>
        `);
        
        try {
            const response = await fetch(`/api/audio/${audioId}/transcription?transcription_text=${encodeURIComponent(text)}`, {
                method: 'PUT'
            });
            
            if (!response.ok) {
                throw new Error('Ошибка сохранения');
            }
            
            Utils.showToast('Изменения сохранены', 'success');
            
            btn.prop('disabled', false).html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z"/>
                </svg>
                <span>Сохранить изменения</span>
            `);
            
            return true;
            
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            Utils.showToast('Ошибка сохранения', 'error');
            
            btn.prop('disabled', false).html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z"/>
                </svg>
                <span>Сохранить изменения</span>
            `);
            
            return false;
        }
    },
    
    /**
     * Извлечь анамнез из транскрипции
     */
    async extractAnamnesis() {
        const btn = $('#extract-anamnesis-btn');
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Анализ и извлечение данных...</span>
        `);
        
        try {
            const response = await fetch(`/api/audio/extract-anamnesis-by-appointment?appointment_id=${this.appointmentId}`, {
                method: 'POST'
            });
            
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
                <span>Анамнез извлечён</span>
            `);
            
            // Добавляем подсказку
            const hint = `
                <div class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div class="flex items-start space-x-3">
                        <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20" class="text-green-500 flex-shrink-0">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                        <div class="flex-1">
                            <p class="text-sm text-green-800 font-semibold mb-1">Данные успешно извлечены!</p>
                            <p class="text-xs text-gray-600 mb-3">
                                • Цель обращения: заполнена<br>
                                • Жалобы пациента: заполнены<br>
                                • Анамнез: заполнен
                            </p>
                            <button id="goto-anamnesis-btn" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium">
                                Перейти к анамнезу
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            $('#audio-upload-section').append(hint);
            
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
                <span>Извлечь анамнез</span>
            `);
        }
    }
};
