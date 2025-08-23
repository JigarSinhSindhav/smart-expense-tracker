// App State
let categoryChart = null;
let monthlyChart = null;

// API Base URL
const API_BASE = '/api';

// DOM Elements
const expenseForm = document.getElementById('expenseForm');
const descriptionInput = document.getElementById('description');
const amountInput = document.getElementById('amount');
const categorySelect = document.getElementById('category');
const notesInput = document.getElementById('notes');
const predictionDiv = document.getElementById('prediction');
const expensesList = document.getElementById('expensesList');
const totalAmountSpan = document.getElementById('totalAmount');
const refreshButton = document.getElementById('refreshExpenses');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    console.log('Expense Tracker App Starting...');
    
    // Bind event listeners
    bindEventListeners();
    
    // Load initial data
    loadExpenses();
    loadAnalytics();
    
    console.log('App initialized successfully');
});

// Event Listeners
function bindEventListeners() {
    // Form submission
    expenseForm.addEventListener('submit', handleExpenseSubmit);
    
    // Real-time prediction on description input
    descriptionInput.addEventListener('input', debounce(handleDescriptionChange, 500));
    
    // Refresh button
    refreshButton.addEventListener('click', () => {
        loadExpenses();
        loadAnalytics();
    });
}

// Form Handlers
async function handleExpenseSubmit(e) {
    e.preventDefault();
    
    const formData = {
        description: descriptionInput.value.trim(),
        amount: parseFloat(amountInput.value),
        category: categorySelect.value,
        notes: notesInput.value.trim()
    };
    
    // Validate form
    if (!validateExpenseForm(formData)) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/expenses`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Expense added successfully!', 'success');
            resetForm();
            loadExpenses();
            loadAnalytics();
        } else {
            throw new Error(result.error || 'Failed to add expense');
        }
    } catch (error) {
        console.error('Error adding expense:', error);
        showToast('Failed to add expense: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleDescriptionChange() {
    const description = descriptionInput.value.trim();
    
    if (description.length < 3) {
        hidePrediction();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showPrediction(result);
            // Auto-select predicted category
            if (categorySelect.value === '') {
                categorySelect.value = result.category;
            }
        }
    } catch (error) {
        console.error('Error getting prediction:', error);
        hidePrediction();
    }
}

// Data Loading Functions
async function loadExpenses() {
    try {
        const response = await fetch(`${API_BASE}/expenses`);
        const expenses = await response.json();
        
        if (response.ok) {
            renderExpensesList(expenses);
        } else {
            throw new Error('Failed to load expenses');
        }
    } catch (error) {
        console.error('Error loading expenses:', error);
        showToast('Failed to load expenses', 'error');
    }
}

async function loadAnalytics() {
    try {
        // Load category analytics
        const categoryResponse = await fetch(`${API_BASE}/analytics/categories`);
        const categoryData = await categoryResponse.json();
        
        // Load total spending
        const totalResponse = await fetch(`${API_BASE}/analytics/total`);
        const totalData = await totalResponse.json();
        
        // Load monthly analytics
        const monthlyResponse = await fetch(`${API_BASE}/analytics/monthly`);
        const monthlyData = await monthlyResponse.json();
        
        if (categoryResponse.ok && totalResponse.ok && monthlyResponse.ok) {
            updateTotalSpending(totalData.total);
            renderCategoryChart(categoryData);
            renderMonthlyChart(monthlyData);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Failed to load analytics', 'error');
    }
}

// Rendering Functions
function renderExpensesList(expenses) {
    if (expenses.length === 0) {
        expensesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-receipt"></i>
                <h3>No expenses yet</h3>
                <p>Add your first expense to get started!</p>
            </div>
        `;
        return;
    }
    
    expensesList.innerHTML = expenses.map(expense => `
        <div class="expense-item" data-id="${expense.id}">
            <div class="expense-details">
                <div class="expense-description">${escapeHtml(expense.description)}</div>
                <div class="expense-meta">
                    <span class="expense-category">
                        ${getCategoryIcon(expense.category)} ${expense.category}
                    </span>
                    <span class="expense-date">
                        <i class="fas fa-calendar"></i> ${formatDate(expense.date_added)}
                    </span>
                    ${expense.predicted_category && expense.predicted_category !== expense.category ? 
                        `<span class="prediction-info">
                            <i class="fas fa-robot"></i> Predicted: ${expense.predicted_category}
                        </span>` : ''
                    }
                </div>
                ${expense.notes ? `<div class="expense-notes">${escapeHtml(expense.notes)}</div>` : ''}
            </div>
            <div class="expense-amount">$${expense.amount.toFixed(2)}</div>
            <div class="expense-actions">
                <button class="btn btn-danger" onclick="deleteExpense(${expense.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function renderCategoryChart(data) {
    if (data.length === 0) {
        const ctx = document.getElementById('categoryChart');
        if (categoryChart) {
            categoryChart.destroy();
            categoryChart = null;
        }
        ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
        return;
    }
    
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                data: data.map(item => item.total_amount),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderMonthlyChart(data) {
    if (data.length === 0) {
        const ctx = document.getElementById('monthlyChart');
        if (monthlyChart) {
            monthlyChart.destroy();
            monthlyChart = null;
        }
        ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
        return;
    }
    
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    // Group data by month
    const monthlyTotals = {};
    data.forEach(item => {
        if (!monthlyTotals[item.month]) {
            monthlyTotals[item.month] = 0;
        }
        monthlyTotals[item.month] += item.total_amount;
    });
    
    const sortedMonths = Object.keys(monthlyTotals).sort().slice(-6); // Last 6 months
    
    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedMonths.map(month => formatMonthLabel(month)),
            datasets: [{
                label: 'Monthly Spending',
                data: sortedMonths.map(month => monthlyTotals[month]),
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderColor: '#667eea',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Total: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

// Utility Functions
function showPrediction(prediction) {
    const confidenceClass = prediction.confidence > 0.8 ? 'high-confidence' : 'low-confidence';
    const confidenceText = (prediction.confidence * 100).toFixed(0);
    
    predictionDiv.innerHTML = `
        <i class="fas fa-robot"></i>
        AI suggests: <strong>${prediction.category}</strong>
        (${confidenceText}% confidence)
    `;
    predictionDiv.className = `prediction-result show ${confidenceClass}`;
}

function hidePrediction() {
    predictionDiv.innerHTML = '';
    predictionDiv.className = 'prediction-result';
}

function updateTotalSpending(total) {
    totalAmountSpan.textContent = `$${total.toFixed(2)}`;
}

function validateExpenseForm(data) {
    if (!data.description) {
        showToast('Description is required', 'error');
        return false;
    }
    
    if (!data.amount || data.amount <= 0) {
        showToast('Valid amount is required', 'error');
        return false;
    }
    
    if (!data.category) {
        showToast('Category is required', 'error');
        return false;
    }
    
    return true;
}

function resetForm() {
    expenseForm.reset();
    hidePrediction();
}

async function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/expenses/${expenseId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Expense deleted successfully', 'success');
            loadExpenses();
            loadAnalytics();
        } else {
            throw new Error('Failed to delete expense');
        }
    } catch (error) {
        console.error('Error deleting expense:', error);
        showToast('Failed to delete expense', 'error');
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    loadingOverlay.classList.toggle('show', show);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<div class="toast-message">${escapeHtml(message)}</div>`;
    
    toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatMonthLabel(monthString) {
    const [year, month] = monthString.split('-');
    return new Date(year, month - 1).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short'
    });
}

function getCategoryIcon(category) {
    const icons = {
        'Food': '🍔',
        'Transportation': '🚗',
        'Entertainment': '🎬',
        'Other': '📦'
    };
    return icons[category] || '📦';
}
