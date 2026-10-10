document.addEventListener('DOMContentLoaded', () => {
    const branchSelect = document.getElementById('branchSelect');
    const resetBtn = document.getElementById('resetBtn');
    const alertsTbody = document.getElementById('alertsTbody');
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

    // Render alerts in executive table
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
        alertsCountBadge.textContent = `${pendingCount} pendientes`;

        // Clear table body
        alertsTbody.innerHTML = '';

        if (branchAlerts.length === 0) {
            alertsTbody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="5">
                        <div class="empty-state-box">
                            <i class="fa-solid fa-circle-check empty-icon"></i>
                            <h4>Sucursal Operando con Eficiencia Total</h4>
                            <p>No existen riesgos pendientes en inventario, bodega o rotación de personal para esta sucursal.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        branchAlerts.forEach(alert => {
            const tr = document.createElement('tr');
            tr.id = `row-${alert.id}`;

            let badgeHtml = '';
            if (alert.type === 'red') {
                badgeHtml = `<span class="status-badge badge-red"><i class="fa-solid fa-triangle-exclamation"></i> Crítico (FEFO)</span>`;
            } else if (alert.type === 'yellow') {
                badgeHtml = `<span class="status-badge badge-yellow"><i class="fa-solid fa-boxes-stacked"></i> Bodega (FIFO)</span>`;
            } else if (alert.type === 'blue') {
                badgeHtml = `<span class="status-badge badge-blue"><i class="fa-solid fa-vault"></i> Estancado</span>`;
            } else if (alert.type === 'purple') {
                badgeHtml = `<span class="status-badge badge-purple"><i class="fa-solid fa-calendar-day"></i> Evento</span>`;
            }

            tr.innerHTML = `
                <td>${badgeHtml}</td>
                <td>
                    <div class="item-title">${alert.title}</div>
                    <div class="item-subtext">${alert.category}</div>
                </td>
                <td>
                    <div class="impact-text">${alert.impact}</div>
                </td>
                <td>
                    <div class="recommendation-text">${alert.recommendation}</div>
                </td>
                <td style="text-align: center;">
                    <button class="btn-action" onclick="approveAction('${alert.id}', '${escapeQuotes(alert.title)}')">
                        <i class="fa-solid fa-check"></i> Aprobar Acción
                    </button>
                </td>
            `;

            alertsTbody.appendChild(tr);
        });
    }

    function escapeQuotes(str) {
        return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }

    // Approve Action function
    window.approveAction = async function(alertId, alertTitle) {
        const rowElement = document.getElementById(`row-${alertId}`);
        
        if (rowElement) {
            rowElement.classList.add('removing');
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

                showToast(`Acción aprobada correctamente: ${alertTitle}`);

                setTimeout(() => {
                    renderDashboard();
                }, 250);
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
                showToast('Datos de demo restablecidos');
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
        toast.className = 'toast-msg';
        toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${message}</span>`;
        
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.25s ease';
            setTimeout(() => toast.remove(), 250);
        }, 3000);
    }

    // Initial load
    loadAlerts();
});
