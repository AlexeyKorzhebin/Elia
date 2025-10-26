/**
 * Модуль работы со списком пациентов
 */

const Patients = {
    appointments: [],
    
    /**
     * Инициализация
     */
    init() {
        console.log('Инициализация модуля пациентов...');
        this.loadAppointments();
    },
    
    /**
     * Загрузить список приёмов
     */
    async loadAppointments(search = '') {
        const container = $('#appointments-list');
        container.html(Utils.showLoader('Загрузка приёмов...'));
        
        try {
            const params = new URLSearchParams();
            if (search) {
                params.append('search', search);
            }
            
            const response = await fetch(`/api/appointments?${params}`);
            if (!response.ok) {
                throw new Error('Ошибка загрузки приёмов');
            }
            
            this.appointments = await response.json();
            this.renderAppointments();
            
        } catch (error) {
            console.error('Ошибка:', error);
            container.html(Utils.showError('Не удалось загрузить список приёмов'));
            Utils.showToast('Ошибка загрузки данных', 'error');
        }
    },
    
    /**
     * Отрендерить список приёмов
     */
    renderAppointments() {
        const container = $('#appointments-list');
        
        if (this.appointments.length === 0) {
            container.html(`
                <div class="text-center py-12">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                    </svg>
                    <p class="mt-4 text-gray-600">Нет запланированных приёмов</p>
                </div>
            `);
            return;
        }
        
        // Группируем приёмы по датам
        const groupedByDate = Utils.groupBy(this.appointments, 'appointment_date');
        
        let html = '';
        for (const [date, appointments] of Object.entries(groupedByDate)) {
            html += this.renderDateGroup(date, appointments);
        }
        
        container.html(html);
        
        // Обработчики кликов на карточки
        $('.appointment-card').on('click', function() {
            const appointmentId = $(this).data('appointment-id');
            App.openPatientCard(appointmentId);
        });
    },
    
    /**
     * Отрендерить группу приёмов по дате
     */
    renderDateGroup(date, appointments) {
        const formattedDate = Utils.formatDate(date);
        
        let cardsHtml = '';
        for (const appointment of appointments) {
            cardsHtml += this.renderAppointmentCard(appointment);
        }
        
        return `
            <div class="mb-8">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">${formattedDate}</h2>
                <div class="flex space-x-4 overflow-x-auto pb-4">
                    ${cardsHtml}
                </div>
            </div>
        `;
    },
    
    /**
     * Отрендерить карточку приёма
     */
    renderAppointmentCard(appointment) {
        const patient = appointment.patient;
        const badgeClass = Utils.getStatusBadgeClass(appointment.status);
        const activeClass = appointment.is_active ? 'active' : '';
        
        return `
            <div class="appointment-card ${activeClass} flex-shrink-0 w-64 bg-white rounded-lg shadow-sm border border-gray-200 p-4 relative" 
                 data-appointment-id="${appointment.id}">
                <!-- Меню -->
                <button class="absolute top-3 right-3 text-gray-400 hover:text-gray-600">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"/>
                    </svg>
                </button>
                
                <!-- ФИО пациента -->
                <h3 class="text-lg font-semibold mb-2 pr-6 ${appointment.is_active ? 'text-white' : 'text-gray-900'}">
                    ${patient.last_name} ${patient.first_name}<br>${patient.middle_name}
                </h3>
                
                <!-- Бейдж статуса -->
                ${appointment.status !== 'Запланирован' ? `
                    <span class="badge ${badgeClass} mb-3">${appointment.status}</span>
                ` : ''}
                
                <!-- Время приёма -->
                <div class="flex items-center mt-4 ${appointment.is_active ? 'text-white' : 'text-gray-600'}">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" class="mr-2">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                    </svg>
                    <span class="text-sm">${appointment.appointment_time_start}</span>
                </div>
            </div>
        `;
    }
};

