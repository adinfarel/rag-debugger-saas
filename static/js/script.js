/* ============================================
   RAG DEBUGGER PRO — MAIN SCRIPT
   Backend connection protected — DO NOT modify API calls
============================================ */

// ============================================
// NAVBAR: Scroll effect
// ============================================
const navbar = document.getElementById('navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
}

// ============================================
// HAMBURGER MENU (mobile)
// ============================================
const hamburger = document.getElementById('hamburger');
if (hamburger) {
    hamburger.addEventListener('click', () => {
        const links = document.querySelector('.nav-links');
        if (links) links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
    });
}

// ============================================
// MODAL SYSTEM
// ============================================
function showLockedModal(planName, price) {
    const overlay = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const desc = document.getElementById('modal-desc');
    if (!overlay) return;
    if (title) title.textContent = `${planName} Plan Required`;
    if (desc) desc.textContent = `This model requires the ${planName} plan (${price}). Upgrade to unlock Llama 70b, DeepSeek R1, and more.`;
    overlay.classList.add('active');
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.remove('active');
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// ============================================
// PARTICLE / ANTIGRAVITY ANIMATION (Hero only)
// ============================================
const canvas = document.getElementById('particle-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;

    const COLORS = ['#5a9e68', '#8bc99a', '#c8dfc8', '#a8c8a8', '#6db87a'];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() { this.reset(true); }

        reset(initial = false) {
            this.x = Math.random() * canvas.width;
            this.y = initial ? Math.random() * canvas.height : canvas.height + 10;
            this.r = Math.random() * 2.5 + 0.5;
            this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
            this.alpha = Math.random() * 0.4 + 0.1;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = -(Math.random() * 0.5 + 0.2);
            this.drift = (Math.random() - 0.5) * 0.01;
            this.life = 0;
            this.maxLife = Math.random() * 400 + 200;
        }

        update() {
            this.x += this.vx + Math.sin(this.life * 0.02) * 0.3;
            this.y += this.vy;
            this.vx += this.drift;
            this.life++;
            if (this.y < -20 || this.life > this.maxLife) this.reset();
        }

        draw() {
            const progress = this.life / this.maxLife;
            const fade = progress < 0.1 ? progress / 0.1 : progress > 0.8 ? 1 - (progress - 0.8) / 0.2 : 1;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.alpha * fade;
            ctx.fill();
        }
    }

    function initParticles() {
        particles = Array.from({ length: 80 }, () => new Particle());
    }

    function drawMesh() {
        ctx.globalAlpha = 0.06;
        ctx.strokeStyle = '#5a9e68';
        ctx.lineWidth = 0.8;
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawMesh();
        particles.forEach(p => { p.update(); p.draw(); });
        ctx.globalAlpha = 1;
        animationId = requestAnimationFrame(animate);
    }

    resize();
    initParticles();
    animate();
    window.addEventListener('resize', () => { resize(); }, { passive: true });
}

// ============================================
// MODEL SELECTOR (Tool Page)
// ============================================
const modelPills = document.querySelectorAll('.model-pill:not(.locked)');
modelPills.forEach(pill => {
    pill.addEventListener('click', () => {
        document.querySelectorAll('.model-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');

        const tier = pill.dataset.tier;
        const model = pill.dataset.model;

        const tierInput = document.getElementById('tier');
        if (tierInput) tierInput.value = tier;

        const modelDisplay = document.getElementById('active-model-name');
        if (modelDisplay) modelDisplay.textContent = model;
    });
});

// ============================================
// LOADING STEPS ANIMATION
// ============================================
let stepTimers = [];

function startLoadingSteps() {
    const steps = ['step-retrieval', 'step-eval', 'step-suggest'];
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
    });

    let delay = 0;
    steps.forEach((id, i) => {
        const timer = setTimeout(() => {
            steps.forEach(s => {
                const el = document.getElementById(s);
                if (el) el.classList.remove('active');
            });
            const current = document.getElementById(id);
            if (current) current.classList.add('active');
        }, delay);
        stepTimers.push(timer);
        delay += 2500;
    });
}

function stopLoadingSteps() {
    stepTimers.forEach(t => clearTimeout(t));
    stepTimers = [];
}

// ============================================
// INTEGRITY GAUGE ANIMATION
// ============================================
function animateGauge(percent) {
    const arc = document.getElementById('gauge-arc');
    const pctText = document.getElementById('gauge-pct');
    if (!arc || !pctText) return;

    const totalLength = 251.2; // half circle arc length
    const targetOffset = totalLength - (totalLength * percent / 100);

    // Color based on pass/fail
    arc.style.stroke = percent >= 50 ? '#5a9e68' : '#ef4444';

    let current = 0;
    const step = percent / 40;
    const timer = setInterval(() => {
        current = Math.min(current + step, percent);
        const offset = totalLength - (totalLength * current / 100);
        arc.setAttribute('stroke-dashoffset', offset);
        pctText.textContent = Math.round(current) + '%';
        if (current >= percent) clearInterval(timer);
    }, 20);
}

// ============================================
// MAIN EVALUATION FUNCTION (Backend Protected)
// ============================================
async function runEvaluation() {
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoading = document.getElementById('btn-loading');
    const loadingStatus = document.getElementById('loading-status');
    const resultSection = document.getElementById('result-section');
    const resultEmpty = document.getElementById('result-empty');

    // Validate inputs
    const query = document.getElementById('query')?.value?.trim();
    const retrieved_context = document.getElementById('retrieved_context')?.value?.trim();
    const model_answer = document.getElementById('model_answer')?.value?.trim();
    const tier = document.getElementById('tier')?.value || 'free';

    if (!query || !retrieved_context || !model_answer) {
        alert('Please fill in all three fields before running evaluation.');
        return;
    }

    // UI: Start loading state
    submitBtn.disabled = true;
    btnText.classList.add('hidden');
    btnLoading.classList.remove('hidden');
    loadingStatus.classList.remove('hidden');
    resultSection.classList.add('hidden');
    if (resultEmpty) resultEmpty.classList.add('hidden');

    startLoadingSteps();

    // Build request payload — PROTECTED: DO NOT CHANGE SCHEMA
    const requestData = {
        tier,
        query,
        retrieved_context,
        model_answer
    };

    try {
        // PROTECTED: DO NOT CHANGE ENDPOINT
        const response = await fetch('http://localhost:8000/api/v1/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        // Render results
        renderResults(data);

    } catch (error) {
        alert('Failed to connect to API. Make sure uvicorn is running on port 8000.');
        console.error('[RAGDebugger] API Error:', error);
        if (resultEmpty) resultEmpty.classList.remove('hidden');
    } finally {
        // UI: Stop loading state
        stopLoadingSteps();
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
        loadingStatus.classList.add('hidden');
    }
}

// ============================================
// RESULT RENDERER
// ============================================
function renderResults(data) {
    const resultSection = document.getElementById('result-section');
    const resultEmpty = document.getElementById('result-empty');

    const outStatusBadge = document.getElementById('out-status-badge');
    const contextFailureAlert = document.getElementById('context-failure-alert');
    const claimsSection = document.getElementById('claims-section');
    const outClaims = document.getElementById('out-claims');
    const suggestionsSection = document.getElementById('suggestions-section');
    const outSuggestions = document.getElementById('out-suggestions');

    // Clear previous
    if (outClaims) outClaims.innerHTML = '';
    if (outSuggestions) outSuggestions.innerHTML = '';

    const status = data.evaluation_status || 'UNKNOWN';
    const isBadContext = status === 'FAIL_BAD_CONTEXT';
    const isPass = status === 'PASS';

    // Status Badge
    if (outStatusBadge) {
        outStatusBadge.textContent = status;
        outStatusBadge.className = 'status-badge' + (!isPass ? ' fail' : '');
    }

    // CRITICAL REMOVAL: No hallucination score shown.
    // Gauge shows Pipeline Integrity instead.
    const integrityPct = isPass ? 100 : 0;
    animateGauge(integrityPct);

    // CRITICAL LOGIC: Context Failure vs Normal
    if (isBadContext) {
        // Show context failure alert, hide claims
        if (contextFailureAlert) contextFailureAlert.classList.remove('hidden');
        if (claimsSection) claimsSection.classList.add('hidden');
    } else {
        // Hide alert, show claims
        if (contextFailureAlert) contextFailureAlert.classList.add('hidden');

        // Render claims
        const claims = data.unsupported_claims || [];
        if (claimsSection) claimsSection.classList.remove('hidden');

        if (claims.length > 0) {
            claims.forEach(claim => {
                const div = document.createElement('div');
                div.className = 'claim-card fade-in';
                div.innerHTML = `
                    <p><strong>Claim:</strong> ${escapeHtml(claim.claim)}</p>
                    <p><strong>Supported:</strong> <span class="${claim.is_supported ? 'claim-supported' : 'claim-unsupported'}">${claim.is_supported ? '✅ Yes' : '❌ No'}</span></p>
                    <p><strong>Reason:</strong> ${escapeHtml(claim.reason)}</p>
                `;
                if (outClaims) outClaims.appendChild(div);
            });
        } else {
            if (outClaims) outClaims.innerHTML = '<div class="claim-card"><p>✅ All claims supported or no specific claims extracted.</p></div>';
        }
    }

    // Render Suggestions (always shown)
    const suggestions = data.suggestions || [];
    if (suggestionsSection) suggestionsSection.classList.remove('hidden');

    if (suggestions.length > 0) {
        suggestions.forEach((s, i) => {
            const li = document.createElement('li');
            li.className = 'fade-in';
            li.style.animationDelay = `${i * 80}ms`;
            li.textContent = s;
            if (outSuggestions) outSuggestions.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No suggestions needed. Pipeline looks clean.';
        if (outSuggestions) outSuggestions.appendChild(li);
    }

    // Show results
    if (resultEmpty) resultEmpty.classList.add('hidden');
    if (resultSection) {
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ============================================
// SECURITY: XSS prevention
// ============================================
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ============================================
// ENTER KEY SHORTCUT (Tool Page)
// ============================================
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        const btn = document.getElementById('submit-btn');
        if (btn && !btn.disabled) runEvaluation();
    }
});
