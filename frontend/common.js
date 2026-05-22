document.addEventListener('DOMContentLoaded', () => {
    updateHeader();
    initFriendFeature();
});

function updateHeader() {
    const authNav = document.querySelector('.auth-nav');
    const adminLink = document.getElementById('admin-link');
    
    // 관리자 버튼 기본 숨김 처리
    if (adminLink) {
        adminLink.style.display = 'none';
    }

    if (!authNav) return;

    const userInfoStr = localStorage.getItem(CONFIG.USER_INFO_KEY);
    
    if (userInfoStr) {
        const userInfo = JSON.parse(userInfoStr);
        
        // 관리자 권한 확인 후 버튼 노출 (role은 user_metadata 내부에 저장됨)
        const userRole = userInfo.user_metadata?.role || '회원';
        if (adminLink && userRole === '관리자') {
            adminLink.style.display = 'inline-block';
        }
        
        const nickname = userInfo.user_metadata?.nickname || userInfo.email.split('@')[0];
        
        authNav.innerHTML = `
            <div class="user-profile-nav" style="display: flex; align-items: center; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span class="user-nickname" style="font-weight: 800; color: var(--text-main);">${nickname}님</span>
                    <a href="/account.html" title="마이페이지 (계정 정보 수정)" style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; background: var(--accent-primary); color: #fff; border-radius: 50%; text-decoration: none; font-size: 0.85rem; transition: 0.2s; box-shadow: 0 2px 5px rgba(124,58,237,0.3);"><i class="fa-solid fa-user"></i></a>
                </div>
                <span style="color: #ccc; font-size: 0.8rem;">|</span>
                <a href="/minihompy.html" target="_blank" class="user-link" style="text-decoration: none; font-weight: 700; color: #000; font-size: 0.9rem;">마이홈피</a>
                <span style="color: #ccc; font-size: 0.8rem;">|</span>
                <a href="/mypage.html" class="user-link" style="text-decoration: none; font-weight: 700; color: #000; font-size: 0.9rem;">내 캐릭터</a>
                <button onclick="handleLogout()" class="btn-text" style="padding: 5px 10px; font-size: 0.8rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; margin-left: 10px;">로그아웃</button>
            </div>
        `;

        // 편지/엽서 버튼 상태 업데이트 (이미 있으면 '바로가기'로 변경, 없으면 생성 페이지로)
        const createLink = document.getElementById('hp-create-link');
        if (createLink) {
            createLink.href = `/DearZit.html?member_id=${userInfo.id}`;
        }
        updateHomepageLink(userInfo.id);

    } else {
        // 로그인하지 않은 상태일 때 기본 버튼 표시
        authNav.innerHTML = `
            <a href="/login.html" class="btn-text" style="text-decoration: none;">로그인</a>
            <a href="/signup.html" class="btn-primary" style="text-decoration: none; display: inline-block;">회원가입</a>
        `;
    }
}

function initFriendFeature() {
    // 친구 목록 플로팅 버튼 추가 (모든 사용자에게 항상 표시)
    if (!document.querySelector('.friend-fab')) {
        const fab = document.createElement('button');
        fab.className = 'friend-fab';
        fab.innerHTML = '<i class="fa-solid fa-user-group"></i>';
        fab.title = '친구 목록';
        fab.onclick = () => {
            const userInfoStr = localStorage.getItem(CONFIG.USER_INFO_KEY);
            if (!userInfoStr) {
                alert('친구 목록을 이용하시려면 먼저 로그인해 주세요.');
                window.location.href = '/login.html';
                return;
            }
            toggleFriendPanel();
        };
        document.body.appendChild(fab);
        
        // 친구 목록 패널 미리 생성
        createFriendPanel();
    }
}

function createFriendPanel() {
    if (document.querySelector('.friend-panel')) return;

    const panel = document.createElement('div');
    panel.className = 'friend-panel';
    panel.innerHTML = `
        <div class="panel-header">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="btn-icon-header" onclick="showFriendList()" title="친구 목록"><i class="fa-solid fa-user-group"></i></button>
                <button class="btn-icon-header" onclick="showAllMembers()" title="친구 추가"><i class="fa-solid fa-plus"></i></button>
            </div>
            <h3 id="panel-title">친구 목록</h3>
            <button class="close-panel" onclick="toggleFriendPanel()">&times;</button>
        </div>
        <div id="friend-list-container" class="friend-list-content">
            <!-- 친구 목록이 여기에 렌더링됩니다. -->
        </div>
    `;
    document.body.appendChild(panel);
    showFriendList(); // 초기에는 친구 목록 표시
}

function showFriendList() {
    const title = document.getElementById('panel-title');
    if (title) title.innerText = '친구 목록';
    const container = document.getElementById('friend-list-container');
    if (!container) return;

    container.innerHTML = `
        <div style="padding: 30px 20px; text-align: center; color: #999; font-size: 0.9rem;">
            <i class="fa-solid fa-user-xmark" style="font-size: 2rem; color: #ddd; margin-bottom: 15px; display: block;"></i>
            아직 추가된 친구가 없습니다.<br>
            <span style="font-size: 0.8rem; margin-top: 5px; display: inline-block;">(친구 찾기를 통해 친구를 추가해보세요!)</span>
        </div>
    `;
}

async function showAllMembers() {
    const title = document.getElementById('panel-title');
    if (title) title.innerText = '회원 찾기';
    const container = document.getElementById('friend-list-container');
    if (!container) return;

    container.innerHTML = '<div style="padding: 20px; text-align: center;"><i class="fa-solid fa-spinner fa-spin"></i> 회원 목록 불러오는 중...</div>';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/auth/members`);
        const result = await response.json();
        
        if (result.status === 'success') {
            if (result.data.length === 0) {
                container.innerHTML = '<div style="padding: 20px; text-align: center;">등록된 회원이 없습니다.</div>';
                return;
            }
            
            container.innerHTML = result.data.map(member => `
                <div class="friend-item">
                    <div class="friend-avatar">${member.nickname ? member.nickname[0].toUpperCase() : '?'}</div>
                    <div class="friend-info">
                        <span class="friend-name">${member.nickname || '익명'}</span>
                        <span class="friend-status">${member.email}</span>
                    </div>
                    <div class="friend-actions">
                        <button class="btn-primary-sm" onclick="addFriend('${member.id}', '${member.nickname}')" style="padding: 5px 10px; font-size: 0.7rem; background: var(--accent-primary); color: #fff; border: none; font-weight: 800; cursor: pointer;">친구 추가</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error("회원 목록 조회 오류:", error);
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: red;">오류가 발생했습니다.</div>';
    }
}

function addFriend(id, nickname) {
    alert(`${nickname}님께 친구 요청을 보냈습니다. (기능 구현 중)`);
}

function openChat(friendName) {
    // 채팅창 UI 생성 및 표시
    if (!document.querySelector('.chat-window')) {
        createChatWindow();
    }
    const chatWindow = document.querySelector('.chat-window');
    chatWindow.querySelector('.chat-target-name').innerText = friendName;
    chatWindow.classList.add('active');
    
    // 친구 목록 패널 닫기 (선택 사항)
    // toggleFriendPanel();
}

function createChatWindow() {
    const chat = document.createElement('div');
    chat.className = 'chat-window';
    chat.innerHTML = `
        <div class="chat-header">
            <span class="chat-target-name">상대방</span>
            <button class="close-chat" onclick="closeChat()">&times;</button>
        </div>
        <div class="chat-messages-area">
            <div class="chat-bubble received">안녕하세요! 반갑습니다.</div>
            <div class="chat-bubble sent">네, 안녕하세요! 공간이 너무 멋지네요.</div>
        </div>
        <div class="chat-input-row">
            <input type="text" placeholder="메시지를 입력하세요...">
            <button class="btn-send-msg"><i class="fa-solid fa-paper-plane"></i></button>
        </div>
    `;
    document.body.appendChild(chat);
}

function closeChat() {
    const chat = document.querySelector('.chat-window');
    if (chat) chat.classList.remove('active');
}

function toggleFriendPanel() {
    const panel = document.querySelector('.friend-panel');
    if (panel) {
        panel.classList.toggle('active');
    }
}

async function updateHomepageLink(memberId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/homepage/me?member_id=${memberId}`);
        const result = await response.json();
        
        if (response.ok && result.status === 'success' && result.data) {
            // CSS를 이용하기 위해 body에 클래스 추가
            document.body.classList.add('user-has-homepage');
            
            // 바로가기 링크의 href 설정 (DearZit 우체국으로 바로 이동)
            const visitLinks = document.querySelectorAll('#hp-visit-link');
            visitLinks.forEach(link => {
                link.href = `/DearZit.html?member_id=${memberId}`;
            });
        }
    } catch (error) {
        console.error("편지함 정보 확인 오류:", error);
    }
}

function handleLogout() {
    if (confirm("로그아웃 하시겠습니까?")) {
        localStorage.removeItem(CONFIG.AUTH_TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_INFO_KEY);
        alert("로그아웃되었습니다.");
        window.location.reload();
    }
}
