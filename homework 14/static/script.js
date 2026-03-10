document.addEventListener('DOMContentLoaded', () => {
    // 1. Плавное появление всех карточек при загрузке страницы
    const cards = document.querySelectorAll('.card, .news-card, .weather-widget');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 150 * index);
    });

    // 2. Анимация цифр для Калькулятора (Эффект счетчика)
    const animateValue = (obj, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    // Ищем итоговую сумму (если мы на странице калькулятора)
    const totalDisplay = document.querySelector('.total-amount');
    if (totalDisplay) {
        const finalValue = parseInt(totalDisplay.innerText.replace(/\D/g, ''));
        animateValue(totalDisplay, 0, finalValue, 1500); // Считает за 1.5 секунды
    }

    // 3. Эффект "пульсации" для виджета погоды
    const weatherWidget = document.querySelector('.weather-widget');
    if (weatherWidget) {
        setInterval(() => {
            weatherWidget.style.boxShadow = `0 0 35px rgba(58, 123, 213, ${Math.random() * 0.5 + 0.2})`;
        }, 2000);
    }

    // 4. Валидация форм (чтобы не отправляли пустые поля)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('input[required]');
            inputs.forEach(input => {
                if (!input.value) {
                    input.style.borderColor = '#ff4757';
                    e.preventDefault();
                }
            });
        });
    });
});