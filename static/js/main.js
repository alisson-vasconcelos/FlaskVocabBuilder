// Main JavaScript file for the truck weighing system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Format numbers in tables
    formatTableNumbers();

    // Add loading spinner to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            showLoadingSpinner();
        });
    });

    // Add confirmation to delete actions (if implemented)
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este registro?')) {
                e.preventDefault();
            }
        });
    });

    // Plate format validation
    const plateInputs = document.querySelectorAll('input[name="placa_veiculo"]');
    plateInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            // Remove non-alphanumeric characters and convert to uppercase
            this.value = this.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
            
            // Add basic format validation
            if (this.value.length >= 7) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            } else {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            }
        });
    });

    // Weight input validation
    const weightInputs = document.querySelectorAll('input[name="quantidade_kg"]');
    weightInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value > 0) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            } else {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            }
        });
    });

    // City input validation
    const cityInputs = document.querySelectorAll('input[name="local_carga"]');
    cityInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const city = this.value.trim();
            if (isValidCity(city)) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            } else {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            }
        });
    });
});

function formatTableNumbers() {
    // Format currency values
    const currencyElements = document.querySelectorAll('.currency');
    currencyElements.forEach(function(element) {
        const value = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
        if (!isNaN(value)) {
            element.textContent = 'R$ ' + value.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    });

    // Format weight values
    const weightElements = document.querySelectorAll('.weight');
    weightElements.forEach(function(element) {
        const value = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
        if (!isNaN(value)) {
            element.textContent = value.toLocaleString('pt-BR', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }) + ' kg';
        }
    });
}

function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Carregando...</span>
        </div>
    `;
    document.body.appendChild(spinner);
    spinner.style.display = 'block';
}

function hideLoadingSpinner() {
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

function isValidCity(city) {
    const lote3Cities = [
        'Guará', 'Arniqueiras', 'Águas Claras', 'Park Way', 'Núcleo Bandeirante',
        'Candangolândia', 'SCIA/Estrutural', 'Vicente Pires', 'Riacho Fundo I',
        'Sobradinho', 'Sobradinho II', 'Fercal', 'Planaltina', 'Arapoanga',
        'Paranoá', 'Itapoã'
    ];

    const lote5Cities = [
        'Lago Sul', 'Jardim Botânico', 'São Sebastião', 'Brazlândia', 'Ceilândia',
        'Taguatinga', 'Sol Nascente/Por do Sol', 'Gama', 'Santa Maria',
        'Recanto das Emas', 'Água Quente', 'Samambaia', 'Riacho Fundo II'
    ];

    const allCities = [...lote3Cities, ...lote5Cities];
    const cityLower = city.toLowerCase();

    return allCities.some(validCity => 
        validCity.toLowerCase().includes(cityLower) || 
        cityLower.includes(validCity.toLowerCase())
    );
}

// Export functions for use in other scripts
window.truckWeighingSystem = {
    formatTableNumbers,
    showLoadingSpinner,
    hideLoadingSpinner,
    isValidCity
};

// Handle print functionality
function printTicket() {
    window.print();
}

// Handle download functionality
function downloadReport(type) {
    const url = type === 'excel' ? '/relatorio/excel' : '/relatorio/csv';
    window.location.href = url;
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href && href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Handle form auto-save (localStorage)
function autoSaveForm() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const formId = form.id;
        if (formId) {
            // Load saved data
            const savedData = localStorage.getItem(`form_${formId}`);
            if (savedData) {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'submit') {
                        input.value = data[key];
                    }
                });
            }

            // Save data on input
            form.addEventListener('input', function() {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(`form_${formId}`, JSON.stringify(data));
            });

            // Clear saved data on successful submit
            form.addEventListener('submit', function() {
                localStorage.removeItem(`form_${formId}`);
            });
        }
    });
}

// Initialize auto-save
autoSaveForm();
