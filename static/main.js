// ==========================================================================
// UNIFIED FRONT-END SINGLE PAGE APPLICATION STATE MANAGER
// ==========================================================================

const AppState = {
    user: null,               // { username, unlocked_index, quiz_scores }
    modules: [],              // Array of modules from /api/modules
    currentView: -1,          // -1: Dashboard Home, >=0: Module Index
    activeTab: "Materials",   // "Materials" or "Quiz"
    
    // Slide State Tracking (Offline server-rendered images)
    pdfState: {
        pageNum: 1,
        numPages: 1
    },
    
    // AI Chat History Cache
    chatHistory: [
        { role: "assistant", content: "Hello! I'm your Socratic Didactics Tutor. Select any course lesson and ask me about the pedagogical models, classroom methods, or textbook concepts!" }
    ]
};

// --- INITIALIZE APPLICATION UPON DOM READY ---
document.addEventListener("DOMContentLoaded", () => {
    // Run bootstrapping sequence
    bootstrapApp();
});

// ==========================================================================
// BOOTSTRAP SYSTEM & AUTH SESSION HOOKS
// ==========================================================================

async function bootstrapApp() {
    try {
        // 1) Fetch current logged-in user profile details
        const userRes = await fetch("/api/user");
        if (!userRes.ok) {
            // Unauthorized session redirect
            window.location.href = "/login";
            return;
        }
        const userData = await userRes.json();
        AppState.user = userData.user;
        
        const greeting = document.getElementById("user-greeting");
        if (greeting) {
            const prefix = AppState.user.is_new_user ? "Welcome" : "Welcome back";
            greeting.textContent = `${prefix}, Teacher ${AppState.user.username}`;
        }
        
        // 2) Fetch syllabus curriculum modules
        const modRes = await fetch("/api/modules");
        const modData = await modRes.json();
        AppState.modules = modData.modules;
        
        // 3) Render core layout frames
        renderCurriculumSidebar();
        renderDashboardView();
        
    } catch (err) {
        console.error("Bootstrapping error:", err);
    }
}

async function handleLogout() {
    try {
        const res = await fetch("/api/auth/logout", { method: "POST" });
        if (res.ok) {
            window.location.href = "/login";
        }
    } catch (err) {
        console.error("Logout communication error:", err);
    }
}

// ==========================================================================
// DYNAMIC CURRICULUM SIDEBAR & PROGRESS CONTROLLERS
// ==========================================================================

function renderCurriculumSidebar() {
    const navList = document.getElementById("module-navigation-list");
    if (!navList) return;
    
    navList.innerHTML = "";
    
    const unlockedIndex = AppState.user.unlocked_index;
    const currentActiveView = AppState.currentView;
    
    let completedCount = 0;
    
    AppState.modules.forEach((mod, idx) => {
        const isLocked = idx > unlockedIndex;
        
        // Check if previously passed quiz with score >= 8
        const bestScore = AppState.user.quiz_scores[idx.toString()] || 0;
        const isPassed = bestScore >= 8;
        if (isPassed) completedCount++;
        
        // Create navigation item element
        const card = document.createElement("button");
        card.className = `module-nav-card ${isLocked ? "locked" : ""} ${currentActiveView === idx ? "active" : ""}`;
        card.disabled = isLocked;
        card.onclick = () => {
            if (!isLocked) loadModule(idx);
        };
        
        // Standardize card items formatting
        let statusEmoji = "🔒";
        if (!isLocked) {
            statusEmoji = isPassed ? "✅" : "📖";
        }
        
        card.innerHTML = `
            <div class="mod-num-tag">Module ${idx + 1}</div>
            <div class="mod-title">${mod.title}</div>
            <span class="mod-status">${statusEmoji}</span>
        `;
        
        navList.appendChild(card);
    });
    
    // Update Global Course Progress Bar Meta
    const progressPct = Math.round((completedCount / AppState.modules.length) * 100);
    const overallPctText = document.getElementById("overall-progress-text");
    const overallBarFill = document.getElementById("overall-progress-bar");
    
    if (overallPctText) overallPctText.textContent = `${progressPct}% Complete`;
    if (overallBarFill) overallBarFill.style.width = `${progressPct}%`;
}

// ==========================================================================
// NAVIGATION SPA VIEW SWITCHERS
// ==========================================================================

function goHome() {
    AppState.currentView = -1;
    AppState.activeTab = "Materials";
    
    // Toggle containers visibility
    document.getElementById("dashboard-container").style.display = "block";
    document.getElementById("lesson-workspace").style.display = "none";
    
    // Clean theater presentation mode if active
    const pdfWrapper = document.querySelector(".pdf-wrapper");
    if (pdfWrapper) pdfWrapper.classList.remove("theater-mode-active");
    document.body.classList.remove("theater-mode-active");
    if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
        const exitMethod = document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen;
        if (exitMethod) exitMethod.call(document).catch(() => {});
    }
    
    renderCurriculumSidebar();
    renderDashboardView();
    
    // Force Scroll reset to top
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderDashboardView() {
    const welcomeTitle = document.getElementById("welcome-title");
    if (welcomeTitle) {
        const prefix = AppState.user.is_new_user ? "Welcome" : "Welcome back";
        welcomeTitle.textContent = `${prefix}, Teacher ${AppState.user.username}!`;
    }
    
    const grid = document.getElementById("dashboard-modules-grid");
    if (!grid) return;
    
    grid.innerHTML = "";
    
    AppState.modules.forEach((mod, idx) => {
        const isLocked = idx > AppState.user.unlocked_index;
        const bestScore = AppState.user.quiz_scores[idx.toString()] || null;
        
        const card = document.createElement("div");
        card.className = "dashboard-mod-card";
        card.style.opacity = isLocked ? "0.6" : "1";
        card.onclick = () => {
            if (!isLocked) loadModule(idx);
        };
        
        let scoreLabel = "";
        if (bestScore !== null) {
            scoreLabel = `<span style="font-size:12px; font-weight:700; color:#10b981; margin-left: 8px;">Passed: ${bestScore}/10</span>`;
        } else if (isLocked) {
            scoreLabel = `<span style="font-size:12px; font-weight:600; color:#9ca3af; margin-left: 8px;">Locked 🔒</span>`;
        } else {
            scoreLabel = `<span style="font-size:12px; font-weight:700; color:#3b82f6; margin-left: 8px;">Active 📖</span>`;
        }
        
        card.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span class="mod-num-tag">Module ${idx + 1}</span>
                ${scoreLabel}
            </div>
            <h3>${mod.title}</h3>
            <p>${mod.description || "Learn pedagogical methods, key terms, teaching applications, and didactic foundations."}</p>
        `;
        
        grid.appendChild(card);
    });
}

// ==========================================================================
// ASYNC CORE LESSON & TEXTBOOK PDF VIEWER (PDF.JS)
// ==========================================================================

async function loadModule(idx) {
    AppState.currentView = idx;
    AppState.activeTab = "Materials";
    
    // Toggle active display viewports
    document.getElementById("dashboard-container").style.display = "none";
    document.getElementById("lesson-workspace").style.display = "block";
    
    // Clean theater viewport overlays
    const pdfWrapper2 = document.querySelector(".pdf-wrapper");
    if (pdfWrapper2) pdfWrapper2.classList.remove("theater-mode-active");
    document.body.classList.remove("theater-mode-active");
    if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
        const exitMethod = document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen;
        if (exitMethod) exitMethod.call(document).catch(() => {});
    }
    
    // Update details texts
    const mod = AppState.modules[idx];
    document.getElementById("breadcrumb-current-module").textContent = `Module ${idx + 1}`;
    document.getElementById("active-module-title").textContent = mod.title;
    
    // Show Materials Panel
    switchToTab("Materials");
    
    // Render dynamic navigation updates
    renderCurriculumSidebar();
    
    // Trigger offline slide image loader sequence
    initPdfViewerOffline(idx);
}

function switchToTab(tabName) {
    AppState.activeTab = tabName;
    
    const panelMat = document.getElementById("panel-materials");
    const panelQuiz = document.getElementById("panel-quiz");
    
    if (tabName === "Materials") {
        panelMat.style.display = "block";
        panelQuiz.style.display = "none";
        document.getElementById("btn-theater-mode").style.display = "inline-flex";
    } else {
        panelMat.style.display = "none";
        panelQuiz.style.display = "block";
        document.getElementById("btn-theater-mode").style.display = "none";
        
        // Lazy initialize the quiz layout when loading check panel
        renderQuizCheckpoint();
    }
    
    // ----------------------------------------------------------------------
    // CRITICAL FIX: AUTOMATIC SCROLL RESET ON VIEWPORT TRANSITION
    // ----------------------------------------------------------------------
    const activeCard = document.querySelector(".workspace-card");
    if (activeCard) {
        // Reset local workspace card scroll to 0
        activeCard.scrollTop = 0;
    }
    // Also scroll the main browser window to top
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// Offline server-side image presentation rendering pipeline
async function initPdfViewerOffline(moduleIdx) {
    const spinner = document.getElementById("pdf-spinner");
    if (spinner) spinner.style.display = "flex";
    
    try {
        const res = await fetch(`/api/slides/${moduleIdx}/meta`);
        const data = await res.json();
        
        if (res.ok && data.success) {
            AppState.pdfState.numPages = data.num_pages;
            AppState.pdfState.pageNum = 1;
            document.getElementById("pdf-page-num").textContent = `Slide 1 of ${data.num_pages}`;
            
            // Trigger image render page 1
            renderSlideImage();
        } else {
            throw new Error(data.message || "Failed to load PDF metadata");
        }
    } catch (err) {
        console.error("PDF metadata loading error:", err);
        if (spinner) {
            spinner.querySelector("span").textContent = "Error loading slide presentation. Please verify that the PDF exists inside your 'lessons' folder.";
            spinner.querySelector(".spinner").style.display = "none";
        }
    }
}

function renderSlideImage() {
    const spinner = document.getElementById("pdf-spinner");
    if (spinner) spinner.style.display = "flex";
    
    const img = document.getElementById("pdf-render-image");
    const pageNum = AppState.pdfState.pageNum;
    const moduleIdx = AppState.currentView;
    
    if (!img) return;
    
    img.onload = () => {
        if (spinner) spinner.style.display = "none";
    };
    
    img.onerror = () => {
        if (spinner) {
            spinner.querySelector("span").textContent = "Error rendering slide image.";
            spinner.querySelector(".spinner").style.display = "none";
        }
    };
    
    // Set source dynamically to trigger server-side pypdfium2 rendering
    img.src = `/api/slides/${moduleIdx}/${pageNum}?t=${new Date().getTime()}`;
    document.getElementById("pdf-page-num").textContent = `Slide ${pageNum} of ${AppState.pdfState.numPages}`;
}

function changePage(delta) {
    if (!AppState.pdfState.numPages) return;
    
    let newPage = AppState.pdfState.pageNum + delta;
    if (newPage < 1) newPage = 1;
    if (newPage > AppState.pdfState.numPages) newPage = AppState.pdfState.numPages;
    
    if (newPage !== AppState.pdfState.pageNum) {
        AppState.pdfState.pageNum = newPage;
        renderSlideImage();
    }
}

// Interactive Fullscreen scaling toggle with native Fullscreen API support
function togglePdfFullscreen() {
    const pdfWrapper = document.querySelector(".pdf-wrapper");
    if (!pdfWrapper) return;
    
    const isFullscreen = !!(document.fullscreenElement || 
                            document.webkitFullscreenElement || 
                            document.mozFullScreenElement || 
                            document.msFullscreenElement);
                            
    if (!isFullscreen) {
        const requestMethod = pdfWrapper.requestFullscreen || 
                              pdfWrapper.webkitRequestFullscreen || 
                              pdfWrapper.mozRequestFullScreen || 
                              pdfWrapper.msRequestFullscreen;
                              
        if (requestMethod) {
            requestMethod.call(pdfWrapper).catch(err => {
                console.warn("Native fullscreen request failed, falling back to CSS theater mode:", err);
            });
        }
        pdfWrapper.classList.add("theater-mode-active");
        document.body.classList.add("theater-mode-active");
    } else {
        const exitMethod = document.exitFullscreen || 
                           document.webkitExitFullscreen || 
                           document.mozCancelFullScreen || 
                           document.msExitFullscreen;
                           
        if (exitMethod) {
            exitMethod.call(document).catch(err => {
                console.warn("Native fullscreen exit failed:", err);
            });
        }
        pdfWrapper.classList.remove("theater-mode-active");
        document.body.classList.remove("theater-mode-active");
    }
}

function handleFullscreenChange() {
    const pdfWrapper = document.querySelector(".pdf-wrapper");
    if (!pdfWrapper) return;
    
    const isFullscreen = !!(document.fullscreenElement || 
                            document.webkitFullscreenElement || 
                            document.mozFullScreenElement || 
                            document.msFullscreenElement);
                            
    if (isFullscreen) {
        pdfWrapper.classList.add("theater-mode-active");
        document.body.classList.add("theater-mode-active");
    } else {
        pdfWrapper.classList.remove("theater-mode-active");
        document.body.classList.remove("theater-mode-active");
    }
}

document.addEventListener("fullscreenchange", handleFullscreenChange);
document.addEventListener("webkitfullscreenchange", handleFullscreenChange);
document.addEventListener("mozfullscreenchange", handleFullscreenChange);
document.addEventListener("MSFullscreenChange", handleFullscreenChange);

// ==========================================================================
// DYNAMIC QUIZ CARD RENDERER & ASYNC ASSESSMENT GRADER
// ==========================================================================

function renderQuizCheckpoint() {
    const quizList = document.getElementById("quiz-questions-list");
    if (!quizList) return;
    
    quizList.innerHTML = "";
    
    const mod = AppState.modules[AppState.currentView];
    const questions = mod.quiz || [];
    
    // Reset assessment notices state
    document.getElementById("quiz-result-feedback").style.display = "none";
    document.getElementById("btn-next-lesson").style.display = "none";
    
    if (questions.length === 0) {
        quizList.innerHTML = `<div style="text-align:center; padding: 20px; color:var(--text-secondary);">No assessment checkpoint found for this module.</div>`;
        return;
    }
    
    questions.forEach((q, qIdx) => {
        const qCard = document.createElement("div");
        qCard.className = "quiz-q-card";
        qCard.id = `quiz-q-block-${qIdx}`;
        
        let optionsHTML = "";
        q.options.forEach((opt, oIdx) => {
            optionsHTML += `
                <label class="option-bubble" id="lbl-q${qIdx}-o${oIdx}">
                    <input type="radio" name="q-${qIdx}" value="${oIdx}" onclick="selectOption(${qIdx}, ${oIdx})">
                    <span>${opt}</span>
                </label>
            `;
        });
        
        qCard.innerHTML = `
            <div class="q-header">
                <span class="q-badge">${qIdx + 1}</span>
                <span class="q-text">${q.question}</span>
            </div>
            <div class="q-options-stack">
                ${optionsHTML}
            </div>
            <div class="option-feedback" id="feedback-q-${qIdx}" style="display:none;"></div>
        `;
        
        quizList.appendChild(qCard);
    });
}

function selectOption(qIdx, oIdx) {
    // Styling feedback on input selection
    const mod = AppState.modules[AppState.currentView];
    const totalOptions = mod.quiz[qIdx].options.length;
    
    for (let i = 0; i < totalOptions; i++) {
        const bubble = document.getElementById(`lbl-q${qIdx}-o${i}`);
        if (bubble) {
            if (i === oIdx) {
                bubble.classList.add("selected");
            } else {
                bubble.classList.remove("selected");
            }
        }
    }
}

async function handleQuizSubmit(e) {
    e.preventDefault();
    
    const mod = AppState.modules[AppState.currentView];
    const questions = mod.quiz || [];
    
    let score = 0;
    let unanswered = 0;
    const userAnswers = {};
    
    questions.forEach((q, qIdx) => {
        const selectedRadio = document.querySelector(`input[name="q-${qIdx}"]:checked`);
        if (!selectedRadio) {
            unanswered++;
        } else {
            const val = parseInt(selectedRadio.value);
            userAnswers[qIdx] = val;
            if (val === q.correct_index) {
                score++;
            }
        }
    });
    
    // Prevent submissions if questions remain unanswered
    if (unanswered > 0) {
        alert(`⚠️ You missed ${unanswered} question(s). Please answer all questions before submitting!`);
        return;
    }
    
    // Apply visual feedback styling on card bubbles
    questions.forEach((q, qIdx) => {
        const selectedVal = userAnswers[qIdx];
        const correctVal = q.correct_index;
        const feedbackBlock = document.getElementById(`feedback-q-${qIdx}`);
        
        // Style option card bubbles
        q.options.forEach((opt, oIdx) => {
            const bubble = document.getElementById(`lbl-q${qIdx}-o${oIdx}`);
            if (bubble) {
                bubble.classList.remove("selected", "correct", "wrong");
                
                if (oIdx === correctVal) {
                    bubble.classList.add("correct");
                } else if (oIdx === selectedVal && selectedVal !== correctVal) {
                    bubble.classList.add("wrong");
                }
            }
        });
        
        // Populate inline feedback explanation blocks
        if (feedbackBlock) {
            feedbackBlock.style.display = "block";
            if (selectedVal === correctVal) {
                feedbackBlock.className = "option-feedback correct-lbl";
                feedbackBlock.innerHTML = `✅ **Correct!** ${q.feedback || ""}`;
            } else {
                feedbackBlock.className = "option-feedback wrong-lbl";
                feedbackBlock.innerHTML = `❌ **Incorrect.** (Correct: Option ${correctVal + 1})<br>${q.feedback || ""}`;
            }
        }
    });
    
    // Check passing status (score >= 8)
    const isPass = score >= 8;
    const feedbackBox = document.getElementById("quiz-result-feedback");
    const scoreText = document.getElementById("result-score-text");
    const scoreMessage = document.getElementById("result-score-message");
    const nextBtn = document.getElementById("btn-next-lesson");
    
    if (feedbackBox) {
        feedbackBox.style.display = "block";
        feedbackBox.className = `quiz-result-box ${isPass ? "pass" : "fail"}`;
        
        if (scoreText) scoreText.textContent = `Score: ${score} / ${questions.length}`;
        
        if (isPass) {
            if (scoreMessage) scoreMessage.textContent = "🎉 Congratulations! You passed the module check and unlocked the next lesson!";
            
            // Check if there is a next lesson to navigate to
            if (AppState.currentView < AppState.modules.length - 1) {
                if (nextBtn) nextBtn.style.display = "inline-flex";
            }
            
            // Update local AppState and notify Flask server async
            const lastUnlocked = AppState.user.unlocked_index;
            const currentView = AppState.currentView;
            
            // Increment unlocked bounds if passing current outermost lesson
            const newUnlocked = currentView === lastUnlocked ? currentView + 1 : lastUnlocked;
            
            // Record score
            const updatedScores = { ...AppState.user.quiz_scores };
            const priorBest = updatedScores[currentView.toString()] || 0;
            updatedScores[currentView.toString()] = Math.max(priorBest, score);
            
            AppState.user.unlocked_index = newUnlocked;
            AppState.user.quiz_scores = updatedScores;
            
            // POST async progress to backend server
            await fetch("/api/progress", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    unlocked_index: newUnlocked,
                    quiz_scores: updatedScores
                })
            });
            
            // Refresh sidebar nodes state
            renderCurriculumSidebar();
            
        } else {
            if (scoreMessage) scoreMessage.textContent = "❌ Not quite there yet. Review your slide presentation and try again!";
            if (nextBtn) nextBtn.style.display = "none";
        }
        
        // Smooth scroll results into view
        feedbackBox.scrollIntoView({ behavior: "smooth" });
    }
}

function goToNextLesson() {
    if (AppState.currentView < AppState.modules.length - 1) {
        loadModule(AppState.currentView + 1);
    }
}

// ==========================================================================
// ASYNC FLOATING AI TUTOR CHAT ENDPOINTS INTERFACE
// ==========================================================================

function toggleChatPanel() {
    const panel = document.getElementById("floating-chat-container");
    const launcher = document.getElementById("chatbot-launcher-btn");
    
    if (panel && launcher) {
        panel.classList.toggle("open");
        
        const isOpen = panel.classList.contains("open");
        
        const chatIcon = launcher.querySelector(".fab-chat-icon");
        const closeIcon = launcher.querySelector(".fab-close-icon");
        
        if (isOpen) {
            chatIcon.style.display = "none";
            closeIcon.style.display = "block";
            launcher.style.background = "#ef4444";
            
            // Scroll to the end of dialogue history
            scrollChatHistoryToBottom();
            
            // Autofocus chatbot textbox on opening on desktop
            if (window.innerWidth > 768) {
                document.getElementById("chat-message-textbox").focus();
            }
        } else {
            chatIcon.style.display = "block";
            closeIcon.style.display = "none";
            launcher.style.background = ""; // Restores theme default
        }
    }
}

async function sendChatMessage(e) {
    e.preventDefault();
    
    const msgInput = document.getElementById("chat-message-textbox");
    const dialogueViewport = document.getElementById("chat-conversation-history");
    const spinner = document.getElementById("tutor-typing-spinner");
    
    if (!msgInput || !msgInput.value.trim()) return;
    
    const query = msgInput.value.trim();
    msgInput.value = ""; // Clean input textbox
    
    // Append User message to local cache and render bubble
    AppState.chatHistory.push({ role: "user", content: query });
    appendChatBubble("user", query);
    scrollChatHistoryToBottom();
    
    // Show AI typing indicator
    if (spinner) spinner.style.display = "flex";
    scrollChatHistoryToBottom();
    
    try {
        const chatRes = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: AppState.chatHistory,
                current_module_index: AppState.currentView
            })
        });
        
        const chatData = await chatRes.json();
        
        // Hide AI typing indicator
        if (spinner) spinner.style.display = "none";
        
        if (chatRes.ok && chatData.success) {
            const reply = chatData.response;
            AppState.chatHistory.push({ role: "assistant", content: reply });
            appendChatBubble("assistant", reply);
        } else {
            const errorReply = "⚠️ I encountered an issue connecting to the didactic engine. Please check your network connection.";
            appendChatBubble("assistant", errorReply);
        }
        
    } catch (err) {
        if (spinner) spinner.style.display = "none";
        console.error("AI Communication error:", err);
        appendChatBubble("assistant", "⚠️ Server network communication error. Please try again.");
    }
    
    scrollChatHistoryToBottom();
}

function appendChatBubble(role, content) {
    const dialogView = document.getElementById("chat-conversation-history");
    if (!dialogView) return;
    
    const msgCard = document.createElement("div");
    msgCard.className = `chat-msg ${role === "user" ? "user" : "system"}`;
    
    // Render support for markdown-style bullet points or quotes in tutor output
    let formattedContent = content
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>")
        .replace(/&gt; "(.*?)"/g, `<blockquote>"$1"</blockquote>`)
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");
        
    msgCard.innerHTML = `
        <div class="msg-bubble">${formattedContent}</div>
    `;
    
    dialogView.appendChild(msgCard);
}

function scrollChatHistoryToBottom() {
    const dialogView = document.getElementById("chat-conversation-history");
    if (dialogView) {
        dialogView.scrollTop = dialogView.scrollHeight;
    }
}

// Responsive hamburger sidebar toggle for both desktop and mobile modes
function toggleSidebar() {
    const drawer = document.getElementById("sidebar-drawer");
    const overlay = document.getElementById("sidebar-shadow");
    
    if (window.innerWidth > 1024) {
        // Desktop Layout (screens > 1024px): Collapsible/expandable sidebar transitions
        document.body.classList.toggle("sidebar-collapsed");
        
        // Ensure mobile drawer state is clean when transitioning
        if (drawer && overlay) {
            drawer.classList.remove("open");
            overlay.classList.remove("open");
        }
    } else {
        // Mobile Layout (screens <= 1024px): Collapsing/expanding sidebar drawers with a dimmed overlay
        document.body.classList.remove("sidebar-collapsed");
        if (drawer && overlay) {
            drawer.classList.toggle("open");
            overlay.classList.toggle("open");
        }
    }
}