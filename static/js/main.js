document.addEventListener('DOMContentLoaded', () => {
    const branchSelect = document.getElementById('branchSelect');
    const resetBtn = document.getElementById('resetBtn');
    const alertsTbody = document.getElementById('alertsTbody');
    const alertsCountBadge = document.getElementById('alertsCountBadge');
    
    const kpiCritical = document.getElementById('kpiCritical');
    const kpiPending = document.getElementById('kpiPending');
    const kpiExecuted = document.getElementById('kpiExecuted');
    const toastContainer = document.getElementById('toastContainer');

    let currentBranch = branchSelect.value;
    let alertsData = {};
    let executedCount = 0;

    // Fetch alerts from Flask API (connected to Ariel's backend)
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

    // Render alerts in executive table using Ariel's exact output fields
    function renderDashboard() {
        const branchAlerts = alertsData[currentBranch] || [];
        
        // Calculate KPIs
        const criticalCount = branchAlerts.filter(a => a.critical || a.tipo_alerta === 'roja').length;
        const pendingCount = branchAlerts.length;

        // Update KPI DOM
        kpiCritical.textContent = criticalCount;
        kpiPending.textContent = pendingCount;
        kpiExecuted.textContent = executedCount;
        alertsCountBadge.textContent = `${pendingCount} activas`;

        // Clear table body
        alertsTbody.innerHTML = '';

        if (branchAlerts.length === 0) {
            alertsTbody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="4">
                        <div class="empty-state-box">
                            <i class="fa-solid fa-circle-check empty-icon"></i>
                            <h4>Sucursal Operando en Estado Óptimo</h4>
                            <p>No existen riesgos pendientes detectados por el Motor de Reglas para esta sucursal.</p>
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
            let categoryIcon = '';

            if (alert.tipo_alerta === 'roja') {
                categoryIcon = '<i class="fa-solid fa-triangle-exclamation"></i>';
                badgeHtml = `<span class="status-badge badge-roja">${categoryIcon} Alerta Roja (FEFO)</span>`;
            } else if (alert.tipo_alerta === 'amarilla') {
                categoryIcon = '<i class="fa-solid fa-boxes-stacked"></i>';
                badgeHtml = `<span class="status-badge badge-amarilla">${categoryIcon} Alerta Amarilla (FIFO)</span>`;
            } else if (alert.tipo_alerta === 'morada') {
                categoryIcon = '<i class="fa-solid fa-calendar-day"></i>';
                badgeHtml = `<span class="status-badge badge-morada">${categoryIcon} Alerta Morada (Demanda)</span>`;
            }

            // Staffing recommendation text formatting
            let staffHtml = '';
            if (alert.recomendacion_personal && alert.recomendacion_personal !== 'N/A') {
                staffHtml = `<div class="recommendation-staff"><i class="fa-solid fa-user-check"></i> Personal: ${alert.recomendacion_personal}</div>`;
            }

            tr.innerHTML = `
                <td>${badgeHtml}</td>
                <td>
                    <div class="item-title">${alert.titulo}</div>
                    <div class="item-subtext">${alert.descripcion}</div>
                </td>
                <td>
                    <div class="recommendation-inv">${alert.recomendacion_inventario}</div>
                    ${staffHtml}
                </td>
                <td style="text-align: center;">
                    <button class="btn-action" onclick="approveAction('${alert.id}', '${escapeQuotes(alert.titulo)}')">
                        <i class="fa-solid fa-check"></i> ${alert.texto_boton || 'Aprobar Acción'}
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

                showToast(`Acción ejecutada correctamente: ${alertTitle}`);

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
                showToast('Datos del Motor Restablecidos');
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
