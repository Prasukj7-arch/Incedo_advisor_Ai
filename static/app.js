// Helper to update clock
function updateClock() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}
setInterval(updateClock, 1000);
updateClock();

// Navigation Logic
const navItems = document.querySelectorAll('.nav-item');
const featureSections = document.querySelectorAll('.feature-section');
const headerTitle = document.getElementById('header-title');
const headerSubtitle = document.getElementById('header-subtitle');

const sectionData = {
    'feature-chat': { title: 'Portfolio Chat', subtitle: 'Ask anything about your client portfolios in natural language.' },
    'feature-rag': { title: 'Research Search', subtitle: 'Search across 5 financial research reports using natural language.' },
    'feature-client360': { title: 'Client 360 — Meeting Prep', subtitle: 'Generate a complete meeting preparation brief for any client instantly.' },
    'feature-compliance': { title: 'Compliance Monitor', subtitle: 'Real-time compliance checks across all client portfolios with CloudWatch audit logging.' },
    'feature-observability': { title: 'AI Observability Console', subtitle: 'Real-time AWS Bedrock token usage, latency, and cost tracking.' }
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
            body: JSON.stringify({ question: query, session_id: 'frontend-session-01' })
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
            alert(`Error: ${data.detail}`);
            ragResultsContainer.classList.add('hidden');
        }
    } catch (err) {
        ragLoader.classList.add('hidden');
        alert(`Error: ${err.message}`);
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
            alert(`Error: ${data.detail || 'Client not found'}`);
        }
    } catch (err) {
        document.getElementById('brief-loader').classList.add('hidden');
        alert(`Error: ${err.message}`);
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
            document.getElementById('c-time').textContent = data.summary.checked_at.replace('T', ' ').substring(0, 16);
            
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
            alert(`Error: ${data.detail}`);
        }
    } catch (err) {
        loader.classList.add('hidden');
        alert(`Error: ${err.message}`);
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
        const apigwText = document.getElementById('text-apigw');
        if (data.api_gateway === 'active') {
            apigwText.innerHTML = '<span class="w-2 h-2 rounded-full bg-green-500" id="status-apigw"></span> <span class="text-gray-300">API Gateway Active</span>';
        } else {
            apigwText.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-500" id="status-apigw"></span> <span class="text-red-400">API Gateway Offline</span>';
        }
        
        // Update Bedrock (tied to API GW)
        const bedrockText = document.getElementById('text-bedrock');
        if (data.bedrock === 'active') {
            bedrockText.innerHTML = '<span class="w-2 h-2 rounded-full bg-green-500" id="status-bedrock"></span> <span class="text-gray-300">Llama 3.1 Bedrock</span>';
        } else {
            bedrockText.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-500" id="status-bedrock"></span> <span class="text-red-400">Bedrock Offline</span>';
        }
        
        // Update EC2
        const ec2Text = document.getElementById('text-ec2');
        if (data.ec2_rag === 'active') {
            ec2Text.innerHTML = '<span class="w-2 h-2 rounded-full bg-green-500" id="status-ec2"></span> <span class="text-gray-300">EC2 ChromaDB</span>';
        } else {
            ec2Text.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-500" id="status-ec2"></span> <span class="text-red-400">EC2 Offline</span>';
        }
        
    } catch (err) {
        console.error("Failed to fetch system status", err);
    }
}

// Check status on load and every 30 seconds
checkSystemStatus();
setInterval(checkSystemStatus, 30000);

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
                        <td class="py-2 text-gray-500 text-xs">${(call.timestamp || '').replace('T', ' ').substring(0, 19)}</td>
                    </tr>
                `;
            });
        }
    } catch (err) {
        loader.classList.add('hidden');
        alert('Error: ' + err.message);
    }
}
