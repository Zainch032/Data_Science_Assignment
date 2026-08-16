/**
 * NexaTel Customer Churn Intelligence Portal — Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Global References ───────────────────────────────────────────────────
    const navTabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    const churnForm = document.getElementById('churn-form');
    const customerLookupSelect = document.getElementById('customer-lookup');
    const btnLoadCustomer = document.getElementById('btn-load-customer');
    
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const resultsActive = document.getElementById('results-active');
    
    const scoreVal = document.getElementById('score-val');
    const gaugeFill = document.getElementById('gauge-fill');
    const riskBadge = document.getElementById('risk-badge');
    const riskSummary = document.getElementById('risk-summary');
    const reasonsList = document.getElementById('reasons-list');
    const actionsList = document.getElementById('actions-list');

    let contractChartInstance = null;
    let internetChartInstance = null;

    // ── 1. Tab Switching Logic ──────────────────────────────────────────────
    navTabs.forEach(btn => {
        btn.addEventListener('click', () => {
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.add('hidden'));

            btn.classList.add('active');
            const targetTabId = btn.getAttribute('data-tab');
            const targetContent = document.getElementById(targetTabId);
            if (targetContent) {
                targetContent.classList.remove('hidden');
            }

            if (targetTabId === 'eda-tab') {
                loadEDAMetrics();
            }
        });
    });

    // ── 2. Populate Customer Lookup Dropdown ────────────────────────────────
    fetchCustomerList();

    async function fetchCustomerList() {
        try {
            const res = await fetch('/api/customers');
            const data = await res.json();
            if (data.status === 'success' && data.customers.length > 0) {
                customerLookupSelect.innerHTML = '<option value="">-- Choose Customer ID --</option>';
                data.customers.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.customer_id;
                    const churnTag = (c.churn === 'Yes' || c.churn == 1) ? ' 🔴 Churned' : ' 🟢 Retained';
                    opt.textContent = `${c.customer_id} (${c.contract}, ${c.tenure}m, $${c.monthly_charges}/mo${churnTag})`;
                    customerLookupSelect.appendChild(opt);
                });
            }
        } catch (err) {
            console.warn('Could not load customer lookup list:', err);
        }
    }

    // ── 3. Load Customer Details on Selection ────────────────────────────────
    btnLoadCustomer.addEventListener('click', loadSelectedCustomer);

    async function loadSelectedCustomer() {
        const customerId = customerLookupSelect.value;
        if (!customerId) {
            alert('Please select a Customer ID from the dropdown first.');
            return;
        }

        btnLoadCustomer.textContent = 'Loading...';
        btnLoadCustomer.disabled = true;

        try {
            const res = await fetch(`/api/customer/${customerId}`);
            const data = await res.json();

            if (data.status === 'success' && data.customer) {
                const c = data.customer;
                // Auto-fill form controls
                setFormVal('gender', c.gender);
                setFormVal('senior_citizen', c.senior_citizen);
                setFormVal('partner', c.partner);
                setFormVal('dependents', c.dependents);
                setFormVal('tenure', c.tenure);
                setFormVal('contract', c.contract);
                setFormVal('monthly_charges', c.monthly_charges);
                setFormVal('total_charges', c.total_charges);
                setFormVal('payment_method', c.payment_method);
                setFormVal('paperless_billing', c.paperless_billing);
                setFormVal('phone_service', c.phone_service);
                setFormVal('multiple_lines', c.multiple_lines);
                setFormVal('internet_service', c.internet_service);
                setFormVal('online_security', c.online_security);
                setFormVal('online_backup', c.online_backup);
                setFormVal('device_protection', c.device_protection);
                setFormVal('tech_support', c.tech_support);
                setFormVal('streaming_tv', c.streaming_tv);
                setFormVal('streaming_movies', c.streaming_movies);

                // Auto-trigger prediction for seamless agent workflow
                churnForm.dispatchEvent(new Event('submit'));
            } else {
                alert(data.message || 'Failed to fetch customer profile.');
            }
        } catch (err) {
            alert('Error connecting to backend server: ' + err.message);
        } finally {
            btnLoadCustomer.textContent = 'Load Profile';
            btnLoadCustomer.disabled = false;
        }
    }

    function setFormVal(name, val) {
        const field = churnForm.querySelector(`[name="${name}"]`);
        if (field) {
            field.value = val;
        }
    }

    // ── 4. Form Submission & Prediction API Call ─────────────────────────────
    churnForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(churnForm);
        const payload = {};
        formData.forEach((value, key) => {
            payload[key] = value;
        });

        // Show loading in results card
        resultsPlaceholder.classList.add('hidden');
        resultsActive.classList.remove('hidden');

        try {
            const res = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (data.status === 'success') {
                renderPredictionResults(data);
            } else {
                alert('Prediction Error: ' + (data.message || 'Unknown error'));
            }
        } catch (err) {
            alert('Error calling predict endpoint: ' + err.message);
        }
    });

    // ── 5. Render Prediction Results & Gauge ────────────────────────────────
    function renderPredictionResults(data) {
        const probPct = data.churn_percentage;
        scoreVal.textContent = probPct.toFixed(1) + '%';

        // Update SVG Gauge Dashoffset (Circumference = 2 * PI * 50 = 314)
        const circumference = 314;
        const offset = circumference - (probPct / 100) * circumference;
        gaugeFill.style.strokeDashoffset = offset;
        gaugeFill.style.stroke = data.risk_color;

        // Risk Level Badge & Summary
        riskBadge.textContent = data.risk_level + ' RISK';
        riskBadge.className = 'risk-badge ' + data.risk_level.toLowerCase();

        if (data.risk_level === 'High') {
            riskSummary.textContent = '🚨 Urgent: High risk of churn. Apply retention playbook immediately.';
        } else if (data.risk_level === 'Medium') {
            riskSummary.textContent = '⚠️ Moderate risk: Proactive engagement recommended to prevent escalation.';
        } else {
            riskSummary.textContent = '🟢 Account Healthy: Low churn probability. Standard service protocol.';
        }

        // Render Top Reasons
        reasonsList.innerHTML = '';
        data.reasons.forEach(r => {
            const card = document.createElement('div');
            card.className = 'reason-card';
            card.innerHTML = `
                <div class="reason-info">
                    <h4>${r.factor}</h4>
                    <p>${r.detail}</p>
                </div>
                <div class="reason-impact">${r.impact}</div>
            `;
            reasonsList.appendChild(card);
        });

        // Render Retention Playbook Actions
        actionsList.innerHTML = '';
        data.actions.forEach(a => {
            const card = document.createElement('div');
            card.className = 'action-card';
            card.innerHTML = `
                <h4>${a.title}</h4>
                <div class="offer">${a.offer}</div>
                <div class="script">${a.script}</div>
            `;
            actionsList.appendChild(card);
        });
    }

    // ── 6. EDA Dashboard Data Loading & Charts ─────────────────────────────
    async function loadEDAMetrics() {
        try {
            const res = await fetch('/api/eda');
            const data = await res.json();

            if (data.status === 'success') {
                const kpis = data.kpis;
                document.getElementById('kpi-total').textContent = kpis.total_customers.toLocaleString();
                document.getElementById('kpi-churn').textContent = kpis.churn_rate + '%';
                document.getElementById('kpi-high-risk').textContent = kpis.high_risk_churn_rate + '%';
                document.getElementById('kpi-recall').textContent = kpis.model_recall + '%';

                renderContractChart(data.contracts);
                renderInternetChart(data.internet_services);
            }
        } catch (err) {
            console.error('Failed to load EDA metrics:', err);
        }
    }

    function renderContractChart(contractsData) {
        const ctx = document.getElementById('contractChart').getContext('2d');
        if (contractChartInstance) contractChartInstance.destroy();

        const labels = contractsData.map(c => c.contract);
        const totalCounts = contractsData.map(c => c.total);
        const churnedCounts = contractsData.map(c => c.churned);

        contractChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total Customers',
                        data: totalCounts,
                        backgroundColor: 'rgba(99, 102, 241, 0.4)',
                        borderColor: '#6366f1',
                        borderWidth: 1
                    },
                    {
                        label: 'Churned Customers',
                        data: churnedCounts,
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderColor: '#ef4444',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8' } }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });
    }

    function renderInternetChart(internetData) {
        const ctx = document.getElementById('internetChart').getContext('2d');
        if (internetChartInstance) internetChartInstance.destroy();

        const labels = internetData.map(i => i.internet_service);
        const churnedCounts = internetData.map(i => i.churned);

        internetChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: churnedCounts,
                    backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#94a3b8' } }
                }
            }
        });
    }
});
