document.addEventListener('DOMContentLoaded', () => {
    const branchSelect = document.getElementById('branchSelect');
    const resetBtn = document.getElementById('resetBtn');
    const alertsContainer = document.getElementById('alertsContainer');
    const alertsCountBadge = document.getElementById('alertsCountBadge');
    
    const kpiCapital = document.getElementById('kpiCapital');
    const kpiCritical = document.getElementById('kpiCritical');
    const kpiPending = document.getElementById('kpiPending');
    const kpiExecuted = document.getElementById('kpiExecuted');
    const toastContainer = document.getElementById('toastContainer');

    let currentBranch = branchSelect.value;
    let alertsData = {};
    let executedCount = 0;

    // Fetch alerts from Flask API
    async function loadAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const data = await response.json();
            alertsData = data.alerts;
            executedCount = data.executed_count || 0;
            renderDashboard();
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    }

    // Render alerts and update KPIs
    function renderDashboard() {
        const branchAlerts = alertsData[currentBranch] || [];
        
        // Calculate KPIs
        const capitalAtRisk = branchAlerts.reduce((sum, a) => sum + (a.impact_value || 0), 0);
        const criticalCount = branchAlerts.filter(a => a.critical).length;
        const pendingCount = branchAlerts.length;

        // Update KPI DOM
        kpiCapital.textContent = `$${capitalAtRisk.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        kpiCritical.textContent = criticalCount;
        kpiPending.textContent = pendingCount;
        kpiExecuted.textContent = executedCount;
        alertsCountBadge.textContent = `${pendingCount} activas`;

        // Clear container
        alertsContainer.innerHTML = '';

        if (branchAlerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-check empty-icon"></i>
                    <h4>¡Excelente Trabajo!</h4>
                    <p>No hay alertas ni riesgos pendientes para esta sucursal. El sistema prescriptivo opera al 100% de eficiencia.</p>
                </div>
            `;
            return;
        }

        branchAlerts.forEach(alert => {
            const card = document.createElement('div');
            card.className = `alert-card ${alert.type}`;
            card.id = `card-${alert.id}`;

            card.innerHTML = `
                <div class="card-main-info">
                    <span class="card-header-badge">
                        ${alert.emoji} ${alert.category}
                    </span>
                    <div class="card-title">${alert.title}</div>
                    <div class="card-impact">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <span><b>Impacto Estimado:</b> ${alert.impact}</span>
                    </div>
                    <div class="card-recommendation">
                        🎯 <strong>Acción Prescriptiva Sugerida:</strong> ${alert.recommendation}
                    </div>
                </div>
                <div class="card-action-side">
                    <button class="btn-approve" onclick="approveAction('${alert.id}', '${escapeQuotes(alert.title)}')">
                        <i class="fa-solid fa-check"></i> Aprobar Acción
                    </button>
                </div>
            `;

            alertsContainer.appendChild(card);
        });
    }

    function escapeQuotes(str) {
        return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }

    // Approve Action function
    window.approveAction = async function(alertId, alertTitle) {
        const cardElement = document.getElementById(`card-${alertId}`);
        
        if (cardElement) {
            cardElement.classList.add('removing');
        }

        try {
            const response = await fetch('/api/alerts/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ branch: currentBranch, alert_id: alertId })
            });
            const resData = await response.json();

            if (resData.success) {
                alertsData = resData.alerts;
                executedCount = resData.executed_count;

                showToast(`✅ Acción Aprobada: ${alertTitle}`);

                setTimeout(() => {
                    renderDashboard();
                }, 300);
            }
        } catch (error) {
            console.error('Error approving action:', error);
        }
    };

    // Reset Demo function
    resetBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/alerts/reset', { method: 'POST' });
            const resData = await response.json();
            if (resData.success) {
                alertsData = resData.alerts;
                executedCount = resData.executed_count;
                showToast('🔄 Datos de demostración restablecidos');
                renderDashboard();
            }
        } catch (error) {
            console.error('Error resetting demo:', error);
        }
    });

    // Branch switch event
    branchSelect.addEventListener('change', (e) => {
        currentBranch = e.target.value;
        renderDashboard();
    });

    // Toast Notification Creator
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${message}</span>`;
        
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // Initial load
    loadAlerts();
});
