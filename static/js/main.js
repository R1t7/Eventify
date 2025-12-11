// Main JavaScript for SGEA

// Simple page navigation
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('.form-control[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('error');
                    isValid = false;
                } else {
                    input.classList.remove('error');
                }
            });

            // Remove error class on input
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    this.classList.remove('error');
                });
            });
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Modal functionality
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });

    // Confirmation dialogs for dangerous actions
    const dangerButtons = document.querySelectorAll('.btn-danger');
    dangerButtons.forEach(btn => {
        if (!btn.hasAttribute('onclick')) {
            btn.addEventListener('click', function(e) {
                if (!confirm('Tem certeza que deseja realizar esta ação?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Date validation for event creation
    const dataInicio = document.getElementById('data_inicio');
    const dataFim = document.getElementById('data_fim');

    if (dataInicio && dataFim) {
        dataInicio.addEventListener('change', function() {
            dataFim.min = this.value;
        });
    }

    // Senha validation for registration
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');

    if (password1 && password2) {
        password2.addEventListener('input', function() {
            if (this.value !== password1.value) {
                this.setCustomValidity('As senhas não coincidem');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Máscara de telefone (XX) XXXXX-XXXX
    const telefoneInputs = document.querySelectorAll('input[name="telefone"]');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito

            if (value.length > 11) {
                value = value.slice(0, 11); // Limita a 11 dígitos
            }

            // Aplica a máscara
            if (value.length <= 2) {
                e.target.value = value;
            } else if (value.length <= 7) {
                e.target.value = `(${value.slice(0, 2)}) ${value.slice(2)}`;
            } else {
                e.target.value = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7)}`;
            }
        });

        // Remove a máscara ao submeter o formulário para enviar apenas números
        input.closest('form')?.addEventListener('submit', function() {
            input.value = input.value.replace(/\D/g, '');
        });
    });
});
