document.addEventListener('DOMContentLoaded', () => {
    const branchSelect = document.getElementById('branchSelect');
    const resetBtn = document.getElementById('resetBtn');
    const alertsTbody = document.getElementById('alertsTbody');
    const alertsCountBadge = document.getElementById('alertsCountBadge');
    
    const kpiCritical = document.getElementById('kpiCritical');
    const kpiPending = document.getElementById('kpiPending');
    const kpiExecuted = document.getElementById('kpiExecuted');
    const kpiSaved = document.getElementById('kpiSaved');
    const toastContainer = document.getElementById('toastContainer');

    let currentBranch = branchSelect.value;
    let alertsData = {};
    let executedCount = 0;
    let totalSavedMxn = 0.0;
    let totalOriginalLossMxn = 0.0;

    // Fetch alerts from Flask API (connected to Ariel's backend)
    async function loadAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const data = await response.json();
            alertsData = data.alerts;
            executedCount = data.executed_count || 0;
            totalSavedMxn = data.total_saved_mxn || 0.0;
            totalOriginalLossMxn = data.total_original_loss_mxn || 0.0;
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
        if (kpiSaved) {
            kpiSaved.textContent = `$${totalSavedMxn.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
        
        // Update Modal Data
        const compLoss = document.getElementById('compLoss');
        const compGain = document.getElementById('compGain');
        if (compLoss) {
            compLoss.textContent = `-$${totalOriginalLossMxn.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
        if (compGain) {
            compGain.textContent = `+$${totalSavedMxn.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }

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
            } else if (alert.tipo_alerta === 'azul') {
                categoryIcon = '<i class="fa-solid fa-clock-rotate-left"></i>';
                badgeHtml = `<span class="status-badge badge-azul">${categoryIcon} Alerta Azul (Lenta Rotación)</span>`;
            } else if (alert.tipo_alerta === 'morada') {
                categoryIcon = '<i class="fa-solid fa-calendar-day"></i>';
                badgeHtml = `<span class="status-badge badge-morada">${categoryIcon} Alerta Morada (Demanda)</span>`;
            }

            // Staffing recommendation text formatting
            let staffHtml = '';
            if (alert.recomendacion_personal && alert.recomendacion_personal !== 'N/A') {
                staffHtml += `<div class="recommendation-staff"><i class="fa-solid fa-chart-line"></i> Proyección: ${alert.recomendacion_personal}</div>`;
            }
            if (alert.accion_personal) {
                staffHtml += `<div class="recommendation-staff" style="color: #94A3B8; margin-top: 4px;"><i class="fa-solid fa-user-tag"></i> ${alert.accion_personal}</div>`;
            }

            // Financial impact badge formatting
            let finHtml = '';
            if (alert.detalle_financiero) {
                finHtml = `<div class="financial-badge"><i class="fa-solid fa-arrow-trend-up"></i> ${alert.detalle_financiero}</div>`;
            }

            const savedAmount = alert.ahorro_recuperado_mxn || 0.0;
            const originalLoss = alert.perdida_original_mxn || 0.0;
            const productName = alert.producto || 'Producto';
            const promoText = alert.recomendacion_inventario || 'Oferta especial';

            tr.innerHTML = `
                <td>${badgeHtml}</td>
                <td>
                    <div class="item-title">${alert.titulo}</div>
                    <div class="item-subtext">${alert.descripcion}</div>
                </td>
                <td>
                    <div class="recommendation-inv">${alert.recomendacion_inventario}</div>
                    ${staffHtml}
                    ${finHtml}
                </td>
                <td style="text-align: center;">
                    <button class="btn-action" onclick="approveAction('${alert.id}', '${escapeQuotes(alert.titulo)}', ${savedAmount}, ${originalLoss}, '${escapeQuotes(promoText)}', '${escapeQuotes(productName)}')">
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
    window.approveAction = async function(alertId, alertTitle, savedAmount = 0.0, originalLoss = 0.0, promoText = '', productName = '') {
        const rowElement = document.getElementById(`row-${alertId}`);
        
        if (rowElement) {
            rowElement.classList.add('removing');
        }

        try {
            const response = await fetch('/api/alerts/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    branch: currentBranch, 
                    alert_id: alertId, 
                    saved_amount: savedAmount, 
                    original_loss_amount: originalLoss,
                    promo_text: promoText,
                    producto: productName
                })
            });
            const resData = await response.json();

            if (resData.success) {
                alertsData = resData.alerts;
                executedCount = resData.executed_count;
                totalSavedMxn = resData.total_saved_mxn || 0.0;
                totalOriginalLossMxn = resData.total_original_loss_mxn || 0.0;

                showToast(`Acción ejecutada: +$${savedAmount.toLocaleString('es-MX', {minimumFractionDigits: 2})} MXN rescatados`);

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
                totalSavedMxn = 0.0;
                totalOriginalLossMxn = 0.0;
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

    const closeModalBtn = document.getElementById('closeModalBtn');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            document.getElementById('impactModal').close();
        });
    }

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
