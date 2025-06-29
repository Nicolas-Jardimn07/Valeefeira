// Vale&feira - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Phone number formatting for Brazilian format
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                if (value.length <= 2) {
                    value = value.replace(/(\d{0,2})/, '($1');
                } else if (value.length <= 7) {
                    value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
                } else {
                    value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
                }
                e.target.value = value;
            }
        });
    });

    // Image preview for file uploads
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Remove existing preview
                    const existingPreview = input.parentNode.querySelector('.image-preview');
                    if (existingPreview) {
                        existingPreview.remove();
                    }

                    // Create new preview
                    const preview = document.createElement('div');
                    preview.className = 'image-preview mt-2';
                    preview.innerHTML = `
                        <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                        <div class="mt-1">
                            <small class="text-muted">Prévia da imagem</small>
                        </div>
                    `;
                    input.parentNode.appendChild(preview);
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Price input formatting for Brazilian currency
    const priceInputs = document.querySelectorAll('input[name="price"], input[type="number"][step="0.01"]');
    priceInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                e.target.value = value.toFixed(2);
            }
        });
    });

    // Search form enhancements
    const searchForm = document.querySelector('form[action*="products"], form[action="/"]');
    if (searchForm) {
        const queryInput = searchForm.querySelector('input[name="query"]');
        const categorySelect = searchForm.querySelector('select[name="category"]');
        const citySelect = searchForm.querySelector('select[name="city"]');

        // Auto-submit on filter change (with debounce)
        let searchTimeout;
        function autoSearch() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                if (queryInput && queryInput.value.trim().length > 2) {
                    searchForm.submit();
                }
            }, 1000);
        }

        if (queryInput) {
            queryInput.addEventListener('input', autoSearch);
        }

        // Clear search functionality
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'btn btn-outline-secondary';
        clearButton.innerHTML = '<i class="fas fa-times"></i>';
        clearButton.title = 'Limpar busca';
        clearButton.addEventListener('click', function() {
            if (queryInput) queryInput.value = '';
            if (categorySelect) categorySelect.value = '';
            if (citySelect) citySelect.value = '';
            // Remove URL parameters and redirect to clean page
            window.location.href = window.location.pathname;
        });

        // Add clear button next to search input
        if (queryInput && (queryInput.value || (categorySelect && categorySelect.value) || (citySelect && citySelect.value))) {
            const inputGroup = queryInput.closest('.col-md-4, .col-lg-4');
            if (inputGroup) {
                inputGroup.appendChild(clearButton);
            }
        }
    }

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading states for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
                
                // Re-enable button after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });

    // Copy contact info functionality
    const contactElements = document.querySelectorAll('[data-copy]');
    contactElements.forEach(function(element) {
        element.style.cursor = 'pointer';
        element.title = 'Clique para copiar';
        element.addEventListener('click', function() {
            const textToCopy = this.dataset.copy || this.textContent;
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Show feedback
                const originalText = element.textContent;
                element.textContent = 'Copiado!';
                element.style.color = '#28a745';
                setTimeout(function() {
                    element.textContent = originalText;
                    element.style.color = '';
                }, 2000);
            }).catch(function() {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
            });
        });
    });

    // Infinite scroll for products (basic implementation)
    const productContainer = document.querySelector('.row[data-infinite-scroll]');
    if (productContainer) {
        let loading = false;
        let page = 1;

        function loadMoreProducts() {
            if (loading) return;
            loading = true;

            // Add loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'col-12 text-center my-4';
            loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin fa-2x text-muted"></i>';
            productContainer.appendChild(loadingDiv);

            // Simulate loading delay (in real app, this would be an AJAX call)
            setTimeout(function() {
                loadingDiv.remove();
                loading = false;
                page++;
            }, 1500);
        }

        window.addEventListener('scroll', function() {
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
                loadMoreProducts();
            }
        });
    }

    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card, .card');
    productCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Confirmation dialogs for delete actions
    const deleteLinks = document.querySelectorAll('a[href*="delete"], button[data-action="delete"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Initialize character counters for text inputs with maxlength
    const textInputsWithMax = document.querySelectorAll('input[maxlength], textarea[maxlength]');
    textInputsWithMax.forEach(function(input) {
        const maxLength = input.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'text-muted small text-end';
        counter.style.marginTop = '2px';
        
        function updateCounter() {
            const remaining = maxLength - input.value.length;
            counter.textContent = `${input.value.length}/${maxLength} caracteres`;
            counter.style.color = remaining < 20 ? '#dc3545' : '#6c757d';
        }
        
        updateCounter();
        input.addEventListener('input', updateCounter);
        input.parentNode.appendChild(counter);
    });

    // WhatsApp number validation and formatting
    const whatsappLinks = document.querySelectorAll('a[href*="wa.me"]');
    whatsappLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Ensure WhatsApp link opens in new tab
            this.target = '_blank';
            this.rel = 'noopener noreferrer';
        });
    });

    // Back to top button
    const backToTop = document.createElement('button');
    backToTop.className = 'btn btn-success position-fixed';
    backToTop.style.cssText = `
        bottom: 80px;
        right: 20px;
        z-index: 999;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTop.title = 'Voltar ao topo';
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(backToTop);

    // Show/hide back to top button
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });

    // Local storage for form data (basic implementation)
    const importantForms = document.querySelectorAll('form[method="POST"]');
    importantForms.forEach(function(form) {
        const formId = form.action + form.method;
        
        // Save form data on input
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                const data = new FormData(form);
                const formData = {};
                for (let [key, value] of data.entries()) {
                    formData[key] = value;
                }
                localStorage.setItem('form_' + formId, JSON.stringify(formData));
            });
        });

        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            setTimeout(function() {
                localStorage.removeItem('form_' + formId);
            }, 1000);
        });
    });

    // Accessibility improvements
    const images = document.querySelectorAll('img:not([alt])');
    images.forEach(function(img) {
        img.alt = img.title || 'Imagem';
    });

    // Focus management for modals and dropdowns
    document.addEventListener('shown.bs.modal', function(e) {
        const modal = e.target;
        const firstInput = modal.querySelector('input, textarea, select, button');
        if (firstInput) {
            firstInput.focus();
        }
    });

    // CPF field validation - only allow numbers
    const cpfField = document.querySelector('input[name="cpf"]');
    if (cpfField) {
        cpfField.addEventListener('input', function(e) {
            // Remove any non-numeric characters
            this.value = this.value.replace(/\D/g, '');
            
            // Limit to 11 digits
            if (this.value.length > 11) {
                this.value = this.value.slice(0, 11);
            }
        });

        cpfField.addEventListener('keypress', function(e) {
            // Only allow numeric keys, backspace, delete, tab, escape, enter
            if (!/[0-9]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }

    console.log('Vale&feira - Sistema carregado com sucesso! 🌱');
});

// Utility functions
window.ValeFeira = {
    // Format currency
    formatCurrency: function(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    // Format phone number
    formatPhone: function(phone) {
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 11) {
            return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (cleaned.length === 10) {
            return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        return phone;
    },

    // Show notification
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 2000; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(function() {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    // Validate Brazilian CPF (for future use)
    validateCPF: function(cpf) {
        cpf = cpf.replace(/\D/g, '');
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
        
        let sum = 0, remainder;
        for (let i = 1; i <= 9; i++) {
            sum += parseInt(cpf.substring(i-1, i)) * (11 - i);
        }
        remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.substring(9, 10))) return false;
        
        sum = 0;
        for (let i = 1; i <= 10; i++) {
            sum += parseInt(cpf.substring(i-1, i)) * (12 - i);
        }
        remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.substring(10, 11))) return false;
        
        return true;
    }
};
