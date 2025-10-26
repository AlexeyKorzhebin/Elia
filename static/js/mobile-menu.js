/**
 * Модуль мобильной навигации
 * Управление бургер-меню и overlay
 */

const MobileMenu = {
    isOpen: false,
    
    /**
     * Инициализация модуля
     */
    init() {
        console.log('Инициализация мобильного меню...');
        
        // Обработчик клика на бургер
        $(document).on('click', '#mobile-menu-button', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Обработчик клика на overlay
        $(document).on('click', '#mobile-menu-overlay', () => {
            this.close();
        });
        
        // Обработчик клика на пункты меню
        $(document).on('click', '#mobile-sidebar a', () => {
            this.close();
        });
        
        // Закрытие при изменении размера окна на desktop
        $(window).on('resize', () => {
            if (window.innerWidth >= 1024 && this.isOpen) {
                this.close();
            }
        });
        
        // Закрытие по Escape
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    },
    
    /**
     * Переключить состояние меню
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    },
    
    /**
     * Открыть меню
     */
    open() {
        this.isOpen = true;
        
        // Показываем overlay
        $('#mobile-menu-overlay').removeClass('hidden').addClass('mobile-menu-overlay-active');
        
        // Выдвигаем sidebar
        $('#mobile-sidebar').addClass('mobile-sidebar-open');
        
        // Блокируем скролл body
        $('body').addClass('overflow-hidden');
        
        // Анимируем иконку бургера
        $('#mobile-menu-button').addClass('mobile-menu-button-active');
        
        console.log('Мобильное меню открыто');
    },
    
    /**
     * Закрыть меню
     */
    close() {
        this.isOpen = false;
        
        // Скрываем overlay
        $('#mobile-menu-overlay').removeClass('mobile-menu-overlay-active');
        setTimeout(() => {
            $('#mobile-menu-overlay').addClass('hidden');
        }, 300); // Ждём окончания анимации
        
        // Прячем sidebar
        $('#mobile-sidebar').removeClass('mobile-sidebar-open');
        
        // Разблокируем скролл body
        $('body').removeClass('overflow-hidden');
        
        // Возвращаем иконку бургера в исходное состояние
        $('#mobile-menu-button').removeClass('mobile-menu-button-active');
        
        console.log('Мобильное меню закрыто');
    }
};

