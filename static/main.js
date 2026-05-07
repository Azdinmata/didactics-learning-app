// Global Application State Manager
const AppState = {
    user: null,          // { username, unlocked_index, quiz_scores }
    modules: [],         // Array of active modules
    currentView: -1,     // -1: Homepage / Dashboard, >=0: Module Index
    activeTab: 'Materials', // 'Materials' or 'Quiz'
    chatHistory: [],     // Thread of active assistant logs
    chatOpen: false      // Floating overlay state
};

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", async () => {
    // 1. Fetch user authentication info
    const authOk = await fetchUserData();
    if (!authOk) {
        // Redirection handled by server.py anyway, but safe-fallback
        window.location.href = '/login';
        return;
    }

    // 2. Fetch course modules definitions
    await fetchModules();

    // 3. Render modules menu and active page
    renderSidebar();
    routeToPage(-1); // Start on Homepage/Dashboard view

    // Close mobile menu on click overlay fallback
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('appSidebar');
        const menuToggle = document.getElementById('menuToggle');
        if (window.innerWidth <= 768 && 
            !sidebar.contains(e.target) && 
            !menuToggle.contains(e.target) && 
            sidebar.classList.contains('mobile-open')) {
            sidebar.classList.remove('mobile-open');
        }
    });
});

// --- API FETCHERS ---

async function fetchUserData() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                AppState.user = data.user;
                document.getElementById('profileName').textContent = data.user.username;
                return true;
            }
        }
    } catch (err) {
        console.error("Auth sync failed:", err);
    }
    return false;
}

async function fetchModules() {
    try {
        const response = await fetch('/api/modules');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                AppState.modules = data.modules;
            }
        }
    } catch (err) {
        console.error("Failed to load modules:", err);
    }
}

async function saveProgressOnServer() {
    try {
        await fetch('/api/progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                unlocked_index: AppState.user.unlocked_index,
                quiz_scores: AppState.user.quiz_scores
            })
        });
    } catch (err) {
        console.error("Progress save failed:", err);
    }
}

// --- RENDERING ROUTINES ---

function renderSidebar() {
    const list = document.getElementById('modulesList');
    list.innerHTML = '';

    // Add Homepage link
    const homeBtn = document.createElement('button');
    homeBtn.className = `module-item-btn ${AppState.currentView === -1 ? 'active' : ''}`;
    homeBtn.innerHTML = `
        <span class="module-icon-status">🏠</span>
        <span class="module-label-title">Homepage / Dashboard</span>
    `;
    homeBtn.onclick = () => {
        routeToPage(-1);
        if (window.innerWidth <= 768) {
            document.getElementById('appSidebar').classList.remove('mobile-open');
        }
    };
    list.appendChild(homeBtn);

    // Add list of lesson modules
    AppState.modules.forEach((mod, idx) => {
        const isLocked = idx > AppState.user.unlocked_index;
        const btn = document.createElement('button');
        btn.className = `module-item-btn ${isLocked ? 'locked' : ''} ${AppState.currentView === idx ? 'active' : ''}`;
        
        let statusIcon = '🔒';
        if (!isLocked) {
            const passed = AppState.user.quiz_scores[idx] >= 8;
            statusIcon = passed ? '✅' : '📖';
        }

        const scoreText = AppState.user.quiz_scores[idx] !== undefined 
            ? `<span class="module-score-pill">${AppState.user.quiz_scores[idx]}/10</span>`
            : '';

        btn.innerHTML = `
            <span class="module-icon-status">${statusIcon}</span>
            <span class="module-label-title">Module ${idx + 1}: ${mod.title}</span>
            ${scoreText}
        `;

        btn.onclick = () => {
            if (isLocked) {
                alert("🔒 This lesson is locked. Pass the previous module's quiz to unlock it!");
                return;
            }
            routeToPage(idx);
            if (window.innerWidth <= 768) {
                document.getElementById('appSidebar').classList.remove('mobile-open');
            }
        };

        list.appendChild(btn);
    });
}

function routeToPage(viewIndex) {
    AppState.currentView = viewIndex;
    renderSidebar();

    // RESET SCROLL LEVELS TO THE VERY TOP IMMEDIATELY ON NAVIGATION
    const viewport = document.querySelector('.workspace-viewport');
    if (viewport) {
        viewport.scrollTop = 0;
    }
    const pdfContainer = document.getElementById('pdfCanvasContainer');
    if (pdfContainer) {
        pdfContainer.scrollTop = 0;
    }

    const welcomeBanner = document.getElementById('welcomeBanner');
    const workspaceCard = document.getElementById('workspaceCard');

    if (viewIndex === -1) {
        // HOMEPAGE / DASHBOARD VIEW
        welcomeBanner.style.display = 'block';
        workspaceCard.style.display = 'none';

        const u = AppState.user;
        const total = AppState.modules.length;
        const finished = Object.keys(u.quiz_scores).filter(k => u.quiz_scores[k] >= 8).length;

        welcomeBanner.innerHTML = `
            <h1 class="welcome-title">🎓 Welcome back, ${u.username}!</h1>
            <p class="welcome-desc">
                Continue your professional teaching journey. You have completed <strong>${finished} of ${total}</strong> modules!
                Select a textbook from the list on the left to start reading or taking assessment checks.
            </p>
        `;
    } else {
        // MODULE ACTIVE VIEW
        welcomeBanner.style.display = 'none';
        workspaceCard.style.display = 'block';

        const mod = AppState.modules[viewIndex];
        
        // Sync header details
        document.getElementById('workspaceBadge').textContent = `Module ${viewIndex + 1}`;
        document.getElementById('workspaceTitle').textContent = mod.title;
        document.getElementById('workspaceDesc').textContent = mod.description;

        // Reset active tab to slides
        switchActiveTab('Materials');
    }
}

function switchActiveTab(tabName) {
    AppState.activeTab = tabName;
    
    // Reset viewport scroll to top instantly when switching tabs!
    const viewport = document.querySelector('.workspace-viewport');
    if (viewport) {
        viewport.scrollTop = 0;
    }
    
    const matView = document.getElementById('materialsView');
    const qView = document.getElementById('quizView');

    if (tabName === 'Materials') {
        matView.classList.add('active');
        qView.classList.remove('active');
        loadLessonPresentation();
    } else {
        matView.classList.remove('active');
        qView.classList.add('active');
        loadLessonQuiz();
    }
}

// --- SERVER-SIDE PYPDFIUM2 PRESENTATION GENERATION ---

async function loadLessonPresentation() {
    const viewIndex = AppState.currentView;
    const container = document.getElementById('pdfCanvasContainer');
    
    // Prevent re-rendering same pdf if already rendered and visible
    if (container.dataset.activeModule === String(viewIndex)) return;

    container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 14px;">📖 Syncing textbook slides with PDFium engine...</div>';

    try {
        const response = await fetch(`/api/pdf-info/${viewIndex}`);
        const result = await response.json();

        if (response.ok && result.success) {
            container.innerHTML = ''; // clear loading message
            container.dataset.activeModule = String(viewIndex);

            // Dynamically inject lazy-loaded individual page images
            for (let pIdx = 0; pIdx < result.num_pages; pIdx++) {
                const wrapper = document.createElement('div');
                wrapper.className = 'pdf-page-wrapper';
                wrapper.style.minHeight = '360px'; // Pre-allocate height to prevent scroll jumps
                wrapper.style.background = '#ffffff';

                const img = document.createElement('img');
                // Point source to the individual page-rendering endpoint
                img.src = `/api/pdf-page-img/${viewIndex}/${pIdx}`;
                img.alt = `Slide ${pIdx + 1}`;
                img.loading = "lazy"; // Browser native high-performance lazy loading!

                // Remove placeholder min-height once the image is fully loaded and self-sized
                img.onload = () => {
                    wrapper.style.minHeight = 'unset';
                };

                wrapper.appendChild(img);
                container.appendChild(wrapper);
            }
        } else {
            container.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--error); font-size: 14px;">⚠️ Failed to load presentation metadata: ${result.message || 'Unknown error'}</div>`;
            container.dataset.activeModule = "";
        }
    } catch (err) {
        container.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--error); font-size: 14px;">⚠️ Error connecting to slide server: ${err.message}</div>`;
        container.dataset.activeModule = "";
    }
}

// --- MODULE ASSESSMENT SYSTEM ---

function loadLessonQuiz() {
    const mod = AppState.modules[AppState.currentView];
    const container = document.getElementById('quizQuestionsList');
    container.innerHTML = '';

    // Hide feedback box and next module buttons
    document.getElementById('quizFeedbackBox').style.display = 'none';
    document.getElementById('nextLessonBlock').style.display = 'none';

    mod.quiz.forEach((q, qIdx) => {
        const card = document.createElement('div');
        card.className = 'quiz-question-card';
        card.id = `question_card_${qIdx}`;

        let optionsHTML = '';
        q.options.forEach((opt, oIdx) => {
            optionsHTML += `
                <label class="option-label" id="label_${qIdx}_${oIdx}">
                    <input type="radio" name="question_${qIdx}" class="option-radio" value="${oIdx}" required>
                    <span>${opt}</span>
                </label>
            `;
        });

        card.innerHTML = `
            <div class="question-text">Question ${qIdx + 1}: ${q.question}</div>
            <div class="options-group">
                ${optionsHTML}
            </div>
            <div class="question-feedback-box" id="qFeedback_${qIdx}" style="display:none;"></div>
        `;

        container.appendChild(card);
    });

    // Check if user has already passed this quiz before
    const score = AppState.user.quiz_scores[AppState.currentView];
    if (score >= 8) {
        showPassedStatus(score);
    }
}

function handleQuizSubmit(event) {
    event.preventDefault();
    const mod = AppState.modules[AppState.currentView];
    let score = 0;

    mod.quiz.forEach((q, qIdx) => {
        const selectedRadio = document.querySelector(`input[name="question_${qIdx}"]:checked`);
        const qFeedback = document.getElementById(`qFeedback_${qIdx}`);
        qFeedback.style.display = 'block';

        const userAnsIndex = parseInt(selectedRadio.value);
        const correctIndex = q.correct_index;

        // Reset label classes
        q.options.forEach((_, oIdx) => {
            document.getElementById(`label_${qIdx}_${oIdx}`).className = 'option-label';
        });

        if (userAnsIndex === correctIndex) {
            score++;
            document.getElementById(`label_${qIdx}_${userAnsIndex}`).className = 'option-label correct';
            qFeedback.textContent = `✅ Correct! ${q.feedback}`;
            qFeedback.className = 'question-feedback-box correct';
        } else {
            document.getElementById(`label_${qIdx}_${userAnsIndex}`).className = 'option-label incorrect';
            document.getElementById(`label_${qIdx}_${correctIndex}`).className = 'option-label correct';
            qFeedback.textContent = `❌ Incorrect. Correct Answer: "${q.options[correctIndex]}". ${q.feedback}`;
            qFeedback.className = 'question-feedback-box incorrect';
        }
    });

    // Handle score calculation
    const passed = score >= 8;
    const feedbackBox = document.getElementById('quizFeedbackBox');
    feedbackBox.style.display = 'block';
    feedbackBox.className = `quiz-feedback-box ${passed ? 'success' : 'failed'}`;

    document.getElementById('feedbackScore').textContent = `Score: ${score}/10`;
    
    if (passed) {
        document.getElementById('feedbackText').textContent = "🎉 Outstanding! You passed the module check.";
        
        // Save score if it is a personal best
        const oldScore = AppState.user.quiz_scores[AppState.currentView] || 0;
        if (score > oldScore) {
            AppState.user.quiz_scores[AppState.currentView] = score;
        }

        // Unlock next index if applicable
        if (AppState.currentView === AppState.user.unlocked_index && AppState.user.unlocked_index < AppState.modules.length - 1) {
            AppState.user.unlocked_index++;
        }

        saveProgressOnServer();
        renderSidebar();
        showPassedStatus(score);
        launchConfetti();
    } else {
        document.getElementById('feedbackText').textContent = "❌ Not quite there yet. Please read through the textbook and try again.";
        document.getElementById('nextLessonBlock').style.display = 'none';
    }

    // Scroll smoothly to feedback box
    feedbackBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showPassedStatus(score) {
    const block = document.getElementById('nextLessonBlock');
    block.style.display = 'block';

    const text = block.querySelector('.congrats-text');
    const btn = document.getElementById('btnNextLesson');

    if (AppState.currentView < AppState.modules.length - 1) {
        text.textContent = `🏆 Quiz Passed! Score: ${score}/10. Ready to proceed.`;
        btn.textContent = "Proceed to Next Lesson ➔";
        btn.style.display = 'inline-block';
    } else {
        text.textContent = `🎓 Sensational! You have mastered all modules in this course with a high score of ${score}/10!`;
        btn.style.display = 'none';
    }
}

function advanceToNextModule() {
    routeToPage(AppState.currentView + 1);
}

// --- FLOATING SOCRATIC CHAT ASSISTANT ---

function toggleFloatingChat(forceOpen = null) {
    const panel = document.getElementById('chatPanel');
    const icon = document.getElementById('bubbleIcon');
    
    if (forceOpen !== null) {
        AppState.chatOpen = forceOpen;
    } else {
        AppState.chatOpen = !AppState.chatOpen;
    }

    panel.classList.toggle('active', AppState.chatOpen);
    icon.textContent = AppState.chatOpen ? '✕' : '💬';

    if (AppState.chatOpen) {
        scrollChatToBottom();
    }
}

async function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const prompt = input.value.trim();
    if (!prompt) return;

    input.value = ''; // clear input

    // Append User message
    appendChatBubble('user', prompt);
    AppState.chatHistory.push({ role: 'user', content: prompt });

    // Show loading spinner
    const loader = document.getElementById('chatLoader');
    loader.style.display = 'block';
    scrollChatToBottom();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                history: AppState.chatHistory,
                module_index: AppState.currentView
            })
        });

        const result = await response.json();
        loader.style.display = 'none';

        if (response.ok && result.success) {
            appendChatBubble('assistant', result.response);
            AppState.chatHistory.push({ role: 'assistant', content: result.response });
        } else {
            appendChatBubble('assistant', '⚠️ I had trouble connecting to the brain server. Please try again.');
        }
    } catch (err) {
        loader.style.display = 'none';
        appendChatBubble('assistant', '⚠️ Server connection timeout. Verify connection and retry.');
    }

    scrollChatToBottom();
}

function appendChatBubble(role, content) {
    const container = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    
    // Parse mini markdown citations and bullet blocks for tutoring responses
    let formatted = content
        .replace(/> "(.*?)"/g, '<blockquote>"$1"</blockquote>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n\* (.*?)/g, '<br>• $1');

    bubble.innerHTML = formatted;
    container.appendChild(bubble);
}

function scrollChatToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

// --- PREMIUM CONFETTI ANIMATION SCRIPT ---

function launchConfetti() {
    const container = document.getElementById('confettiContainer');
    container.innerHTML = '';

    const colors = ['#2563eb', '#4f46e5', '#10b981', '#f59e0b', '#f43f5e', '#a855f7'];

    for (let i = 0; i < 120; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        
        piece.style.left = `${Math.random() * 100}vw`;
        piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        
        const scale = 0.5 + Math.random() * 0.8;
        piece.style.transform = `scale(${scale})`;
        
        const delay = Math.random() * 0.5;
        piece.style.animationDelay = `${delay}s`;
        
        const duration = 2 + Math.random() * 2;
        piece.style.animationDuration = `${duration}s`;

        container.appendChild(piece);
    }

    // Auto-cleanup confetti elements
    setTimeout(() => {
        container.innerHTML = '';
    }, 4500);
}

// --- UTILS ---

function toggleMobileSidebar() {
    const sidebar = document.getElementById('appSidebar');
    sidebar.classList.toggle('mobile-open');
}

async function handleLogout() {
    try {
        const res = await fetch('/api/auth/logout', { method: 'POST' });
        if (res.ok) {
            window.location.href = '/login';
        }
    } catch (err) {
        console.error("Logout failed:", err);
    }
}

// --- FULLSCREEN PRESENTATION VIEWER TOGGLE ---

function togglePdfFullscreen() {
    const outerContainer = document.querySelector('.pdf-container-outer');
    const toggleBtn = document.getElementById('pdfScaleToggle');
    
    if (!outerContainer || !toggleBtn) return;
    
    const isFullscreen = outerContainer.classList.toggle('fullscreen-active');
    document.body.classList.toggle('pdf-fullscreen-active', isFullscreen);
    
    if (isFullscreen) {
        toggleBtn.innerHTML = '<span>🗜️ Close Fullscreen</span>';
        toggleBtn.classList.add('active');
        document.body.style.overflow = 'hidden'; // Lock main scroll
    } else {
        toggleBtn.innerHTML = '<span>🔍 Maximize Presentation</span>';
        toggleBtn.classList.remove('active');
        document.body.style.overflow = ''; // Restore main scroll
    }
}
