// Helper to update clock
function updateClock() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}
setInterval(updateClock, 1000);
updateClock();

// Helper to format UTC ISO timestamps into Indian Standard Time (IST)
function formatTimestampIST(isoStr) {
    if (!isoStr) return '';
    try {
        const dateObj = new Date(isoStr);
        const datePart = dateObj.toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' });
        const timePart = dateObj.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        return `${datePart} | ${timePart} (IST)`;
    } catch (e) {
        return isoStr.replace('T', ' ').substring(0, 19);
    }
}

// ── Toast Notification System (replaces all alert() calls) ──────────────────
const TOAST_ICONS = {
    error:   '<i class="fa-solid fa-circle-xmark text-red-400 text-base mt-0.5"></i>',
    success: '<i class="fa-solid fa-circle-check text-green-400 text-base mt-0.5"></i>',
    info:    '<i class="fa-solid fa-circle-info text-blue-400 text-base mt-0.5"></i>',
    warning: '<i class="fa-solid fa-triangle-exclamation text-amber-400 text-base mt-0.5"></i>'
};
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) { console.warn(message); return; }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `${TOAST_ICONS[type] || TOAST_ICONS.info}<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('toast-out');
        toast.addEventListener('animationend', () => toast.remove(), { once: true });
    }, duration);
}

// ── Dynamic Session ID — unique per browser tab, persisted across page loads ─
const SESSION_ID = (() => {
    const key = 'advisor_ai_session_id';
    let sid = sessionStorage.getItem(key);
    if (!sid) {
        sid = 'session-' + (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).substring(2));
        sessionStorage.setItem(key, sid);
    }
    return sid;
})();


// Mobile Sidebar Toggle Logic
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const closeSidebarBtn = document.getElementById('close-sidebar-btn');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');

function toggleSidebar() {
    if (sidebar) sidebar.classList.toggle('-translate-x-full');
    if (sidebarOverlay) sidebarOverlay.classList.toggle('hidden');
}

if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebar);
if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', toggleSidebar);
if (sidebarOverlay) sidebarOverlay.addEventListener('click', toggleSidebar);


// Navigation Logic
const navItems = document.querySelectorAll('.nav-item');
const featureSections = document.querySelectorAll('.feature-section');
const headerTitle = document.getElementById('header-title');
const headerSubtitle = document.getElementById('header-subtitle');

const sectionData = {
    'feature-dashboard': { title: 'Executive Dashboard', subtitle: 'Overview of your book of business, AI insights, and compliance health.' },
    'feature-chat': { title: 'Portfolio Chat', subtitle: 'Ask anything about your client portfolios in natural language.' },
    'feature-rag': { title: 'Research Search', subtitle: 'Search across 5 financial research reports using natural language.' },
    'feature-client360': { title: 'Client 360 — Meeting Prep', subtitle: 'Generate a complete meeting preparation brief for any client instantly.' },
    'feature-compliance': { title: 'Compliance Monitor', subtitle: 'Real-time compliance checks across all client portfolios with CloudWatch audit logging.' },
    'feature-observability': { title: 'AI Observability Console', subtitle: 'Real-time AWS Bedrock token usage, latency, and cost tracking.' },
    'feature-supervision': { title: 'Supervision Queue', subtitle: 'Human-in-the-loop review for high-risk AI recommendations.' },
    'feature-simulator': { title: 'Portfolio Scenario Simulator', subtitle: 'Run what-if analysis on client portfolios to simulate market scenarios.' },
    'feature-revenue': { title: 'Revenue Enablement', subtitle: 'AI-ranked cross-sell and upsell opportunities personalised to each client.' }
};

navItems.forEach(item => {
    item.addEventListener('click', () => {
        // Remove active class
        navItems.forEach(n => n.classList.remove('active'));
        featureSections.forEach(s => s.classList.remove('active'));
        
        // Add active class
        item.classList.add('active');
        const targetId = item.getAttribute('data-target');
        document.getElementById(targetId).classList.add('active');
        
        // Update Header
        headerTitle.textContent = sectionData[targetId].title;
        headerSubtitle.textContent = sectionData[targetId].subtitle;
        
        // Close sidebar on mobile
        if (window.innerWidth < 768 && sidebar && !sidebar.classList.contains('-translate-x-full')) {
            toggleSidebar();
        }
    });
});

// Configure Marked.js for safe markdown rendering
if (typeof marked !== 'undefined') {
    marked.setOptions({
        gfm: true,
        breaks: true
    });
}

// -----------------------------------------------------------
// FEATURE 1: Portfolio Chat
// -----------------------------------------------------------
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');
const chatSubmit = document.getElementById('chat-submit');
const micBtn = document.getElementById('mic-btn');
const voiceToggle = document.getElementById('voice-toggle');

// Voice Recognition Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('text-red-500', 'listening-pulse');
        chatInput.placeholder = "Listening...";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        chatForm.dispatchEvent(new Event('submit'));
    };

    recognition.onend = () => {
        isListening = false;
        micBtn.classList.remove('text-red-500', 'listening-pulse');
        chatInput.placeholder = "Ask about portfolios... e.g. 'What are Rahul's top risks?'";
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        recognition.stop();
    };
}

micBtn.addEventListener('click', () => {
    if (!recognition) {
        showToast("Speech recognition not supported in this browser.", 'warning');
        return;
    }
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

// Voice toggle change listener to instantly stop speaking if turned off
if (voiceToggle) {
    voiceToggle.addEventListener('change', () => {
        if (!voiceToggle.checked && window.speechSynthesis) {
            window.speechSynthesis.cancel();
            const stopBtn = document.getElementById('stop-speech-btn');
            if (stopBtn) stopBtn.classList.add('hidden');
        }
    });
}

// Text-to-Speech Helper
function speakResponse(text) {
    if (!voiceToggle.checked || !window.speechSynthesis) return;
    
    // Stop any current speaking
    window.speechSynthesis.cancel();
    
    // Clean text for better speaking (remove markdown)
    const cleanText = text.replace(/[#*`_]/g, '').replace(/\[.*?\]/g, '').trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Find a professional-sounding voice if possible
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha'));
    if (preferredVoice) utterance.voice = preferredVoice;

    const stopBtn = document.getElementById('stop-speech-btn');
    if (stopBtn) {
        utterance.onstart = () => stopBtn.classList.remove('hidden');
        utterance.onend = () => stopBtn.classList.add('hidden');
        utterance.onerror = () => stopBtn.classList.add('hidden');
    }

    window.speechSynthesis.speak(utterance);
}

function fillChat(query) {
    chatInput.value = query;
    chatForm.dispatchEvent(new Event('submit'));
}

function clearChat() {
    chatHistory.innerHTML = `
        <div class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-robot text-xs"></i></div>
            <div class="msg-ai p-4 rounded-2xl text-sm ai-content shadow-sm text-gray-200">
                Chat cleared. How can I help you analyze your client portfolios today?
            </div>
        </div>
    `;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Add user message
    chatHistory.innerHTML += `
        <div class="flex items-start gap-4 flex-row-reverse">
            <div class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-user text-xs"></i></div>
            <div class="msg-user p-4 rounded-2xl text-sm shadow-sm text-white max-w-[80%]">
                ${query}
            </div>
        </div>
    `;
    chatInput.value = '';
    chatSubmit.disabled = true;

    // Add typing indicator
    const typingId = 'typing-' + Date.now();
    chatHistory.innerHTML += `
        <div id="${typingId}" class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-robot text-xs"></i></div>
            <div class="msg-ai p-4 rounded-2xl flex items-center gap-1 shadow-sm">
                <div class="w-2 h-2 rounded-full bg-blue-400 typing-dot"></div>
                <div class="w-2 h-2 rounded-full bg-blue-400 typing-dot"></div>
                <div class="w-2 h-2 rounded-full bg-blue-400 typing-dot"></div>
            </div>
        </div>
    `;
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: query, session_id: SESSION_ID })
        });
        
        const data = await response.json();
        document.getElementById(typingId).remove();

        if (response.ok) {
            const htmlAnswer = marked.parse(data.answer);
            chatHistory.innerHTML += `
                <div class="flex items-start gap-4">
                    <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-robot text-xs"></i></div>
                    <div class="msg-ai p-4 rounded-2xl text-sm ai-content shadow-sm text-gray-200 w-full overflow-hidden">
                        ${htmlAnswer}
                    </div>
                </div>
            `;
            // Trigger Voice Response if enabled
            speakResponse(data.answer);
        } else {
            chatHistory.innerHTML += `<div class="text-red-400 text-sm mt-2 text-center">Error: ${data.detail || 'Connection failed'}</div>`;
        }
    } catch (err) {
        document.getElementById(typingId)?.remove();
        chatHistory.innerHTML += `<div class="text-red-400 text-sm mt-2 text-center">Error: ${err.message}</div>`;
    }

    chatSubmit.disabled = false;
    chatHistory.scrollTop = chatHistory.scrollHeight;
});

// -----------------------------------------------------------
// FEATURE 2: Research Search (RAG)
// -----------------------------------------------------------
const ragForm = document.getElementById('rag-form');
const ragInput = document.getElementById('rag-input');
const ragResultsContainer = document.getElementById('rag-results-container');
const ragLoader = document.getElementById('rag-loader');
const ragAnswer = document.getElementById('rag-answer');
const ragSources = document.getElementById('rag-sources');

function fillRag(query) {
    ragInput.value = query;
    ragForm.dispatchEvent(new Event('submit'));
}

ragForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = ragInput.value.trim();
    if (!query) return;

    ragResultsContainer.classList.add('hidden');
    ragLoader.classList.remove('hidden');

    try {
        const response = await fetch('/api/rag', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: query })
        });
        
        const data = await response.json();
        ragLoader.classList.add('hidden');

        if (response.ok) {
            ragResultsContainer.classList.remove('hidden');
            ragAnswer.innerHTML = marked.parse(data.answer);
            
            ragSources.innerHTML = '';
            if (data.sources && data.sources.length > 0) {
                data.sources.forEach(src => {
                    ragSources.innerHTML += `<li class="text-sm bg-gray-800/50 px-3 py-2 rounded border border-gray-700/50 flex items-center gap-2"><i class="fa-solid fa-file-pdf text-red-400"></i> ${src}</li>`;
                });
            } else {
                ragSources.innerHTML = '<li class="text-sm text-gray-500">No specific sources cited.</li>';
            }
        } else {
            showToast(`Research error: ${data.detail}`, 'error');
            ragResultsContainer.classList.add('hidden');
        }
    } catch (err) {
        ragLoader.classList.add('hidden');
        showToast(`Research error: ${err.message}`, 'error');
    }
});

// -----------------------------------------------------------
// FEATURE 3: Client 360
// -----------------------------------------------------------
async function generateBrief(clientName) {
    if (!clientName) return;
    
    document.getElementById('brief-content').classList.add('hidden');
    document.getElementById('brief-loader').classList.remove('hidden');
    
    try {
        const response = await fetch('/api/client360', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ client_name: clientName })
        });
        
        const data = await response.json();
        document.getElementById('brief-loader').classList.add('hidden');

        if (response.ok) {
            document.getElementById('brief-content').classList.remove('hidden');
            
            // Populate Header metrics
            document.getElementById('b-name').textContent = data.client_name;
            document.getElementById('b-aum').textContent = '$' + data.aum.toLocaleString();
            document.getElementById('b-risk').textContent = data.risk_profile;
            document.getElementById('b-meeting').textContent = data.meeting_time;
            
            // Populate flags
            const flagsContainer = document.getElementById('b-flags-container');
            if (data.compliance_flags && data.compliance_flags.length > 0) {
                flagsContainer.classList.remove('hidden');
                flagsContainer.innerHTML = '';
                data.compliance_flags.forEach(flag => {
                    flagsContainer.innerHTML += `
                        <div class="alert-high p-3 rounded-lg flex items-start gap-3 mb-2">
                            <i class="fa-solid fa-triangle-exclamation text-red-500 mt-0.5"></i>
                            <div>
                                <strong class="text-red-500 text-sm">COMPLIANCE ALERT</strong>
                                <p class="text-red-200 text-sm">${flag}</p>
                            </div>
                        </div>
                    `;
                });
            } else {
                flagsContainer.classList.remove('hidden');
                flagsContainer.innerHTML = `
                    <div class="alert-low p-3 rounded-lg flex items-center gap-3">
                        <i class="fa-solid fa-check text-green-500"></i>
                        <span class="text-green-200 text-sm font-medium">No compliance flags</span>
                    </div>
                `;
            }
            
            // Populate Brief content
            document.getElementById('b-text').innerHTML = marked.parse(data.brief);
            
        } else {
            showToast(`Error: ${data.detail || 'Client not found'}`, 'error');
        }
    } catch (err) {
        document.getElementById('brief-loader').classList.add('hidden');
        showToast(`Error: ${err.message}`, 'error');
    }
}

// -----------------------------------------------------------
// FEATURE 4: Compliance Monitor
// -----------------------------------------------------------
async function runComplianceCheck(clientFilter = '') {
    const resultsContainer = document.getElementById('comp-results');
    const loader = document.getElementById('comp-loader');
    
    resultsContainer.classList.add('hidden');
    loader.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/compliance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ client_filter: clientFilter || null })
        });
        
        const data = await response.json();
        loader.classList.add('hidden');
        
        if (response.ok) {
            resultsContainer.classList.remove('hidden');
            resultsContainer.classList.add('flex');
            
            // Update Summary
            document.getElementById('c-total').textContent = data.summary.total_clients_checked;
            document.getElementById('c-violations').textContent = data.summary.total_violations;
            document.getElementById('c-high').textContent = data.summary.high_severity_count;
            document.getElementById('c-time').textContent = formatTimestampIST(data.summary.checked_at);
            
            // Build Client Cards
            const list = document.getElementById('c-list');
            list.innerHTML = '';
            
            data.results.forEach(res => {
                let badgeClass = 'bg-green-500/20 text-green-400 border-green-500/30';
                let icon = '<i class="fa-solid fa-circle-check"></i>';
                
                if (res.status === 'ALERT') {
                    badgeClass = 'bg-red-500/20 text-red-400 border-red-500/30';
                    icon = '<i class="fa-solid fa-triangle-exclamation"></i>';
                } else if (res.status === 'WARNING') {
                    badgeClass = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
                    icon = '<i class="fa-solid fa-circle-exclamation"></i>';
                }
                
                let violationsHtml = '';
                if (res.violations && res.violations.length > 0) {
                    violationsHtml = '<div class="mt-4 space-y-3">';
                    res.violations.forEach(v => {
                        let vClass = v.severity === 'HIGH' ? 'alert-high' : (v.severity === 'MEDIUM' ? 'alert-medium' : 'alert-low');
                        let vIcon = v.severity === 'HIGH' ? 'fa-solid fa-bomb text-red-500' : 'fa-solid fa-bolt text-amber-500';
                        violationsHtml += `
                            <div class="${vClass} p-4 rounded-xl">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="${vIcon}"></i>
                                    <span class="font-bold text-sm tracking-wide">[${v.severity}] ${v.rule_name}</span>
                                </div>
                                <p class="text-sm text-gray-300 mb-2">${v.description}</p>
                                <div class="bg-black/20 px-3 py-2 rounded text-xs font-mono text-gray-400">
                                    <span class="text-white font-bold">Action:</span> ${v.action}
                                </div>
                            </div>
                        `;
                    });
                    violationsHtml += '</div>';
                } else {
                    violationsHtml = `
                        <div class="mt-4 alert-low p-3 rounded-lg flex items-center gap-3">
                            <i class="fa-solid fa-check text-green-500"></i>
                            <span class="text-green-200 text-sm">No compliance violations found for this client.</span>
                        </div>
                    `;
                }
                
                const cardHtml = `
                    <div class="bg-gray-800/40 border border-gray-700/50 rounded-xl p-5 mb-4 hover:border-gray-600 transition-colors">
                        <div class="flex justify-between items-center mb-2">
                            <h4 class="font-bold text-lg text-white flex items-center gap-2">
                                <i class="fa-solid fa-user-tie text-blue-400"></i>
                                ${res.client_name}
                            </h4>
                            <span class="px-3 py-1 rounded-full border text-xs font-bold flex items-center gap-2 ${badgeClass}">
                                ${icon} ${res.status}
                            </span>
                        </div>
                        <div class="flex gap-4 text-sm text-gray-400 mb-2">
                            <span><i class="fa-solid fa-chart-pie mr-1"></i> Risk: <span class="text-gray-200">${res.risk_profile}</span></span>
                            <span><i class="fa-solid fa-sack-dollar mr-1"></i> AUM: <span class="text-gray-200">$${res.aum.toLocaleString()}</span></span>
                            <span><i class="fa-solid fa-bug mr-1"></i> Violations: <span class="text-gray-200">${res.violation_count}</span></span>
                        </div>
                        ${violationsHtml}
                    </div>
                `;
                list.innerHTML += cardHtml;
            });
            
        } else {
            showToast(`Compliance error: ${data.detail}`, 'error');
        }
    } catch (err) {
        loader.classList.add('hidden');
        showToast(`Compliance error: ${err.message}`, 'error');
    }
}

// -----------------------------------------------------------
// System Status Checker
// -----------------------------------------------------------
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update API Gateway
        const apigwDot = document.getElementById('status-apigw');
        if (data.api_gateway === 'active') {
            apigwDot.classList.remove('bg-gray-600', 'bg-red-500');
            apigwDot.classList.add('bg-green-500');
        } else {
            apigwDot.classList.remove('bg-gray-600', 'bg-green-500');
            apigwDot.classList.add('bg-red-500');
        }
        
        // Update Bedrock (tied to API GW)
        const bedrockDot = document.getElementById('status-bedrock');
        if (data.bedrock === 'active') {
            bedrockDot.classList.remove('bg-gray-600', 'bg-red-500');
            bedrockDot.classList.add('bg-green-500');
        } else {
            bedrockDot.classList.remove('bg-gray-600', 'bg-green-500');
            bedrockDot.classList.add('bg-red-500');
        }
        
        // Update EC2
        const ec2Dot = document.getElementById('status-ec2');
        if (data.ec2_rag === 'active') {
            ec2Dot.classList.remove('bg-gray-600', 'bg-red-500');
            ec2Dot.classList.add('bg-green-500');
        } else {
            ec2Dot.classList.remove('bg-gray-600', 'bg-green-500');
            ec2Dot.classList.add('bg-red-500');
        }
        
    } catch (err) {
        console.error("Failed to fetch system status", err);
    }
}

// Helper to render dashboard insights
function renderDashboard(data) {
    const insightsContainer = document.getElementById('dash-insights');
    if (data.insights && data.insights.length > 0) {
        insightsContainer.innerHTML = '';
        data.insights.forEach(insight => {
            const icon = insight.type === 'warning' ? 'fa-triangle-exclamation' : (insight.type === 'success' ? 'fa-circle-check' : 'fa-circle-info');
            const color = insight.type === 'warning' ? 'text-amber-400' : (insight.type === 'success' ? 'text-green-400' : 'text-blue-400');
            const bg = insight.type === 'warning' ? 'bg-amber-500/10' : (insight.type === 'success' ? 'bg-green-500/10' : 'bg-blue-500/10');
            const border = insight.type === 'warning' ? 'border-amber-500/20' : (insight.type === 'success' ? 'border-green-500/20' : 'border-blue-500/20');
            
            insightsContainer.innerHTML += `
                <div class="glass p-5 rounded-2xl flex items-start gap-4 transition-all hover:scale-[1.01] ${bg} ${border} border">
                    <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${bg}">
                        <i class="fa-solid ${icon} ${color}"></i>
                    </div>
                    <div class="flex-1">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] font-bold uppercase tracking-widest ${color}">${insight.client}</span>
                            <span class="text-[8px] bg-white/5 px-1.5 py-0.5 rounded text-gray-500 uppercase">AI Insight</span>
                        </div>
                        <p class="text-sm text-gray-200">${insight.text}</p>
                    </div>
                </div>
            `;
        });
    }
}

async function loadDashboard() {
    const insightsContainer = document.getElementById('dash-insights');
    
    // Check localStorage cache (6 hours = 21,600,000 ms)
    const cacheKey = 'dash_insights_cache';
    const cacheDuration = 21600000;
    const cachedData = localStorage.getItem(cacheKey);
    
    if (cachedData) {
        try {
            const cache = JSON.parse(cachedData);
            if (Date.now() - cache.timestamp < cacheDuration) {
                renderDashboard(cache.data);
                return;
            }
        } catch (e) {
            localStorage.removeItem(cacheKey);
        }
    }
    
    try {
        const response = await fetch('/api/dashboard');
        
        // ONLY proceed to cache and render if the HTTP status is 200 (OK)
        if (response.ok) {
            const data = await response.json();
            
            // Validate that we got a successful structure containing insights
            if (data && data.insights && data.insights.length > 0) {
                localStorage.setItem(cacheKey, JSON.stringify({
                    data: data,
                    timestamp: Date.now()
                }));
            }
            
            renderDashboard(data);
        } else {
            throw new Error(`HTTP status ${response.status}`);
        }
    } catch (err) {
        console.error("Dashboard error:", err);
        insightsContainer.innerHTML = '<p class="text-gray-500 text-sm">Failed to load proactive insights.</p>';
    }
}

async function loadMarketData() {
    const contentContainer = document.getElementById('market-ticker-content');
    const timeContainer = document.getElementById('market-ticker-time');
    try {
        const response = await fetch('/api/market');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data && data.indices) {
            contentContainer.innerHTML = '';
            let hasValidData = false;
            data.indices.forEach(index => {
                if (index.price !== null) {
                    hasValidData = true;
                    const changeVal = index.change_pct;
                    const sign = changeVal >= 0 ? '+' : '';
                    const isUp = changeVal >= 0;
                    const colorClass = isUp ? 'text-emerald-400' : 'text-rose-400';
                    const iconClass = isUp ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';
                    const bgClass = isUp ? 'bg-emerald-500/10' : 'bg-rose-500/10';
                    const borderClass = isUp ? 'border-emerald-500/10' : 'border-rose-500/10';
                    
                    contentContainer.innerHTML += `
                        <div class="flex items-center gap-2 bg-slate-900/40 px-3 py-1.5 rounded-xl border border-white/5 transition-all hover:scale-[1.02]">
                            <span class="text-xs font-bold text-gray-300">${index.name}</span>
                            <span class="text-xs font-semibold text-white font-mono">${index.price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                            <span class="flex items-center gap-1 text-[10px] font-bold ${colorClass} ${bgClass} px-1.5 py-0.5 rounded border ${borderClass}">
                                <i class="fa-solid ${iconClass}"></i> ${sign}${changeVal.toFixed(2)}%
                            </span>
                        </div>
                    `;
                    timeContainer.textContent = index.fetched_at;
                } else {
                    contentContainer.innerHTML += `
                        <div class="flex items-center gap-2 bg-slate-900/40 px-3 py-1.5 rounded-xl border border-white/5 opacity-50">
                            <span class="text-xs font-bold text-gray-400">${index.name}</span>
                            <span class="text-xs font-semibold text-gray-500 font-mono">Offline</span>
                        </div>
                    `;
                }
            });
            if (!hasValidData) {
                contentContainer.innerHTML = '<span class="text-xs text-gray-500">Live feed temporarily paused.</span>';
            }
        }
    } catch (err) {
        console.error("Market data error:", err);
        contentContainer.innerHTML = `
            <span class="text-xs text-rose-400 flex items-center gap-1.5">
                <i class="fa-solid fa-triangle-exclamation"></i> Live feed connection error
            </span>
        `;
    }
}

// Fetch and render proactive life-event alerts
async function loadLifeEvents() {
    const section = document.getElementById('life-events-alerts-section');
    const container = document.getElementById('life-events-alerts-container');
    if (!section || !container) return;

    try {
        const response = await fetch('/api/life-events');
        if (!response.ok) throw new Error("HTTP error " + response.status);
        const data = await response.json();
        
        if (data.events && data.events.length > 0) {
            section.classList.remove('hidden');
            container.innerHTML = '';
            
            data.events.forEach(alert => {
                let borderClass = 'border-blue-500/20 bg-blue-500/5 text-blue-400';
                let iconClass = 'fa-circle-info text-blue-400';
                let titleColor = 'text-blue-400';
                let pulseRing = '';
                
                if (alert.severity === 'danger') {
                    borderClass = 'border-red-500/30 bg-red-500/5 text-red-400';
                    iconClass = 'fa-circle-exclamation text-red-400';
                    titleColor = 'text-red-400';
                    pulseRing = '<span class="absolute top-1 right-1 flex h-2 w-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span></span>';
                } else if (alert.severity === 'warning') {
                    borderClass = 'border-amber-500/30 bg-amber-500/5 text-amber-400';
                    iconClass = 'fa-triangle-exclamation text-amber-400';
                    titleColor = 'text-amber-400';
                }
                
                container.innerHTML += `
                    <div class="glass p-5 rounded-2xl border ${borderClass} transition-all hover:scale-[1.01] relative overflow-hidden">
                        ${pulseRing}
                        <div class="flex items-start gap-4">
                            <div class="w-10 h-10 rounded-xl flex items-center justify-center bg-white/5 flex-shrink-0">
                                <i class="fa-solid ${iconClass} text-base"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <div class="flex justify-between items-center mb-1.5 gap-2">
                                    <span class="text-[10px] font-bold uppercase tracking-widest ${titleColor} truncate">${alert.client_name}</span>
                                    <span class="text-[8px] bg-white/5 px-2 py-0.5 rounded text-gray-400 font-mono flex-shrink-0 uppercase">${alert.category}</span>
                                </div>
                                <h4 class="text-sm font-semibold text-white mb-1.5 leading-snug">${alert.event}</h4>
                                <p class="text-[11px] text-gray-300 leading-relaxed"><strong class="${titleColor}">Action:</strong> ${alert.action}</p>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            section.classList.add('hidden');
        }
    } catch (err) {
        console.error("Failed to load life-event alerts:", err);
        section.classList.add('hidden');
    }
}

// Check status on load and every 30 seconds
checkSystemStatus();
loadDashboard();
loadMarketData();
loadLifeEvents();
setInterval(checkSystemStatus, 30000);
setInterval(loadDashboard, 21600000); // Refresh dashboard every 6 hours (cost control)
setInterval(loadMarketData, 300000); // Refresh market ticker every 5 minutes

// -----------------------------------------------------------
// FEATURE 5: AI Observability
// -----------------------------------------------------------
async function loadObservability() {
    const loader = document.getElementById('obs-loader');
    const results = document.getElementById('obs-results');

    results.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const response = await fetch('/api/observability');
        const data = await response.json();
        loader.classList.add('hidden');

        if (response.ok) {
            results.classList.remove('hidden');
            results.classList.add('flex');

            // Summary
            const s = data.summary;
            document.getElementById('obs-calls').textContent = s.total_calls;
            document.getElementById('obs-tokens').textContent = s.total_tokens.toLocaleString();
            document.getElementById('obs-cost').textContent = '$' + s.total_cost_usd.toFixed(6);
            document.getElementById('obs-cost-inr').textContent = '₹' + s.total_cost_inr.toFixed(4);
            document.getElementById('obs-latency').textContent = s.avg_latency_ms + 'ms';
            document.getElementById('obs-model').textContent = s.model_id;

            // By feature
            const featDiv = document.getElementById('obs-features');
            featDiv.innerHTML = '';
            const colors = {
                'portfolio_chat': 'blue',
                'client360_brief': 'purple',
                'compliance_check': 'red'
            };
            Object.entries(data.by_feature).forEach(([feat, stats]) => {
                const color = colors[feat] || 'gray';
                featDiv.innerHTML += `
                    <div class="flex items-center gap-4 p-3 rounded-lg bg-gray-800/40">
                        <div class="w-3 h-3 rounded-full bg-${color}-400 flex-shrink-0"></div>
                        <div class="flex-1">
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-sm font-medium text-gray-200">${feat.replace('_', ' ').toUpperCase()}</span>
                                <span class="text-xs text-gray-400">${stats.calls} calls</span>
                            </div>
                            <div class="w-full bg-gray-700 rounded-full h-1.5">
                                <div class="bg-${color}-400 h-1.5 rounded-full" style="width: ${Math.min((stats.calls / data.summary.total_calls) * 100, 100)}%"></div>
                            </div>
                        </div>
                        <div class="text-right text-xs text-gray-400">
                            <div>${stats.tokens.toLocaleString()} tokens</div>
                            <div class="text-green-400">$${stats.cost.toFixed(6)}</div>
                        </div>
                    </div>
                `;
            });

            // Recent calls
            const tbody = document.getElementById('obs-recent');
            tbody.innerHTML = '';
            data.recent_calls.forEach(call => {
                const feat = call.feature || 'unknown';
                const badge = feat === 'portfolio_chat' ? 'bg-blue-500/20 text-blue-300' :
                              feat === 'client360_brief' ? 'bg-purple-500/20 text-purple-300' :
                              'bg-gray-500/20 text-gray-300';
                tbody.innerHTML += `
                    <tr class="border-b border-gray-800 hover:bg-gray-800/30">
                        <td class="py-2 pr-4">
                            <span class="px-2 py-0.5 rounded text-xs font-medium ${badge}">
                                ${feat.replace('_', ' ')}
                            </span>
                        </td>
                        <td class="py-2 pr-4 text-gray-300">${(call.tokens || 0).toLocaleString()}</td>
                        <td class="py-2 pr-4 text-amber-400">${call.latency_ms || 0}ms</td>
                        <td class="py-2 pr-4 text-green-400">$${parseFloat(call.cost_usd || 0).toFixed(6)}</td>
                        <td class="py-2 text-gray-500 text-xs">${formatTimestampIST(call.timestamp)}</td>
                    </tr>
                `;
            });
        }
    } catch (err) {
        loader.classList.add('hidden');
        showToast('Observability error: ' + err.message, 'error');
    }
}

// -----------------------------------------------------------
// FEATURE 6: Supervision Queue
// -----------------------------------------------------------
async function loadSupervisionQueue() {
    const list = document.getElementById('sup-list');
    const empty = document.getElementById('sup-empty');
    const loader = document.getElementById('sup-loader');
    const badge = document.getElementById('supervision-badge');

    list.classList.add('hidden');
    empty.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const response = await fetch('/api/supervision/pending');
        const data = await response.json();
        loader.classList.add('hidden');

        if (data.length === 0) {
            empty.classList.remove('hidden');
            badge.classList.add('hidden');
        } else {
            list.classList.remove('hidden');
            list.classList.add('flex');
            badge.textContent = data.length;
            badge.classList.remove('hidden');

            list.innerHTML = '';
            data.forEach(item => {
                const violationsHtml = item.violations.map(v => `
                    <span class="px-1.5 py-0.5 bg-red-900/30 text-red-400 border border-red-500/30 rounded text-[9px] font-bold">
                        ${v}
                    </span>
                `).join(' ');

                list.innerHTML += `
                    <div class="glass p-4 md:p-6 rounded-xl md:rounded-2xl border border-gray-700/50 shadow-xl relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-2.5">
                            <span class="text-[8px] md:text-[10px] font-mono text-gray-500 uppercase">${item.review_id}</span>
                        </div>
                        
                        <div class="flex items-start gap-3 md:gap-4 mb-3 md:mb-4">
                            <div class="w-9 h-9 md:w-12 md:h-12 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center text-sm md:text-xl font-bold flex-shrink-0">
                                ${item.client_name.substring(0, 1)}
                            </div>
                            <div>
                                <h4 class="font-bold text-white text-sm md:text-lg leading-tight">${item.client_name}</h4>
                                <p class="text-[10px] md:text-xs text-gray-500 mt-0.5">Feature: ${item.feature.replace('_', ' ').toUpperCase()}</p>
                            </div>
                        </div>

                        <div class="mb-3 md:mb-4">
                            <p class="text-[10px] md:text-xs font-bold text-gray-500 uppercase mb-1.5">Violations Detected</p>
                            <div class="flex flex-wrap gap-1.5">${violationsHtml}</div>
                        </div>

                        <div class="bg-black/30 p-3 md:p-4 rounded-xl border border-gray-700/50 mb-4 md:mb-6">
                            <p class="text-[10px] md:text-xs font-bold text-gray-500 uppercase mb-1">Proposed Recommendation</p>
                            <p class="text-xs md:text-sm text-gray-300 italic leading-relaxed">"${item.recommendation}"</p>
                        </div>

                        <div class="space-y-3">
                            <textarea id="notes-${item.review_id}" class="w-full bg-gray-900/60 border border-gray-700 rounded-lg p-2.5 text-xs text-gray-200 focus:outline-none focus:border-blue-500" rows="2" placeholder="Add supervisor notes here..."></textarea>
                            <div class="flex gap-2">
                                <button onclick="submitSupervisionAction('${item.review_id}', 'APPROVE')" class="flex-1 bg-green-600 hover:bg-green-500 text-white font-bold py-1.5 md:py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 text-xs md:text-sm">
                                    <i class="fa-solid fa-check"></i> Approve
                                </button>
                                <button onclick="submitSupervisionAction('${item.review_id}', 'OVERRIDE')" class="flex-1 bg-red-600 hover:bg-red-500 text-white font-bold py-1.5 md:py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 text-xs md:text-sm">
                                    <i class="fa-solid fa-xmark"></i> Block
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (err) {
        loader.classList.add('hidden');
        showToast('Supervision fetch error: ' + err.message, 'error');
    }
}

async function submitSupervisionAction(reviewId, action) {
    const notes = document.getElementById(`notes-${reviewId}`).value;
    if (!notes) {
        showToast("Mandatory: Please provide supervisor notes explaining the decision.", 'warning');
        return;
    }

    try {
        const response = await fetch('/api/supervision/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                review_id: reviewId,
                action: action,
                notes: notes
            })
        });

        if (response.ok) {
            showToast(`Successfully ${action.toLowerCase()}d recommendation ${reviewId}.`, 'success');
            loadSupervisionQueue(); // Refresh the list
        } else {
            const data = await response.json();
            showToast(`Action failed: ${data.detail}`, 'error');
        }
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    }
}

// Initial check for supervision queue
loadSupervisionQueue();
setInterval(loadSupervisionQueue, 60000); // Check every minute
// -----------------------------------------------------------
// FEATURE 8: Portfolio Scenario Simulator
// -----------------------------------------------------------
async function runSimulation() {
    const clientName = document.getElementById('sim-client-select').value;
    const scenario = document.getElementById('sim-scenario-input').value;
    const btn = document.getElementById('sim-btn');
    const results = document.getElementById('sim-results');
    const empty = document.getElementById('sim-empty');
    
    if (!scenario) {
        showToast("Please describe a scenario first.", 'warning');
        return;
    }
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Simulating...';
    
    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ client_name: clientName, scenario: scenario })
        });
        
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        empty.classList.add('hidden');
        results.classList.remove('hidden');
        
        // Render stats
        renderSimStats('sim-current-stats', data.current);
        renderSimStats('sim-new-stats', data.simulated);
        
        // Render Analysis
        document.getElementById('sim-analysis-text').innerText = data.analysis;
        
        // Render Compliance Badge
        const badge = document.getElementById('sim-compliance-badge');
        badge.innerText = `Compliance: ${data.compliance_status}`;
        if (data.compliance_status === 'PASS') {
            badge.className = 'px-3 py-1 rounded-full text-[10px] font-bold uppercase bg-green-500/20 text-green-400 border border-green-500/30';
        } else if (data.compliance_status === 'FAIL') {
            badge.className = 'px-3 py-1 rounded-full text-[10px] font-bold uppercase bg-red-500/20 text-red-400 border border-red-500/30';
        } else {
            badge.className = 'px-3 py-1 rounded-full text-[10px] font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30';
        }
        
    } catch (err) {
        console.error("Simulation error:", err);
        showToast("Simulation failed. Please try again.", 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-play"></i> Run Simulation';
    }
}

function renderSimStats(containerId, stats) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="grid grid-cols-2 gap-4">
            <div class="bg-black/20 p-3 rounded-xl border border-gray-800">
                <span class="text-[10px] text-gray-500 uppercase font-bold block mb-1">Return</span>
                <span class="text-xl font-bold text-white">${stats.return}%</span>
            </div>
            <div class="bg-black/20 p-3 rounded-xl border border-gray-800">
                <span class="text-[10px] text-gray-500 uppercase font-bold block mb-1">Risk</span>
                <span class="text-xl font-bold ${stats.risk === 'High' ? 'text-red-400' : 'text-green-400'}">${stats.risk}</span>
            </div>
        </div>
        <div class="space-y-3 mt-4">
            ${renderBar('Equity', stats.equity, 'bg-blue-500')}
            ${renderBar('Fixed Income', stats.fixed_income, 'bg-green-500')}
            ${renderBar('Cash', stats.cash, 'bg-gray-500')}
            ${renderBar('Alternatives', stats.alternatives, 'bg-purple-500')}
        </div>
    `;
}

function renderBar(label, value, colorClass) {
    return `
        <div>
            <div class="flex justify-between text-[11px] mb-1">
                <span class="text-gray-400">${label}</span>
                <span class="text-white font-bold">${value}%</span>
            </div>
            <div class="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <div class="${colorClass} h-full" style="width: ${value}%"></div>
            </div>
        </div>
    `;
}

// -----------------------------------------------------------
// FEATURE 10: Revenue Enablement
// -----------------------------------------------------------
async function generateRevenue() {
    const clientName = document.getElementById('rev-client-select').value;
    const btn = document.getElementById('rev-btn');
    const results = document.getElementById('rev-results');
    const empty = document.getElementById('rev-empty');

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';

    try {
        const response = await fetch('/api/revenue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ client_name: clientName })
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        empty.classList.add('hidden');
        results.classList.remove('hidden');
        results.classList.add('flex');

        // Render client header
        const header = document.getElementById('rev-client-header');
        header.innerHTML = `
            <div class="w-14 h-14 rounded-2xl bg-green-600/20 text-green-400 flex items-center justify-center text-2xl font-bold">
                ${data.client_name.charAt(0)}
            </div>
            <div class="flex-1">
                <h3 class="text-xl font-bold text-white">${data.client_name}</h3>
                <p class="text-sm text-gray-400">${data.risk_profile} Profile &nbsp;•&nbsp; AUM: $${(data.aum/1000000).toFixed(1)}M</p>
            </div>
            <div class="text-right">
                <p class="text-[10px] text-gray-500 uppercase font-bold">Opportunities Found</p>
                <p class="text-3xl font-bold text-green-400">${data.opportunities.length}</p>
            </div>
        `;

        // Render opportunity cards
        const cards = document.getElementById('rev-cards');
        cards.innerHTML = '';
        data.opportunities.forEach((opp, idx) => {
            const priorityColor = opp.priority === 'HIGH'
                ? 'text-red-400 bg-red-500/10 border-red-500/30'
                : opp.priority === 'MEDIUM'
                ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
                : 'text-blue-400 bg-blue-500/10 border-blue-500/30';

            const complianceColor = (opp.compliance === 'SUITABLE' || opp.compliance === 'COMPLIANT')
                ? 'text-green-400 bg-green-500/10 border-green-500/30'
                : 'text-red-400 bg-red-500/10 border-red-500/30';

            cards.innerHTML += `
                <div class="glass p-6 rounded-2xl border border-gray-700/50 flex flex-col gap-4 hover:border-green-500/30 transition-all">
                    <div class="flex items-start justify-between">
                        <div class="flex-1">
                            <p class="text-[10px] text-gray-500 uppercase font-bold mb-1">Opportunity ${idx + 1}</p>
                            <h4 class="text-lg font-bold text-white">${opp.product}</h4>
                        </div>
                        <span class="px-2 py-1 rounded-lg text-[10px] font-bold uppercase border ${priorityColor} ml-3">${opp.priority}</span>
                    </div>
                    <p class="text-sm text-gray-300 leading-relaxed">${opp.rationale}</p>
                    <div class="flex items-center justify-between pt-2 border-t border-gray-800">
                        <div>
                            <p class="text-[10px] text-gray-500 uppercase font-bold">Revenue Impact</p>
                            <p class="text-green-400 font-bold text-sm">${opp.revenue_impact}</p>
                        </div>
                        <span class="px-2 py-1 rounded-lg text-[10px] font-bold uppercase border ${complianceColor}">${opp.compliance}</span>
                    </div>
                </div>
            `;
        });

    } catch (err) {
        console.error('Revenue error:', err);
        showToast('Failed to generate opportunities. Please try again.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-sack-dollar"></i> Generate Opportunities';
    }
}
