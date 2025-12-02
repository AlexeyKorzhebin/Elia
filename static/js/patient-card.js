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
            <header class="patient-card-header bg-white border-b border-gray-200 px-4 py-4 lg:px-8 lg:py-6">
                <div class="flex items-center justify-between mb-4 lg:mb-6">
                    <div class="flex items-center space-x-2 lg:space-x-4 flex-1 min-w-0">
                        <button id="back-button" class="p-2 hover:bg-gray-100 rounded-lg flex-shrink-0">
                            <svg width="20" height="20" class="lg:w-6 lg:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                            </svg>
                        </button>
                        <div class="min-w-0 flex-1">
                            <h1 class="text-lg lg:text-2xl font-semibold text-gray-900 truncate">${patient.full_name}</h1>
                            <div class="flex flex-col lg:flex-row lg:items-center text-xs lg:text-sm text-gray-600 mt-1 space-y-1 lg:space-y-0">
                                <div class="flex items-center">
                                    <svg width="14" height="14" class="lg:w-4 lg:h-4" fill="currentColor" viewBox="0 0 20 20" class="mr-1 lg:mr-2">
                                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                                    </svg>
                                    <span>${Utils.formatDate(appointment.appointment_date)}</span>
                                </div>
                                <div class="flex items-center lg:ml-3">
                                    <svg width="14" height="14" class="lg:w-4 lg:h-4" fill="currentColor" viewBox="0 0 20 20" class="mr-1 lg:mr-2">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                                    </svg>
                                    <span>${appointment.appointment_time_start}–${appointment.appointment_time_end}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <button id="download-pdf-btn" class="hidden lg:flex px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 items-center space-x-2 flex-shrink-0 ml-4">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                        <span>Скачать</span>
                    </button>
                    <!-- Mobile download button -->
                    <button id="download-pdf-btn-mobile" class="lg:hidden p-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex-shrink-0 ml-2">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Вкладки -->
                <div class="tabs-container flex space-x-2 overflow-x-auto -mx-4 px-4 lg:mx-0 lg:px-0">
                    <button class="tab-button px-4 lg:px-6 py-2 lg:py-3 rounded-lg font-medium transition-colors flex-shrink-0" 
                            data-tab="digital-portrait">
                        Цифровой портрет
                    </button>
                    <button class="tab-button px-4 lg:px-6 py-2 lg:py-3 rounded-lg font-medium transition-colors flex-shrink-0" 
                            data-tab="anamnesis">
                        Анамнез
                    </button>
                    <button class="tab-button px-4 lg:px-6 py-2 lg:py-3 rounded-lg font-medium transition-colors flex-shrink-0" 
                            data-tab="stenogram">
                        Стенограмма
                    </button>
                </div>
            </header>
            
            <!-- Контент вкладок -->
            <div class="px-4 py-4 lg:px-8 lg:py-6">
                <div id="tab-content"></div>
            </div>
        `;
        
        $('#patient-card-screen').html(html);
        
        // Обработчики
        $('#back-button').on('click', () => {
            App.backToPatients();
        });
        
        $('#download-pdf-btn, #download-pdf-btn-mobile').on('click', () => {
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
    async switchTab(tab) {
        this.currentTab = tab;
        
        // Обновляем стили кнопок
        $('.tab-button').removeClass('tab-active bg-elia-lavender text-elia-dark').addClass('bg-gray-100 text-gray-700');
        $(`.tab-button[data-tab="${tab}"]`).removeClass('bg-gray-100 text-gray-700').addClass('tab-active');
        
        // Рендерим контент
        const content = $('#tab-content');
        
        switch (tab) {
            case 'digital-portrait':
                content.html(this.renderDigitalPortrait());
                this.initHealthModalHandlers();
                break;
            case 'anamnesis':
                // Перезагружаем данные отчёта перед рендерингом
                await this.reloadReportData();
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
     * Перезагрузить данные отчёта
     */
    async reloadReportData() {
        try {
            const reportResponse = await fetch(`/api/appointments/${this.appointmentData.id}/report`);
            if (reportResponse.ok) {
                this.reportData = await reportResponse.json();
            }
        } catch (e) {
            // Если отчёт не найден, оставляем null
            console.log('Отчёт не найден или ошибка загрузки');
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
                            <button id="health-details-btn" class="text-sm text-purple-600 hover:text-purple-700 font-medium">Подробнее</button>
                        </div>
                        <div class="health-indicators-grid">
                            <div class="health-card">
                                <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="text-red-500">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                                </svg>
                                <div class="text-center mt-3">
                                    <p class="text-xs text-gray-600 mb-1">АД ${health.bp_source === 'photo' ? '📸' : ''}</p>
                                    <p class="health-card-value">${health.systolic_pressure && health.diastolic_pressure ? health.systolic_pressure + '/' + health.diastolic_pressure : '—'}</p>
                                    <p class="health-card-unit">${health.systolic_pressure ? 'мм рт.ст.' : ''}</p>
                                </div>
                            </div>
                            
                            <div class="health-card">
                                <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="text-blue-500">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                                </svg>
                                <div class="text-center mt-3">
                                    <p class="text-xs text-gray-600 mb-1">Пульс ${health.bp_source === 'photo' ? '📸' : ''}</p>
                                    <p class="health-card-value">${health.pulse || health.heart_rate || '—'}</p>
                                    <p class="health-card-unit">${health.pulse || health.heart_rate ? 'уд/мин' : ''}</p>
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
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Модальное окно показателей здоровья -->
            <div id="health-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                    <div class="p-6 border-b border-gray-200 flex items-center justify-between">
                        <h2 class="text-xl font-semibold">Показатели здоровья</h2>
                        <button id="close-health-modal" class="p-2 hover:bg-gray-100 rounded-lg">
                            <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    <div id="health-modal-content" class="p-6">
                        <!-- Контент будет добавлен динамически -->
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
                    <div class="flex flex-col lg:flex-row space-y-3 lg:space-y-0 lg:space-x-4">
                        <button type="button" id="save-report-btn" class="w-full lg:w-auto px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium">
                            Сохранить черновик
                        </button>
                        <button type="button" id="submit-to-mis-btn" class="btn-gradient w-full lg:w-auto flex items-center justify-center space-x-2">
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
     * Инициализировать обработчики модального окна показателей здоровья
     */
    initHealthModalHandlers() {
        const self = this;
        
        $('#health-details-btn').on('click', () => {
            this.openHealthModal();
        });
        
        $('#close-health-modal').on('click', () => {
            this.closeHealthModal();
        });
        
        // Закрытие по клику на оверлей
        $('#health-modal').on('click', (e) => {
            if (e.target.id === 'health-modal') {
                this.closeHealthModal();
            }
        });
    },
    
    /**
     * Открыть модальное окно показателей здоровья
     */
    openHealthModal() {
        const health = this.patientData.health_indicators || {};
        
        const html = `
            <div class="space-y-6">
                <!-- Текущие показатели давления -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="font-semibold text-gray-900 mb-4 flex items-center">
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="mr-2 text-red-500">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                        </svg>
                        Артериальное давление
                    </h3>
                    
                    <div class="grid grid-cols-3 gap-4 mb-4">
                        <div class="text-center p-3 bg-white rounded-lg">
                            <p class="text-xs text-gray-500 mb-1">Систолическое</p>
                            <p id="current-systolic" class="text-2xl font-bold text-gray-900">${health.systolic_pressure || '—'}</p>
                            <p class="text-xs text-gray-500">мм рт.ст.</p>
                        </div>
                        <div class="text-center p-3 bg-white rounded-lg">
                            <p class="text-xs text-gray-500 mb-1">Диастолическое</p>
                            <p id="current-diastolic" class="text-2xl font-bold text-gray-900">${health.diastolic_pressure || '—'}</p>
                            <p class="text-xs text-gray-500">мм рт.ст.</p>
                        </div>
                        <div class="text-center p-3 bg-white rounded-lg">
                            <p class="text-xs text-gray-500 mb-1">Пульс</p>
                            <p id="current-pulse" class="text-2xl font-bold text-gray-900">${health.pulse || '—'}</p>
                            <p class="text-xs text-gray-500">уд/мин</p>
                        </div>
                    </div>
                    
                    ${health.bp_source === 'photo' ? `
                        <div class="flex items-center text-sm text-gray-500">
                            <span class="mr-1">📸</span>
                            <span>Получено с фото тонометра</span>
                            ${health.bp_updated_at ? `<span class="ml-2">• ${new Date(health.bp_updated_at).toLocaleString('ru-RU')}</span>` : ''}
                        </div>
                    ` : ''}
                </div>
                
                <!-- Кнопки добавления показателей -->
                <div class="border-2 border-dashed border-gray-300 rounded-lg p-6">
                    <h4 class="font-medium text-gray-900 mb-4 text-center">Добавить показатели с тонометра</h4>
                    
                    <div class="flex flex-col sm:flex-row gap-3 justify-center">
                        <button id="tonometer-image-btn" class="flex items-center justify-center space-x-2 px-6 py-3 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors">
                            <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                            </svg>
                            <span>Изображение</span>
                        </button>
                        
                        <button id="tonometer-camera-btn" class="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                            <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                            <span>Камера</span>
                        </button>
                    </div>
                    
                    <input type="file" id="tonometer-file-input" accept="image/*" class="hidden">
                </div>
                
                <!-- Область распознавания (скрыта по умолчанию) -->
                <div id="tonometer-recognition-area" class="hidden">
                    <!-- Будет заполнено при загрузке изображения -->
                </div>
            </div>
        `;
        
        $('#health-modal-content').html(html);
        $('#health-modal').removeClass('hidden');
        
        // Обработчики кнопок
        $('#tonometer-image-btn').on('click', () => {
            $('#tonometer-file-input').click();
        });
        
        $('#tonometer-camera-btn').on('click', () => {
            this.openCameraPreview();
        });
        
        $('#tonometer-file-input').on('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleTonometerImage(file);
            }
        });
    },
    
    /**
     * Открыть камеру с предпросмотром
     */
    async openCameraPreview() {
        const html = `
            <div class="bg-gray-900 rounded-lg p-4">
                <div class="flex items-center justify-between mb-4">
                    <h4 class="font-medium text-white">Камера</h4>
                    <button id="close-camera-btn" class="p-2 text-white hover:bg-gray-700 rounded-lg">
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                
                <div class="relative mb-4">
                    <video id="camera-preview" autoplay playsinline class="w-full rounded-lg bg-black" style="max-height: 400px;"></video>
                    <div id="camera-loading" class="absolute inset-0 flex items-center justify-center bg-gray-800 rounded-lg">
                        <div class="text-center">
                            <div class="processing-spinner mx-auto mb-2"></div>
                            <p class="text-white text-sm">Инициализация камеры...</p>
                        </div>
                    </div>
                </div>
                
                <div class="flex justify-center">
                    <button id="capture-photo-btn" disabled class="px-8 py-4 bg-white text-gray-900 rounded-full hover:bg-gray-100 font-medium flex items-center space-x-2 disabled:opacity-50">
                        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke-width="2"/>
                            <circle cx="12" cy="12" r="4" fill="currentColor"/>
                        </svg>
                        <span>Сделать фото</span>
                    </button>
                </div>
                
                <canvas id="camera-canvas" class="hidden"></canvas>
            </div>
        `;
        
        $('#tonometer-recognition-area').html(html).removeClass('hidden');
        
        // Инициализация камеры
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment', // Задняя камера
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            });
            
            const video = document.getElementById('camera-preview');
            video.srcObject = stream;
            
            // Когда видео загрузится
            video.onloadedmetadata = () => {
                $('#camera-loading').addClass('hidden');
                $('#capture-photo-btn').prop('disabled', false);
            };
            
            // Сохраняем stream для закрытия
            this.cameraStream = stream;
            
        } catch (error) {
            console.error('Ошибка доступа к камере:', error);
            $('#camera-loading').html(`
                <div class="text-center">
                    <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24" class="mx-auto mb-2 text-red-500">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                    </svg>
                    <p class="text-white text-sm">Не удалось получить доступ к камере</p>
                    <p class="text-gray-400 text-xs mt-1">Проверьте разрешения браузера</p>
                </div>
            `);
        }
        
        // Обработчик закрытия камеры
        $('#close-camera-btn').on('click', () => {
            this.closeCameraPreview();
        });
        
        // Обработчик съёмки фото
        $('#capture-photo-btn').on('click', () => {
            this.capturePhoto();
        });
    },
    
    /**
     * Закрыть камеру
     */
    closeCameraPreview() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        $('#tonometer-recognition-area').addClass('hidden').empty();
    },
    
    /**
     * Сделать фото с камеры
     */
    capturePhoto() {
        const video = document.getElementById('camera-preview');
        const canvas = document.getElementById('camera-canvas');
        const ctx = canvas.getContext('2d');
        
        // Устанавливаем размер canvas по видео
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Рисуем кадр на canvas
        ctx.drawImage(video, 0, 0);
        
        // Конвертируем в blob
        canvas.toBlob((blob) => {
            if (blob) {
                // Останавливаем камеру
                if (this.cameraStream) {
                    this.cameraStream.getTracks().forEach(track => track.stop());
                    this.cameraStream = null;
                }
                
                // Создаём файл из blob
                const file = new File([blob], 'tonometer_photo.jpg', { type: 'image/jpeg' });
                
                // Получаем data URL для превью
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.showTonometerRecognition(file, e.target.result);
                };
                reader.readAsDataURL(blob);
            }
        }, 'image/jpeg', 0.9);
    },
    
    /**
     * Закрыть модальное окно
     */
    closeHealthModal() {
        $('#health-modal').addClass('hidden');
    },
    
    /**
     * Обработать загруженное изображение тонометра
     */
    async handleTonometerImage(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const imageDataUrl = e.target.result;
            this.showTonometerRecognition(file, imageDataUrl);
        };
        
        reader.readAsDataURL(file);
    },
    
    /**
     * Показать область распознавания тонометра
     */
    showTonometerRecognition(file, imageDataUrl) {
        const html = `
            <div class="bg-white border-2 border-purple-200 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-4">Распознавание показателей</h4>
                
                <!-- Превью изображения -->
                <div class="relative mb-4">
                    <img id="tonometer-preview" src="${imageDataUrl}" class="max-w-full max-h-64 mx-auto rounded-lg" alt="Фото тонометра">
                    <div id="roi-overlay" class="absolute inset-0 pointer-events-none">
                        <!-- ROI рамка будет здесь -->
                    </div>
                </div>
                
                <p class="text-sm text-gray-500 text-center mb-4">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" class="inline mr-1">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                    </svg>
                    Убедитесь, что экран тонометра хорошо виден на изображении
                </p>
                
                <div class="flex justify-center space-x-3">
                    <button id="cancel-recognition-btn" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                        Отмена
                    </button>
                    <button id="recognize-btn" class="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:from-purple-600 hover:to-blue-600 flex items-center space-x-2">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 9a2 2 0 114 0 2 2 0 01-4 0z"/>
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a4 4 0 00-3.446 6.032l-2.261 2.26a1 1 0 101.414 1.415l2.261-2.261A4 4 0 1011 5z" clip-rule="evenodd"/>
                        </svg>
                        <span>Распознать</span>
                    </button>
                </div>
            </div>
        `;
        
        $('#tonometer-recognition-area').html(html).removeClass('hidden');
        
        // Обработчики
        $('#cancel-recognition-btn').on('click', () => {
            $('#tonometer-recognition-area').addClass('hidden').empty();
        });
        
        $('#recognize-btn').on('click', () => {
            this.recognizeTonometer(file);
        });
    },
    
    /**
     * Распознать показатели с изображения
     */
    async recognizeTonometer(file) {
        const btn = $('#recognize-btn');
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Распознавание...</span>
        `);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`/api/patients/${this.patientData.id}/recognize-tonometer`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showRecognitionResults(result);
            } else {
                Utils.showToast(result.error || 'Не удалось распознать показания', 'error');
                btn.prop('disabled', false).html(`
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 9a2 2 0 114 0 2 2 0 01-4 0z"/>
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a4 4 0 00-3.446 6.032l-2.261 2.26a1 1 0 101.414 1.415l2.261-2.261A4 4 0 1011 5z" clip-rule="evenodd"/>
                    </svg>
                    <span>Распознать</span>
                `);
            }
            
        } catch (error) {
            console.error('Ошибка распознавания:', error);
            Utils.showToast('Ошибка распознавания', 'error');
            btn.prop('disabled', false).html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 9a2 2 0 114 0 2 2 0 01-4 0z"/>
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a4 4 0 00-3.446 6.032l-2.261 2.26a1 1 0 101.414 1.415l2.261-2.261A4 4 0 1011 5z" clip-rule="evenodd"/>
                </svg>
                <span>Распознать</span>
            `);
        }
    },
    
    /**
     * Показать результаты распознавания
     */
    showRecognitionResults(result) {
        const confidenceColors = {
            'high': 'text-green-600',
            'medium': 'text-yellow-600',
            'low': 'text-red-600'
        };
        
        const confidenceTexts = {
            'high': 'Высокая уверенность',
            'medium': 'Средняя уверенность',
            'low': 'Низкая уверенность'
        };
        
        const html = `
            <div class="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                <div class="flex items-center space-x-2 mb-4">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20" class="text-green-500">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <h4 class="font-medium text-green-800">Показатели распознаны</h4>
                    <span class="text-sm ${confidenceColors[result.confidence] || 'text-gray-600'}">
                        (${confidenceTexts[result.confidence] || result.confidence})
                    </span>
                </div>
                
                ${result.confidence === 'low' ? `
                    <div class="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg text-sm text-yellow-800">
                        ⚠️ Проверьте корректность значений. Низкая уверенность распознавания.
                    </div>
                ` : ''}
                
                <div class="grid grid-cols-3 gap-4 mb-4">
                    <div class="text-center">
                        <label class="text-xs text-gray-500 block mb-1">Систолическое</label>
                        <input type="number" id="result-systolic" value="${result.systolic || ''}" 
                            class="w-full px-3 py-2 text-center text-xl font-bold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500">
                        <span class="text-xs text-gray-500">мм рт.ст.</span>
                    </div>
                    <div class="text-center">
                        <label class="text-xs text-gray-500 block mb-1">Диастолическое</label>
                        <input type="number" id="result-diastolic" value="${result.diastolic || ''}" 
                            class="w-full px-3 py-2 text-center text-xl font-bold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500">
                        <span class="text-xs text-gray-500">мм рт.ст.</span>
                    </div>
                    <div class="text-center">
                        <label class="text-xs text-gray-500 block mb-1">Пульс</label>
                        <input type="number" id="result-pulse" value="${result.pulse || ''}" 
                            class="w-full px-3 py-2 text-center text-xl font-bold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500">
                        <span class="text-xs text-gray-500">уд/мин</span>
                    </div>
                </div>
                
                <div class="flex justify-end space-x-3">
                    <button id="discard-results-btn" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                        Отменить
                    </button>
                    <button id="save-results-btn" class="px-6 py-2 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg hover:from-green-600 hover:to-teal-600 flex items-center space-x-2">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        <span>Сохранить показатели</span>
                    </button>
                </div>
            </div>
        `;
        
        $('#tonometer-recognition-area').html(html);
        
        // Обработчики
        $('#discard-results-btn').on('click', () => {
            $('#tonometer-recognition-area').addClass('hidden').empty();
        });
        
        $('#save-results-btn').on('click', () => {
            this.saveBloodPressure();
        });
    },
    
    /**
     * Сохранить показатели давления
     */
    async saveBloodPressure() {
        const systolic = parseInt($('#result-systolic').val());
        const diastolic = parseInt($('#result-diastolic').val());
        const pulse = $('#result-pulse').val() ? parseInt($('#result-pulse').val()) : null;
        
        // Валидация
        if (!systolic || systolic < 60 || systolic > 300) {
            Utils.showToast('Введите корректное систолическое давление (60-300)', 'error');
            return;
        }
        if (!diastolic || diastolic < 30 || diastolic > 200) {
            Utils.showToast('Введите корректное диастолическое давление (30-200)', 'error');
            return;
        }
        
        const btn = $('#save-results-btn');
        btn.prop('disabled', true).html(`
            <div class="spinner mr-2"></div>
            <span>Сохранение...</span>
        `);
        
        try {
            const response = await fetch(`/api/patients/${this.patientData.id}/blood-pressure`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    systolic: systolic,
                    diastolic: diastolic,
                    pulse: pulse,
                    source: 'photo'
                })
            });
            
            if (!response.ok) {
                throw new Error('Ошибка сохранения');
            }
            
            const result = await response.json();
            
            // Обновляем локальные данные
            if (!this.patientData.health_indicators) {
                this.patientData.health_indicators = {};
            }
            this.patientData.health_indicators.systolic_pressure = systolic;
            this.patientData.health_indicators.diastolic_pressure = diastolic;
            this.patientData.health_indicators.pulse = pulse;
            this.patientData.health_indicators.bp_source = 'photo';
            this.patientData.health_indicators.bp_updated_at = new Date().toISOString();
            
            Utils.showToast('Показатели успешно сохранены!', 'success');
            
            // Обновляем отображение в модалке
            $('#current-systolic').text(systolic);
            $('#current-diastolic').text(diastolic);
            $('#current-pulse').text(pulse || '—');
            
            // Скрываем область распознавания
            $('#tonometer-recognition-area').addClass('hidden').empty();
            
            // Закрываем модалку и перерендерим портрет
            this.closeHealthModal();
            this.switchTab('digital-portrait');
            
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            Utils.showToast('Ошибка сохранения показателей', 'error');
            btn.prop('disabled', false).html(`
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                <span>Сохранить показатели</span>
            `);
        }
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

