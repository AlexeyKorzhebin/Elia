/**
 * Главный файл приложения
 * Управление состоянием и роутингом
 */

const App = {
    currentScreen: 'patients',
    currentAppointmentId: null,
    currentPatientId: null,
    
    /**
     * Инициализация приложения
     */
    init() {
        console.log('Инициализация Elia AI Platform...');
        
        // Инициализация компонентов
        if (typeof MobileMenu !== 'undefined') {
            MobileMenu.init();
        }
        Patients.init();
        PatientCard.init();
        
        // Обработчики меню
        $('#menu-patients, #mobile-menu-patients').on('click', (e) => {
            e.preventDefault();
            this.showScreen('patients');
        });
        
        // Поиск
        let searchTimeout;
        $('#search-input').on('input', function() {
            clearTimeout(searchTimeout);
            const query = $(this).val().trim();
            searchTimeout = setTimeout(() => {
                Patients.loadAppointments(query);
            }, 300);
        });
        
        console.log('Приложение готово!');
    },
    
    /**
     * Переключение между экранами
     */
    showScreen(screen) {
        if (screen === 'patients') {
            $('#patients-screen').removeClass('hidden');
            $('#patient-card-screen').addClass('hidden');
            this.currentScreen = 'patients';
            Patients.loadAppointments();
        } else if (screen === 'patient-card') {
            $('#patients-screen').addClass('hidden');
            $('#patient-card-screen').removeClass('hidden');
            this.currentScreen = 'patient-card';
        }
    },
    
    /**
     * Открыть карточку пациента
     */
    openPatientCard(appointmentId) {
        this.currentAppointmentId = appointmentId;
        PatientCard.load(appointmentId);
        this.showScreen('patient-card');
    },
    
    /**
     * Вернуться к списку пациентов
     */
    backToPatients() {
        this.currentAppointmentId = null;
        this.currentPatientId = null;
        this.showScreen('patients');
    }
};

/**
 * Утилиты
 */
const Utils = {
    /**
     * Форматирование даты
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const options = { weekday: 'short', day: 'numeric', month: 'numeric', year: '2-digit' };
        const formatted = date.toLocaleDateString('ru-RU', options);
        
        // Преобразуем формат: "чт, 16.10.25" -> "Чт, 16.10.25"
        return formatted.charAt(0).toUpperCase() + formatted.slice(1);
    },
    
    /**
     * Форматирование времени
     */
    formatTime(timeString) {
        return timeString;
    },
    
    /**
     * Группировка массива по ключу
     */
    groupBy(array, key) {
        return array.reduce((result, item) => {
            const groupKey = item[key];
            if (!result[groupKey]) {
                result[groupKey] = [];
            }
            result[groupKey].push(item);
            return result;
        }, {});
    },
    
    /**
     * Получить класс цвета для бейджа статуса
     */
    getStatusBadgeClass(status) {
        const statusMap = {
            'Запланирован': 'badge-purple',
            'Анализ': 'badge-cyan',
            'Головная боль': 'badge-pink',
            'ОРВИ': 'badge-pink',
            'Направление на анализы': 'badge-yellow',
            'Инфекционный мононуклеоз': 'badge-yellow',
            'Анемия': 'badge-cyan'
        };
        return statusMap[status] || 'badge-cyan';
    },
    
    /**
     * Показать toast уведомление
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = $(`
            <div class="toast toast-${type}">
                <svg class="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 20 20">
                    ${type === 'success' ? 
                        '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>' :
                        type === 'error' ?
                        '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>' :
                        '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>'
                    }
                </svg>
                <span>${message}</span>
            </div>
        `);
        
        $('#toast-container').append(toast);
        
        setTimeout(() => {
            toast.fadeOut(300, function() {
                $(this).remove();
            });
        }, duration);
    },
    
    /**
     * Показать лоадер
     */
    showLoader(text = 'Загрузка...') {
        return `
            <div class="text-center py-12">
                <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-elia-lavender"></div>
                <p class="mt-4 text-gray-600">${text}</p>
            </div>
        `;
    },
    
    /**
     * Показать сообщение об ошибке
     */
    showError(message) {
        return `
            <div class="text-center py-12">
                <svg class="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p class="mt-4 text-gray-600">${message}</p>
            </div>
        `;
    },
    
    /**
     * Вычислить возраст
     */
    calculateAge(birthDate) {
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    }
};

// Инициализация при загрузке страницы
$(document).ready(() => {
    App.init();
});

