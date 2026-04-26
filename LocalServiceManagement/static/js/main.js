/**
 * LocalServices Main JavaScript File
 * Handles Chatbot, Live Search, and other global logic.
 */

document.addEventListener('DOMContentLoaded', function() {
    // ---------------------------------------------------------
    // 1. CHATBOT LOGIC
    // ---------------------------------------------------------
    const toggle = document.getElementById('chatbot-toggle');
    const panel = document.getElementById('chatbot-panel');
    const closeBtn = document.getElementById('chatbot-close');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messagesDiv = document.getElementById('chatbot-messages');
    const suggestionsDiv = document.getElementById('chatbot-suggestions');

    if (toggle && panel && closeBtn) {
        toggle.onclick = function(e) {
            e.stopPropagation();
            panel.classList.toggle('active');
            if (panel.classList.contains('active')) {
                input.focus();
                loadSuggestions();
            }
        };

        closeBtn.onclick = function(e) {
            e.stopPropagation();
            panel.classList.remove('active');
            panel.style.display = 'none'; // Force hide
            // Reset for next toggle
            setTimeout(() => { panel.style.display = ''; }, 100);
        };

        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                sendChatbotMessage(input.value);
                input.value = '';
            });
        }
    }

    function loadSuggestions() {
        if (!suggestionsDiv) return;
        fetch('/chatbot/suggestions/')
            .then(r => r.json())
            .then(data => {
                suggestionsDiv.innerHTML = '';
                if (data.suggestions) {
                    data.suggestions.forEach(s => {
                        const btn = document.createElement('button');
                        btn.className = 'chatbot-suggestion-btn';
                        btn.textContent = s.text;
                        btn.addEventListener('click', () => sendChatbotMessage(s.action));
                        suggestionsDiv.appendChild(btn);
                    });
                }
            })
            .catch(err => console.error('Error loading suggestions:', err));
    }

    function appendChatbotMessage(text, sender) {
        if (!messagesDiv) return;
        const div = document.createElement('div');
        div.className = 'chatbot-msg ' + sender;
        const bubble = document.createElement('div');
        bubble.className = 'chatbot-bubble';
        bubble.textContent = text;
        div.appendChild(bubble);
        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function showChatbotTyping() {
        if (!messagesDiv) return;
        const div = document.createElement('div');
        div.className = 'chatbot-msg bot';
        div.id = 'typing-indicator';
        div.innerHTML = '<div class="chatbot-typing"><span></span><span></span><span></span></div>';
        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function removeChatbotTyping() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    function sendChatbotMessage(text) {
        if (!text.trim() || !messagesDiv) return;
        appendChatbotMessage(text, 'user');
        if (suggestionsDiv) suggestionsDiv.innerHTML = '';
        showChatbotTyping();

        fetch('/chatbot/message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ message: text }),
        })
        .then(r => r.json())
        .then(data => {
            removeChatbotTyping();
            appendChatbotMessage(data.response || 'Sorry, something went wrong.', 'bot');
        })
        .catch(() => {
            removeChatbotTyping();
            appendChatbotMessage('Connection error. Please try again.', 'bot');
        });
    }

    function getCookie(name) {
        let val = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(c => {
                c = c.trim();
                if (c.substring(0, name.length + 1) === (name + '=')) {
                    val = decodeURIComponent(c.substring(name.length + 1));
                }
            });
        }
        return val;
    }

    // ---------------------------------------------------------
    // 2. LIVE SEARCH LOGIC
    // ---------------------------------------------------------
    const searchInput = document.getElementById('searchInput');
    const liveSuggestions = document.getElementById('liveSuggestions');
    const suggestionList = document.getElementById('suggestionList');

    if (searchInput && liveSuggestions && suggestionList) {
        let timeout = null;

        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            const query = this.value.trim();

            if (query.length < 2) {
                liveSuggestions.style.display = 'none';
                return;
            }

            timeout = setTimeout(() => {
                fetch(`/services/search-suggestions/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        suggestionList.innerHTML = '';
                        if (data.results && data.results.length > 0) {
                            data.results.forEach(item => {
                                const li = document.createElement('li');
                                li.className = 'list-group-item list-group-item-action d-flex align-items-center gap-3';
                                li.style.cursor = 'pointer';
                                
                                const imgHtml = item.image 
                                    ? `<img src="${item.image}" style="width:40px; height:40px; border-radius:8px; object-fit:cover;">`
                                    : `<div style="width:40px; height:40px; border-radius:8px; background:#f1f5f9; display:flex; align-items:center; justify-content:center;"><i class="fa-solid fa-image text-muted"></i></div>`;
                                
                                li.innerHTML = `
                                    ${imgHtml}
                                    <div>
                                        <h6 class="mb-0 fw-bold">${item.name}</h6>
                                        <small class="text-muted">${item.category}</small>
                                    </div>
                                    <div class="ms-auto fw-bold text-primary">₹${item.price}</div>
                                `;
                                
                                li.addEventListener('click', () => {
                                    window.location.href = item.url;
                                });
                                
                                suggestionList.appendChild(li);
                            });
                            liveSuggestions.style.display = 'block';
                        } else {
                            liveSuggestions.style.display = 'none';
                        }
                    })
                    .catch(err => {
                        console.error("Live search error:", err);
                        liveSuggestions.style.display = 'none';
                    });
            }, 300);
        });

        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !liveSuggestions.contains(e.target)) {
                liveSuggestions.style.display = 'none';
            }
        });
    }

    // ---------------------------------------------------------
    // 3. SERVICE CHAT LOGIC (chat.html)
    // ---------------------------------------------------------
    const serviceChatBox = document.getElementById('chat-box');
    const serviceChatForm = document.getElementById('chatForm');
    const serviceMsgInput = document.getElementById('message-input');
    
    if (serviceChatBox && serviceChatForm && serviceMsgInput) {
        const roomIdInput = serviceChatForm.querySelector('input[name="room_id"]');
        const roomId = roomIdInput ? roomIdInput.value : null;
        let lastMsgId = 0;

        // Initialize lastMsgId from initial messages
        const initialMsgs = serviceChatBox.querySelectorAll('.chat-msg');
        if (initialMsgs.length > 0) {
            lastMsgId = parseInt(initialMsgs[initialMsgs.length - 1].getAttribute('data-msg-id')) || 0;
        }

        function scrollServiceChatBottom() {
            serviceChatBox.scrollTop = serviceChatBox.scrollHeight;
        }
        scrollServiceChatBottom();

        serviceChatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const text = serviceMsgInput.value.trim();
            if (!text) return;

            const formData = new FormData(serviceChatForm);

            fetch('/chat/send/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.message) {
                    appendServiceMsg(data.message, data.timestamp, true, data.id);
                    serviceMsgInput.value = '';
                    if (data.id > lastMsgId) lastMsgId = data.id;
                }
            })
            .catch(err => console.error('Error sending message:', err));
        });

        function appendServiceMsg(text, time, isSelf, msgId) {
            const div = document.createElement('div');
            div.className = 'chat-msg ' + (isSelf ? 'chat-self' : 'chat-other');
            if (msgId) div.setAttribute('data-msg-id', msgId);
            div.innerHTML = `
                <div class="chat-bubble">
                    ${escapeHtml(text)}
                    <span class="chat-time">${time}</span>
                </div>`;
            serviceChatBox.appendChild(div);
            scrollServiceChatBottom();
        }

        function escapeHtml(str) {
            const d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        }

        if (roomId) {
            // Polling for new messages
            setInterval(() => {
                fetch(`/chat/fetch/${roomId}/?after=${lastMsgId}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.messages && data.messages.length > 0) {
                            data.messages.forEach(m => {
                                if (!m.is_self) {
                                    appendServiceMsg(m.message, m.timestamp, false, m.id);
                                }
                                if (m.id > lastMsgId) {
                                    lastMsgId = m.id;
                                }
                            });
                        }
                    })
                    .catch(err => console.error('Error fetching messages:', err));
            }, 3000);
        }
    }

    // ---------------------------------------------------------
    // 4. REVIEW STAR RATING LOGIC
    // ---------------------------------------------------------
    const stars = document.querySelectorAll('.star-btn');
    const ratingInp = document.getElementById('rating-value');
    const hint = document.getElementById('star-hint');
    const submitBtn = document.getElementById('submit-btn');
    
    if (stars.length > 0 && ratingInp && hint && submitBtn) {
        let currentRating = 0;
        const labels = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent!'];

        function setStars(n) {
            stars.forEach((s, idx) => {
                s.classList.toggle('active', idx < n);
            });
            hint.textContent = n ? labels[n] : 'Click a star to rate';
            ratingInp.value  = n || '';
            submitBtn.disabled = (n === 0);
        }

        stars.forEach((btn, idx) => {
            btn.addEventListener('mouseenter', () => setStars(idx + 1));
            btn.addEventListener('mouseleave', () => setStars(currentRating));
            btn.addEventListener('click', () => {
                currentRating = idx + 1;
                setStars(currentRating);
            });
        });
    }

    // --- 11. Booking Date Picker ---
    const bookingDateInput = document.querySelector('#booking_date');
    if (bookingDateInput) {
        flatpickr(bookingDateInput, {
            dateFormat: "Y-m-d",
            minDate: "today",
            disableMobile: "true", // Force custom picker on mobile
        });
    }
});
