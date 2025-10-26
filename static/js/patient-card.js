/**
 * Модуль работы с карточкой пациента
 */

const PatientCard = {
    currentTab: 'digital-portrait',
    appointmentData: null,
    patientData: null,
    reportData: null,
    
    /**
     * Инициализация
     */
    init() {
        console.log('Инициализация модуля карточки пациента...');
    },
    
    /**
     * Загрузить данные приёма и пациента
     */
    async load(appointmentId) {
        const container = $('#patient-card-screen');
        container.html(Utils.showLoader('Загрузка данных пациента...'));
        
        try {
            // Загружаем данные приёма
            const appointmentResponse = await fetch(`/api/appointments/${appointmentId}`);
            if (!appointmentResponse.ok) {
                throw new Error('Ошибка загрузки приёма');
            }
            this.appointmentData = await appointmentResponse.json();
            
            // Загружаем цифровой портрет пациента
            const patientResponse = await fetch(`/api/patients/${this.appointmentData.patient.id}/digital-portrait`);
            if (!patientResponse.ok) {
                throw new Error('Ошибка загрузки пациента');
            }
            this.patientData = await patientResponse.json();
            
            // Пытаемся загрузить отчёт (может не существовать)
            try {
                const reportResponse = await fetch(`/api/appointments/${appointmentId}/report`);
                if (reportResponse.ok) {
                    this.reportData = await reportResponse.json();
                }
            } catch (e) {
                this.reportData = null;
            }
            
            this.render();
            
        } catch (error) {
            console.error('Ошибка:', error);
            container.html(Utils.showError('Не удалось загрузить данные пациента'));
            Utils.showToast('Ошибка загрузки данных', 'error');
        }
    },
    
    /**
     * Отрендерить карточку пациента
     */
    render() {
        const patient = this.patientData;
        const appointment = this.appointmentData;
        
        const html = `
            <!-- Хедер -->
            <header class="bg-white border-b border-gray-200 px-8 py-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <button id="back-button" class="p-2 hover:bg-gray-100 rounded-lg">
                            <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                            </svg>
                        </button>
                        <div>
                            <h1 class="text-2xl font-semibold text-gray-900">${patient.full_name}</h1>
                            <div class="flex items-center text-sm text-gray-600 mt-1">
                                <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" class="mr-2">
                                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                                </svg>
                                <span>${Utils.formatDate(appointment.appointment_date)}</span>
                                <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" class="ml-4 mr-2">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                                </svg>
                                <span>${appointment.appointment_time_start}–${appointment.appointment_time_end}</span>
                            </div>
                        </div>
                    </div>
                    <button id="download-pdf-btn" class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                        <span>Скачать</span>
                    </button>
                </div>
                
                <!-- Вкладки -->
                <div class="flex space-x-2 mt-6">
                    <button class="tab-button px-6 py-3 rounded-lg font-medium transition-colors" 
                            data-tab="digital-portrait">
                        Цифровой портрет
                    </button>
                    <button class="tab-button px-6 py-3 rounded-lg font-medium transition-colors" 
                            data-tab="anamnesis">
                        Анамнез
                    </button>
                    <button class="tab-button px-6 py-3 rounded-lg font-medium transition-colors" 
                            data-tab="stenogram">
                        Стенограмма
                    </button>
                </div>
            </header>
            
            <!-- Контент вкладок -->
            <div class="px-8 py-6">
                <div id="tab-content"></div>
            </div>
        `;
        
        $('#patient-card-screen').html(html);
        
        // Обработчики
        $('#back-button').on('click', () => {
            App.backToPatients();
        });
        
        $('#download-pdf-btn').on('click', () => {
            this.downloadPDF();
        });
        
        $('.tab-button').on('click', (e) => {
            const tab = $(e.currentTarget).data('tab');
            this.switchTab(tab);
        });
        
        // Показываем первую вкладку
        this.switchTab('digital-portrait');
    },
    
    /**
     * Переключить вкладку
     */
    switchTab(tab) {
        this.currentTab = tab;
        
        // Обновляем стили кнопок
        $('.tab-button').removeClass('tab-active bg-elia-lavender text-elia-dark').addClass('bg-gray-100 text-gray-700');
        $(`.tab-button[data-tab="${tab}"]`).removeClass('bg-gray-100 text-gray-700').addClass('tab-active');
        
        // Рендерим контент
        const content = $('#tab-content');
        
        switch (tab) {
            case 'digital-portrait':
                content.html(this.renderDigitalPortrait());
                break;
            case 'anamnesis':
                content.html(this.renderAnamnesis());
                this.initAnamnesisHandlers();
                break;
            case 'stenogram':
                content.html(this.renderStenogram());
                AudioHandler.init(this.appointmentData.id);
                break;
        }
    },
    
    /**
     * Отрендерить цифровой портрет
     */
    renderDigitalPortrait() {
        const patient = this.patientData;
        const health = patient.health_indicators || {};
        
        return `
            <div class="digital-portrait-container">
                <h2 class="section-header">Цифровой портрет</h2>
                
                <!-- Верхняя строка: три карточки -->
                <div class="portrait-grid-top">
                    <!-- Основные данные -->
                    <div class="section-cyan">
                        <h3 class="font-semibold text-lg mb-4">Основные данные</h3>
                        <div class="space-y-3 text-sm">
                            <div>
                                <span class="text-gray-600 block text-xs mb-1">Пол</span>
                                <p class="font-medium">${patient.gender === 'male' ? 'Мужской' : 'Женский'}</p>
                            </div>
                            <div>
                                <span class="text-gray-600 block text-xs mb-1">Возраст</span>
                                <p class="font-medium">${patient.age}</p>
                            </div>
                            <div>
                                <span class="text-gray-600 block text-xs mb-1">МО прикрепления</span>
                                <p class="font-medium">${patient.medical_organization}</p>
                            </div>
                            <div>
                                <span class="text-gray-600 block text-xs mb-1">Участок прикрепления</span>
                                <p class="font-medium">${patient.medical_area}</p>
                            </div>
                            <div>
                                <span class="text-gray-600 block text-xs mb-1">Дата последнего обращения</span>
                                <p class="font-medium">${patient.last_visit_date ? Utils.formatDate(patient.last_visit_date) : 'Нет данных'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Хронические заболевания -->
                    <div class="section-pink">
                        <h3 class="font-semibold text-lg mb-4">Хронические заболевания</h3>
                        ${patient.chronic_diseases.length > 0 ? `
                            <ul class="list-disc list-inside space-y-2 text-sm">
                                ${patient.chronic_diseases.map(d => `<li>${d.name}</li>`).join('')}
                            </ul>
                        ` : '<p class="text-gray-600 text-sm">Нет данных</p>'}
                    </div>
                    
                    <!-- Последние заболевания -->
                    <div class="section-yellow">
                        <h3 class="font-semibold text-lg mb-4">Последние заболевания</h3>
                        ${patient.recent_diseases.length > 0 ? `
                            <ul class="list-disc list-inside space-y-2 text-sm">
                                ${patient.recent_diseases.map(d => `<li>${d.name}</li>`).join('')}
                            </ul>
                        ` : '<p class="text-gray-600 text-sm">Нет данных</p>'}
                    </div>
                </div>
                
                <!-- Нижняя строка: две широкие карточки -->
                <div class="portrait-grid-bottom">
                    <!-- Саммари -->
                    <div class="section-blue">
                        <h3 class="font-semibold text-lg mb-4">Саммари</h3>
                        <div class="space-y-3">
                            <div class="flex items-start space-x-3">
                                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="text-blue-600 flex-shrink-0 mt-0.5">
                                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                                </svg>
                                <p class="text-sm">Уровень внимания по диспансеризации: без COVID-19, коморбидных заболеваний и с мед. осмотром в течение 2 лет</p>
                            </div>
                            <div class="flex items-start space-x-3">
                                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="text-blue-600 flex-shrink-0 mt-0.5">
                                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                                </svg>
                                <p class="text-sm">Целевые цифры АД не достигнуты</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Основные показатели здоровья -->
                    <div class="section-green">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-semibold text-lg">Основные показатели здоровья</h3>
                            <a href="#" class="text-sm text-purple-600 hover:text-purple-700 font-medium">Подробнее</a>
                        </div>
                        <div class="health-indicators-grid">
                            <div class="health-card">
                                <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="text-red-500">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                                </svg>
                                <div class="text-center mt-3">
                                    <p class="text-xs text-gray-600 mb-1">Гемоглобин</p>
                                    <p class="health-card-value">${health.hemoglobin || '—'}</p>
                                    <p class="health-card-unit">${health.hemoglobin ? 'г/л' : ''}</p>
                                </div>
                            </div>
                            
                            <div class="health-card">
                                <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="text-orange-500">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                                <div class="text-center mt-3">
                                    <p class="text-xs text-gray-600 mb-1">Холестерин</p>
                                    <p class="health-card-value">${health.cholesterol || '—'}</p>
                                    <p class="health-card-unit">${health.cholesterol ? 'ммоль/л' : ''}</p>
                                </div>
                            </div>
                            
                            <div class="health-card">
                                <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="text-gray-600">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                                </svg>
                                <div class="text-center mt-3">
                                    <p class="text-xs text-gray-600 mb-1">ИМТ</p>
                                    <p class="health-card-value">${health.bmi || '—'}</p>
                                    <p class="health-card-unit">${health.bmi ? 'кг/м²' : ''}</p>
                                </div>
                            </div>
                            
                            <div class="health-card">
                                <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="text-blue-500">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                                </svg>
                                <div class="text-center mt-3">
                                    <p class="text-xs text-gray-600 mb-1">ЧСС</p>
                                    <p class="health-card-value">${health.heart_rate || '—'}</p>
                                    <p class="health-card-unit">${health.heart_rate ? 'уд/мин' : ''}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * Отрендерить анамнез
     */
    renderAnamnesis() {
        const report = this.reportData || {};
        
        return `
            <div class="max-w-4xl">
                <h2 class="section-header">Анамнез</h2>
                
                <form id="anamnesis-form" class="space-y-6">
                    <!-- Цель обращения -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Цель обращения</label>
                        <textarea 
                            id="purpose-field"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-elia-lavender"
                            rows="3"
                            placeholder="Опишите цель обращения пациента..."
                        >${report.purpose || ''}</textarea>
                    </div>
                    
                    <!-- Жалобы пациента -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Жалобы пациента</label>
                        <textarea 
                            id="complaints-field"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-elia-lavender"
                            rows="4"
                            placeholder="Опишите жалобы пациента..."
                        >${report.complaints || ''}</textarea>
                    </div>
                    
                    <!-- Анамнез -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Анамнез</label>
                        <textarea 
                            id="anamnesis-field"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-elia-lavender"
                            rows="6"
                            placeholder="Опишите анамнез..."
                        >${report.anamnesis || ''}</textarea>
                    </div>
                    
                    <!-- Кнопки -->
                    <div class="flex space-x-4">
                        <button type="button" id="save-report-btn" class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium">
                            Сохранить черновик
                        </button>
                        <button type="button" id="submit-to-mis-btn" class="btn-gradient flex items-center space-x-2">
                            <span>Занести в МИС</span>
                            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd"/>
                            </svg>
                        </button>
                    </div>
                    
                    ${report.submitted_to_mis ? `
                        <div class="flex items-center space-x-2 text-green-600">
                            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                            </svg>
                            <span class="font-medium">Отчёт отправлен в МИС</span>
                            <span class="text-sm text-gray-600">(${new Date(report.submitted_at).toLocaleString('ru-RU')})</span>
                        </div>
                    ` : ''}
                </form>
            </div>
        `;
    },
    
    /**
     * Инициализировать обработчики для анамнеза
     */
    initAnamnesisHandlers() {
        const self = this;
        
        // Сохранение черновика
        $('#save-report-btn').on('click', async function() {
            const btn = $(this);
            btn.prop('disabled', true).html('<span class="spinner mr-2"></span>Сохранение...');
            
            try {
                await self.saveReport();
                Utils.showToast('Черновик сохранён', 'success');
            } catch (error) {
                Utils.showToast('Ошибка сохранения', 'error');
            } finally {
                btn.prop('disabled', false).text('Сохранить черновик');
            }
        });
        
        // Отправка в МИС
        $('#submit-to-mis-btn').on('click', async function() {
            const btn = $(this);
            btn.prop('disabled', true).html('<span class="spinner mr-2"></span>Отправка в МИС...');
            
            try {
                // Сначала сохраняем отчёт
                await self.saveReport();
                
                // Имитация отправки в МИС
                const response = await fetch(`/api/appointments/${self.appointmentData.id}/submit-to-mis`, {
                    method: 'POST'
                });
                
                if (!response.ok) {
                    throw new Error('Ошибка отправки в МИС');
                }
                
                const result = await response.json();
                Utils.showToast(result.message, 'success');
                
                // Перезагружаем отчёт
                const reportResponse = await fetch(`/api/appointments/${self.appointmentData.id}/report`);
                if (reportResponse.ok) {
                    self.reportData = await reportResponse.json();
                    self.switchTab('anamnesis'); // Перерендерим вкладку
                }
                
            } catch (error) {
                Utils.showToast('Ошибка отправки в МИС', 'error');
            } finally {
                btn.prop('disabled', false).html(`
                    <span>Занести в МИС</span>
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd"/>
                    </svg>
                `);
            }
        });
    },
    
    /**
     * Сохранить отчёт
     */
    async saveReport() {
        const data = {
            purpose: $('#purpose-field').val(),
            complaints: $('#complaints-field').val(),
            anamnesis: $('#anamnesis-field').val()
        };
        
        const response = await fetch(`/api/appointments/${this.appointmentData.id}/report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка сохранения отчёта');
        }
        
        this.reportData = await response.json();
    },
    
    /**
     * Отрендерить стенограмму
     */
    renderStenogram() {
        return `
            <div class="max-w-4xl">
                <h2 class="section-header">Стенограмма</h2>
                <div id="audio-upload-section"></div>
            </div>
        `;
    },
    
    /**
     * Скачать информацию о приёме в PDF
     */
    async downloadPDF() {
        if (!this.appointmentData) {
            Utils.showToast('Данные приёма не загружены', 'error');
            return;
        }
        
        try {
            // Показываем индикатор загрузки
            const btn = $('#download-pdf-btn');
            const originalHtml = btn.html();
            btn.prop('disabled', true).html(`
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="ml-2">Генерация...</span>
            `);
            
            // Создаем скрытый iframe для скачивания
            const url = `/api/appointments/${this.appointmentData.id}/download-pdf`;
            
            // Используем fetch для получения файла
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Ошибка скачивания PDF');
            }
            
            // Получаем blob из ответа
            const blob = await response.blob();
            
            // Создаем ссылку для скачивания
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            
            // Получаем имя файла из заголовков
            const contentDisposition = response.headers.get('content-disposition');
            let filename = 'priem.pdf';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename=(.+)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            // Очистка
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
            
            Utils.showToast('PDF успешно скачан', 'success');
            
            // Восстанавливаем кнопку
            btn.prop('disabled', false).html(originalHtml);
            
        } catch (error) {
            console.error('Ошибка скачивания PDF:', error);
            Utils.showToast('Ошибка скачивания PDF', 'error');
            
            // Восстанавливаем кнопку
            const btn = $('#download-pdf-btn');
            btn.prop('disabled', false).html(`
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
                <span>Скачать</span>
            `);
        }
    }
};

