// Tênis de Mesa Check-in System - JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Form validation
    setupFormValidation();
    
    // Auto-dismiss alerts
    setupAutoAlerts();
    
    // Real-time updates
    setupRealTimeUpdates();
    
    // Confirmation dialogs
    setupConfirmationDialogs();
    
    console.log('Sistema de Check-in inicializado');
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const nome = form.querySelector('input[name="nome"]');
            const creditos = form.querySelector('input[name="creditos"]');
            
            // Validar nome
            if (nome && nome.value.trim().length < 2) {
                event.preventDefault();
                showAlert('Nome deve ter pelo menos 2 caracteres', 'error');
                nome.focus();
                return;
            }
            
            // Validar créditos
            if (creditos) {
                const creditosValue = parseInt(creditos.value);
                if (isNaN(creditosValue) || creditosValue < 0 || creditosValue > 20) {
                    event.preventDefault();
                    showAlert('Créditos deve ser um número entre 0 e 20', 'error');
                    creditos.focus();
                    return;
                }
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                
                // Clear button and add spinner icon safely
                submitBtn.textContent = '';
                submitBtn.disabled = true;
                
                const spinner = document.createElement('i');
                spinner.className = 'fas fa-spinner fa-spin';
                const text = document.createTextNode(' Processando...');
                
                submitBtn.appendChild(spinner);
                submitBtn.appendChild(text);
                
                // Restore button after timeout (fallback)
                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

/**
 * Setup auto-dismissing alerts
 */
function setupAutoAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    
    alerts.forEach(alert => {
        // Auto-dismiss success alerts after 3 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 3000);
        }
        
        // Auto-dismiss error alerts after 5 seconds
        if (alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

/**
 * Setup real-time updates for user panel
 */
function setupRealTimeUpdates() {
    // Check if we're on the user panel
    if (window.location.pathname.includes('painel_usuario')) {
        // Update every 30 seconds
        setInterval(updateVagasStatus, 30000);
    }
}

/**
 * Update vagas status without full page reload
 */
function updateVagasStatus() {
    // This would typically make an AJAX call to get updated status
    // For now, we'll just add a visual indicator that data is being refreshed
    const statusCards = document.querySelectorAll('.card .badge');
    
    statusCards.forEach(badge => {
        badge.style.opacity = '0.5';
        setTimeout(() => {
            badge.style.opacity = '1';
        }, 500);
    });
}

/**
 * Setup confirmation dialogs
 */
function setupConfirmationDialogs() {
    // Check-in confirmations
    const checkinLinks = document.querySelectorAll('a[href*="/checkin/"]');
    checkinLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const horario = this.href.split('/').pop();
            if (!confirm(`Confirma a reserva para o horário ${horario}?\n\nSerá descontado 1 crédito da sua conta.`)) {
                event.preventDefault();
            }
        });
    });
    
    // Cancellation confirmations
    const cancelLinks = document.querySelectorAll('a[href*="/cancelar/"]');
    cancelLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const horario = this.href.split('/').pop();
            if (!confirm(`Tem certeza que deseja cancelar sua reserva para ${horario}?\n\nO crédito será reembolsado.`)) {
                event.preventDefault();
            }
        });
    });
    
    // Admin form confirmations
    const adminForms = document.querySelectorAll('form[action*="admin"]');
    adminForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const nome = form.querySelector('input[name="nome"]').value;
            const creditos = form.querySelector('input[name="creditos"]').value;
            
            if (!confirm(`Confirma o cadastro do aluno?\n\nNome: ${nome}\nCréditos: ${creditos}`)) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Show custom alert
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    
    // Create icon element safely
    const icon = document.createElement('i');
    icon.className = `fas fa-${getAlertIcon(type)}`;
    
    // Create message text safely
    const messageText = document.createTextNode(' ' + message);
    
    // Create close button safely
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'btn-close';
    closeBtn.setAttribute('data-bs-dismiss', 'alert');
    
    // Append elements safely
    alertDiv.appendChild(icon);
    alertDiv.appendChild(messageText);
    alertDiv.appendChild(closeBtn);
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 3000);
    }
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-triangle';
        case 'warning': return 'exclamation-triangle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

/**
 * Format time display
 */
function formatTime(timeString) {
    try {
        const [hours, minutes] = timeString.split(':');
        return `${hours}:${minutes}h`;
    } catch (e) {
        return timeString;
    }
}

/**
 * Update page title with notification count
 */
function updatePageTitle(count = 0) {
    const baseTitle = document.title.split(' - ')[0];
    document.title = count > 0 ? `(${count}) ${baseTitle}` : baseTitle;
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(event) {
    // Ctrl + Enter to submit forms
    if (event.ctrlKey && event.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            activeForm.submit();
        }
    }
    
    // Escape to close modals/alerts
    if (event.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = bootstrap.Alert.getInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        });
    }
});

/**
 * Smooth scroll to elements
 */
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

/**
 * Local storage helpers
 */
const storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('Não foi possível salvar no localStorage:', e);
        }
    },
    
    get: function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.warn('Não foi possível ler do localStorage:', e);
            return null;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('Não foi possível remover do localStorage:', e);
        }
    }
};

/**
 * Remember user name in login form
 */
const nomeInput = document.querySelector('input[name="nome"]');
if (nomeInput) {
    // Load saved name
    const savedName = storage.get('lastUserName');
    if (savedName) {
        nomeInput.value = savedName;
    }
    
    // Save name on form submit
    nomeInput.closest('form')?.addEventListener('submit', function() {
        if (nomeInput.value.trim()) {
            storage.set('lastUserName', nomeInput.value.trim());
        }
    });
}

/**
 * Add loading states to buttons
 */
function addLoadingState(button, text = 'Processando...') {
    const originalText = button.textContent;
    
    // Clear button content safely
    button.textContent = '';
    button.disabled = true;
    
    // Create spinner and text elements safely
    const spinner = document.createElement('i');
    spinner.className = 'fas fa-spinner fa-spin';
    const textNode = document.createTextNode(' ' + text);
    
    button.appendChild(spinner);
    button.appendChild(textNode);
    
    return function() {
        button.textContent = originalText;
        button.disabled = false;
    };
}

/**
 * Utility function to get current time in Brazil timezone
 */
function getCurrentBrazilTime() {
    return new Date().toLocaleString('pt-BR', {
        timeZone: 'America/Sao_Paulo',
        hour12: false
    });
}

/**
 * Check if cancellation is still allowed
 */
function canCancel() {
    const now = new Date();
    const currentHour = now.getHours();
    return currentHour < 15; // Before 3 PM
}

// Export functions for global use
window.TenisMesaSystem = {
    showAlert,
    formatTime,
    updatePageTitle,
    smoothScrollTo,
    addLoadingState,
    getCurrentBrazilTime,
    canCancel,
    storage
};

console.log('Sistema de Tênis de Mesa carregado com sucesso! 🏓');
