/**
 * Модуль работы с аудиофайлами
 */

const AudioHandler = {
    appointmentId: null,
    
    /**
     * Инициализация - всегда загружаем данные из БД
     */
    init(appointmentId) {
        this.appointmentId = appointmentId;
        
        // Всегда загружаем актуальное состояние из базы данных
        this.loadFromDatabase();
    },
    
    /**
     * Загрузить данные из базы данных
     */
    async loadFromDatabase() {
        try {
            // Запрашиваем аудиофайл для этого приёма
            const audioResponse = await fetch(`/api/audio/by-appointment/${this.appointmentId}`);
            
            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                
                // Если есть транскрипция в БД - показываем её
                // Важно: enum возвращается как lowercase значение ("completed"), а не uppercase имя ("COMPLETED")
                if (audioData.transcription_text && audioData.transcription_status === 'completed') {
                    this.displayEditableTranscription(audioData.transcription_text, audioData.id);
                    return;
                }
            }
            
            // Если транскрипции нет - показываем кнопку генерации
            this.renderInitialUI();
            
        } catch (error) {
            console.error('AudioHandler: ошибка загрузки из БД:', error);
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
        const originalHTML = btn.html();
        
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
            
            // Получаем audio_id из БД
            const audioResponse = await fetch(`/api/audio/by-appointment/${this.appointmentId}`);
            let audioId = null;
            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                audioId = audioData.id;
            }
            
            // Отображаем транскрипцию для редактирования (это пересоздаст кнопку)
            this.displayEditableTranscription(result.transcription_text, audioId);
            
        } catch (error) {
            console.error('Ошибка генерации:', error);
            Utils.showToast(error.message || 'Ошибка генерации разговора', 'error');
            
            // Восстанавливаем исходное состояние кнопки
            btn.prop('disabled', false).html(originalHTML);
        }
    },
    
    /**
     * Очистить транскрипцию
     */
    async clearTranscription() {
        if (!confirm('Вы уверены? Разговор будет удалён из базы данных.')) {
            return;
        }
        
        const btn = $('#clear-transcription-btn');
        const originalHTML = btn.html();
        
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
            
            Utils.showToast('Разговор успешно удалён', 'success');
            
            // Перезагружаем UI
            this.loadFromDatabase();
            
        } catch (error) {
            console.error('Ошибка удаления:', error);
            Utils.showToast(error.message || 'Ошибка удаления разговора', 'error');
            
            // Восстанавливаем исходное состояние кнопки
            btn.prop('disabled', false).html(originalHTML);
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
     * Отобразить редактируемую транскрипцию
     */
    displayEditableTranscription(text, audioId) {
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
                
                <!-- Уведомление о редактировании -->
                <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p class="text-sm text-blue-800">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" class="inline mr-2">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                        </svg>
                        Проверьте текст транскрипции и при необходимости внесите исправления перед извлечением анамнеза
                    </p>
                </div>
                
                <!-- Редактируемая транскрипция -->
                <div class="mb-4">
                    <textarea 
                        id="transcription-text-area" 
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-mono"
                        rows="15"
                        placeholder="Текст транскрипции..."
                    >${text}</textarea>
                </div>
                
                <!-- Кнопки действий -->
                <div class="flex flex-col lg:flex-row space-y-3 lg:space-y-0 lg:space-x-4">
                    <button id="generate-conversation-btn" class="w-full lg:w-auto px-6 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:from-purple-600 hover:to-blue-600 font-medium flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                            <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                        </svg>
                        <span>Сгенерировать разговор</span>
                    </button>
                    <button id="clear-transcription-btn" class="w-full lg:w-auto px-6 py-3 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 font-medium flex items-center justify-center space-x-2">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
                        </svg>
                        <span>Очистить</span>
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
        
        // Очищаем контейнер и создаем transcription-display
        const container = $('#audio-upload-section');
        container.empty(); // Очищаем весь контейнер (удаляет старую кнопку генерации)
        container.html('<div id="transcription-display"></div>');
        
        $('#transcription-display').removeClass('hidden').html(html);
        
        // Обработчик генерации/регенерации
        $('#generate-conversation-btn').on('click', async () => {
            if (confirm('Вы уверены? Текущий текст будет заменён новым сгенерированным разговором.')) {
                await this.generateConversation();
            }
        });
        
        // Обработчик очистки
        $('#clear-transcription-btn').on('click', async () => {
            await this.clearTranscription();
        });
        
        // Обработчик сохранения транскрипции
        $('#save-transcription-btn').on('click', async () => {
            await this.saveTranscription(audioId);
        });
        
        // Обработчик извлечения анамнеза
        $('#extract-anamnesis-btn').on('click', async () => {
            // Сначала сохраняем изменения
            const saved = await this.saveTranscription(audioId);
            if (saved) {
                await this.extractAnamnesis();
            }
        });
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
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка сохранения');
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
            Utils.showToast(error.message || 'Ошибка сохранения изменений', 'error');
            
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
     * Отобразить транскрипцию с уже извлечённым анамнезом
     */
    displayTranscriptionWithExtractedAnamnesis(text) {
        const html = `
            <div class="bg-white border-2 border-green-200 rounded-lg p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="mr-2 text-green-500">
                            <path fill-rule="evenodd" d="M7 2a1 1 0 011 1v1h3a1 1 0 110 2H9.578a18.87 18.87 0 01-1.724 4.78c.29.354.596.696.914 1.026a1 1 0 11-1.44 1.389c-.188-.196-.373-.396-.554-.6a19.098 19.098 0 01-3.107 3.567 1 1 0 01-1.334-1.49 17.087 17.087 0 003.13-3.733 18.992 18.992 0 01-1.487-2.494 1 1 0 111.79-.89c.234.47.489.928.764 1.372.417-.934.752-1.913.997-2.927H3a1 1 0 110-2h3V3a1 1 0 011-1zm6 6a1 1 0 01.894.553l2.991 5.982a.869.869 0 01.02.037l.99 1.98a1 1 0 11-1.79.894L15.383 16h-4.764l-.723 1.447a1 1 0 11-1.788-.894l.99-1.98.019-.038 2.99-5.982A1 1 0 0113 8zm-1.382 6h2.764L13 11.236 11.618 14z" clip-rule="evenodd"/>
                        </svg>
                        Транскрипция разговора
                    </h3>
                    <span class="badge badge-cyan">Сгенерировано AI</span>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 mb-4 max-h-96 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-sm text-gray-700 font-mono">${text}</pre>
                </div>
                
                <!-- Успешное извлечение анамнеза -->
                <div class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div class="flex items-start space-x-3 mb-3">
                        <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20" class="text-green-500 flex-shrink-0 mt-0.5">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                        <div class="flex-1">
                            <p class="text-sm text-green-800 font-semibold mb-1">
                                Анамнез автоматически извлечён и сохранён!
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
                    </div>
                </div>
            </div>
        `;
        
        $('#transcription-display').removeClass('hidden').html(html);
        
        // Скрываем секцию загрузки файлов
        $('#upload-section').hide();
        
        $('#goto-anamnesis-btn').on('click', () => {
            PatientCard.switchTab('anamnesis');
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
            
            const audioData = await response.json();
            Utils.showToast('Файл успешно загружен', 'success');
            
            this.renderAudioPlayer(audioData);
            
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            Utils.showToast(error.message || 'Ошибка загрузки файла', 'error');
            this.renderUploadForm();
        }
    },
    
    /**
     * Отрендерить аудиоплеер
     */
    renderAudioPlayer(audioData) {
        $('#upload-area').remove();
        
        const html = `
            <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <svg class="w-10 h-10 text-elia-lavender" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                        </svg>
                        <div>
                            <p class="font-medium text-gray-900">${audioData.filename}</p>
                            <p class="text-sm text-gray-500">${(audioData.file_size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                    </div>
                </div>
                
                <audio controls class="w-full mb-4">
                    <source src="/api/audio/${audioData.id}/download" type="audio/mpeg">
                    Ваш браузер не поддерживает аудио элемент.
                </audio>
                
                <button id="transcribe-btn" class="btn-gradient w-full" data-audio-id="${audioData.id}">
                    <span>Транскрибировать</span>
                </button>
            </div>
            
            <div id="transcription-result" class="hidden"></div>
        `;
        
        $('#audio-player-section').removeClass('hidden').html(html);
        
        // Обработчик кнопки транскрибации
        $('#transcribe-btn').on('click', (e) => {
            const audioId = $(e.currentTarget).data('audio-id');
            this.transcribeAudio(audioId);
        });
    },
    
    /**
     * Транскрибировать аудио
     */
    async transcribeAudio(audioId) {
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
            const response = await fetch(`/api/audio/${audioId}/transcribe`, {
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

