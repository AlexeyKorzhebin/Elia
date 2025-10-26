"""E2E тесты с Playwright"""
import pytest
import asyncio
import subprocess
import time
from playwright.async_api import async_playwright, Page, expect


# Флаг для запуска сервера только один раз
server_process = None


@pytest.fixture(scope="module")
def setup_server():
    """Запустить тестовый сервер FastAPI"""
    global server_process
    
    # Загружаем fixtures
    print("Загрузка тестовых данных...")
    subprocess.run(["python", "-m", "app.fixtures"], check=True)
    
    # Запускаем сервер
    print("Запуск тестового сервера...")
    server_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Ждём запуска сервера
    time.sleep(3)
    
    yield
    
    # Останавливаем сервер
    print("Остановка сервера...")
    server_process.terminate()
    server_process.wait()


@pytest.fixture(scope="function")
async def page(setup_server):
    """Создать страницу Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        yield page
        
        await context.close()
        await browser.close()


@pytest.mark.e2e
class TestPatientsListScreen:
    """Тесты главного экрана со списком пациентов"""
    
    async def test_load_patients_list(self, page: Page):
        """UC-01: Просмотр списка пациентов"""
        await page.goto("http://127.0.0.1:8000/")
        
        # Проверяем заголовок
        await expect(page.locator("h1")).to_contain_text("Мои пациенты")
        
        # Ждём загрузки приёмов
        await page.wait_for_selector(".appointment-card", timeout=5000)
        
        # Проверяем, что карточки загружены
        cards = await page.locator(".appointment-card").count()
        assert cards > 0, "Должны быть загружены карточки пациентов"
    
    async def test_search_patient(self, page: Page):
        """UC-02: Поиск пациента по имени"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        
        # Вводим поисковый запрос
        search_input = page.locator("#search-input")
        await search_input.fill("Иванов")
        
        # Ждём обновления результатов
        await page.wait_for_timeout(500)
        
        # Проверяем, что есть результаты поиска
        cards = await page.locator(".appointment-card").count()
        assert cards >= 1, "Должны быть найдены пациенты"
        
        # Проверяем, что в результатах есть "Иванов"
        card_text = await page.locator(".appointment-card").first.text_content()
        assert "Иванов" in card_text
    
    async def test_open_patient_card(self, page: Page):
        """UC-03: Открытие карточки пациента"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        
        # Кликаем на первую карточку
        first_card = page.locator(".appointment-card").first
        patient_name = await first_card.locator("h3").text_content()
        await first_card.click()
        
        # Ждём загрузки карточки пациента
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        await page.wait_for_selector("h1", timeout=5000)
        
        # Проверяем, что открылась карточка
        header = await page.locator("h1").text_content()
        assert len(header) > 0, "Должен быть заголовок с именем пациента"
        
        # Проверяем наличие вкладок
        tabs = await page.locator(".tab-button").count()
        assert tabs == 3, "Должны быть 3 вкладки"


@pytest.mark.e2e
class TestPatientCardScreen:
    """Тесты экрана карточки пациента"""
    
    async def test_view_digital_portrait(self, page: Page):
        """UC-04: Просмотр цифрового портрета"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        
        # Открываем карточку
        await page.locator(".appointment-card").first.click()
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        
        # Проверяем, что открыта вкладка "Цифровой портрет"
        digital_portrait_tab = page.locator('[data-tab="digital-portrait"]')
        await expect(digital_portrait_tab).to_have_class(/tab-active/)
        
        # Проверяем наличие секций
        await expect(page.locator("text=Основные данные")).to_be_visible()
        await expect(page.locator("text=Хронические заболевания")).to_be_visible()
        await expect(page.locator("text=Последние заболевания")).to_be_visible()
        await expect(page.locator("text=Основные показатели здоровья")).to_be_visible()
    
    async def test_switch_tabs(self, page: Page):
        """UC-09: Переключение между вкладками"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        await page.locator(".appointment-card").first.click()
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        
        # Переключаемся на вкладку "Анамнез"
        anamnesis_tab = page.locator('[data-tab="anamnesis"]')
        await anamnesis_tab.click()
        await expect(anamnesis_tab).to_have_class(/tab-active/)
        await expect(page.locator("text=Цель обращения")).to_be_visible()
        
        # Переключаемся на вкладку "Стенограмма"
        stenogram_tab = page.locator('[data-tab="stenogram"]')
        await stenogram_tab.click()
        await expect(stenogram_tab).to_have_class(/tab-active/)
        await expect(page.locator("#audio-upload-section")).to_be_visible()
    
    async def test_fill_anamnesis_form(self, page: Page):
        """UC-05: Заполнение формы анамнеза"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        await page.locator(".appointment-card").first.click()
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        
        # Переходим на вкладку "Анамнез"
        await page.locator('[data-tab="anamnesis"]').click()
        await page.wait_for_selector("#anamnesis-form", timeout=2000)
        
        # Заполняем форму
        await page.fill("#purpose-field", "Консультация терапевта")
        await page.fill("#complaints-field", "Головная боль, повышенная температура")
        await page.fill("#anamnesis-field", "Симптомы появились 2 дня назад")
        
        # Сохраняем черновик
        await page.click("#save-report-btn")
        
        # Ждём уведомления об успехе
        await page.wait_for_selector(".toast-success", timeout=3000)
        toast = await page.locator(".toast-success").text_content()
        assert "сохранён" in toast.lower()
    
    async def test_submit_to_mis(self, page: Page):
        """UC-08: Имитация отправки в МИС"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        await page.locator(".appointment-card").first.click()
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        
        # Переходим на вкладку "Анамнез"
        await page.locator('[data-tab="anamnesis"]').click()
        await page.wait_for_selector("#anamnesis-form", timeout=2000)
        
        # Заполняем форму
        await page.fill("#purpose-field", "Тест")
        await page.fill("#complaints-field", "Тест")
        
        # Нажимаем "Занести в МИС"
        await page.click("#submit-to-mis-btn")
        
        # Ждём завершения (имитация занимает 3 секунды)
        await page.wait_for_selector(".toast-success", timeout=5000)
        toast = await page.locator(".toast-success").text_content()
        assert "МИС" in toast
    
    async def test_back_to_patients(self, page: Page):
        """UC-10: Навигация назад к списку пациентов"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        await page.locator(".appointment-card").first.click()
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        
        # Нажимаем кнопку "Назад"
        await page.click("#back-button")
        
        # Проверяем, что вернулись к списку
        await expect(page.locator("#patients-screen")).to_be_visible()
        await expect(page.locator("h1")).to_contain_text("Мои пациенты")


@pytest.mark.e2e
@pytest.mark.slow
class TestAudioUpload:
    """Тесты загрузки и транскрибации аудио"""
    
    async def test_upload_audio_file(self, page: Page):
        """UC-06: Загрузка аудиофайла"""
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_selector(".appointment-card", timeout=5000)
        await page.locator(".appointment-card").first.click()
        await page.wait_for_selector("#patient-card-screen", timeout=5000)
        
        # Переходим на вкладку "Стенограмма"
        await page.locator('[data-tab="stenogram"]').click()
        await page.wait_for_selector("#audio-upload-section", timeout=2000)
        
        # Проверяем наличие зоны загрузки
        await expect(page.locator(".drop-zone")).to_be_visible()
    
    async def test_transcribe_audio(self, page: Page):
        """UC-07: Имитация транскрибации"""
        # Этот тест требует создания реального аудиофайла
        # Для MVP можно пропустить или реализовать через mock
        pytest.skip("Требуется реальный аудиофайл для загрузки")


@pytest.mark.e2e
class TestUIComponents:
    """Тесты UI компонентов"""
    
    async def test_sidebar_navigation(self, page: Page):
        """Тест навигации в боковой панели"""
        await page.goto("http://127.0.0.1:8000/")
        
        # Проверяем наличие логотипа
        await expect(page.locator("text=elia")).to_be_visible()
        
        # Проверяем пункты меню
        await expect(page.locator("text=Мои пациенты")).to_be_visible()
        await expect(page.locator("text=Организация")).to_be_visible()
        await expect(page.locator("text=Настройки")).to_be_visible()
        await expect(page.locator("text=Поддержка")).to_be_visible()
        
        # Проверяем профиль врача
        await expect(page.locator("text=Тимофей Арзамасцев")).to_be_visible()
    
    async def test_responsive_layout(self, page: Page):
        """Тест адаптивности интерфейса"""
        await page.goto("http://127.0.0.1:8000/")
        
        # Проверяем на разных размерах экрана
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await expect(page.locator("h1")).to_be_visible()
        
        await page.set_viewport_size({"width": 1024, "height": 768})
        await expect(page.locator("h1")).to_be_visible()

