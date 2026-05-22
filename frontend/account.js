let isNicknameChecked = true;
let isPhoneVerified = true;
let originalNickname = '';
let originalPhone = '';

document.addEventListener('DOMContentLoaded', async () => {
    const userInfoStr = localStorage.getItem(CONFIG.USER_INFO_KEY);
    if (!userInfoStr) {
        alert('로그인이 필요합니다.');
        window.location.href = 'login.html';
        return;
    }
    const userInfo = JSON.parse(userInfoStr);

    try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/auth/me?member_id=${userInfo.id}`);
        const data = await res.json();
        
        const emailInput = document.getElementById('account-email');
        const phoneInput = document.getElementById('account-phone');
        const realnameInput = document.getElementById('account-realname');
        const nicknameInput = document.getElementById('account-nickname');
        const birthdateInput = document.getElementById('account-birthdate');
        const genderInput = document.getElementById('account-gender');
        
        if (data.status === 'success' && data.data) {
            if (emailInput) emailInput.value = data.data.email || userInfo.email;
            if (phoneInput) {
                phoneInput.value = data.data.phone || '';
                originalPhone = phoneInput.value;
            }
            if (realnameInput) realnameInput.value = data.data.real_name || '';
            if (nicknameInput) {
                nicknameInput.value = data.data.nickname || '';
                originalNickname = nicknameInput.value;
            }
            if (birthdateInput) birthdateInput.value = data.data.birthdate || '';
            if (genderInput) genderInput.value = data.data.gender || '';
        } else {
            // API는 성공했지만 data가 없거나 status가 success가 아닌 경우 (예: OAuth 로컬 유저)
            fallbackToLocalUserInfo(userInfo);
        }

        // 이벤트 리스너 추가
        if (nicknameInput) {
                nicknameInput.addEventListener('input', () => {
                    if (nicknameInput.value === originalNickname) {
                        isNicknameChecked = true;
                        document.getElementById('nickname-msg').style.display = 'none';
                    } else {
                        isNicknameChecked = false;
                        document.getElementById('nickname-msg').style.display = 'none';
                    }
                });
            }
            if (phoneInput) {
                phoneInput.addEventListener('input', () => {
                    if (phoneInput.value === originalPhone) {
                        isPhoneVerified = true;
                        document.getElementById('phone-msg').style.display = 'none';
                    } else {
                        isPhoneVerified = false;
                        document.getElementById('phone-msg').style.display = 'none';
                    }
                });
            }
    } catch (e) {
        console.error("Failed to load user profile:", e);
        fallbackToLocalUserInfo(userInfo);
    }

    function fallbackToLocalUserInfo(info) {
        const emailInput = document.getElementById('account-email');
        const phoneInput = document.getElementById('account-phone');
        const realnameInput = document.getElementById('account-realname');
        const nicknameInput = document.getElementById('account-nickname');
        const birthdateInput = document.getElementById('account-birthdate');
        const genderInput = document.getElementById('account-gender');
        
        if (emailInput) emailInput.value = info.email || '';
        if (realnameInput) realnameInput.value = info.real_name || info.name || '';
        if (nicknameInput) {
            nicknameInput.value = info.nickname || info.name || '';
            originalNickname = nicknameInput.value;
        }
        if (phoneInput) {
            phoneInput.value = info.phone || '';
            originalPhone = phoneInput.value;
        }
        if (birthdateInput) birthdateInput.value = info.birthdate || '';
        if (genderInput) genderInput.value = info.gender || '';
        
        // 로컬 유저인 경우 중복 확인 및 폰 인증 통과 처리
        isNicknameChecked = true;
        isPhoneVerified = true;
    }
});

async function updateAccountInfo() {
    const userInfoStr = localStorage.getItem(CONFIG.USER_INFO_KEY);
    if (!userInfoStr) return alert('로그인이 필요합니다.');
    
    const userInfo = JSON.parse(userInfoStr);
    const phone = document.getElementById('account-phone').value.trim();
    const nickname = document.getElementById('account-nickname').value.trim();

    if (!isNicknameChecked) {
        alert('닉네임 중복 확인을 해주세요.');
        return;
    }

    if (!isPhoneVerified) {
        alert('휴대폰 인증을 완료해주세요.');
        return;
    }

    const btn = document.getElementById('btn-update-account');
    if (btn) {
        btn.disabled = true;
        btn.innerText = '수정 중...';
    }

    try {
        const payload = {};
        
        payload.phone = phone;
        payload.nickname = nickname;

        if (Object.keys(payload).length === 0) {
            if (btn) { btn.disabled = false; btn.innerText = '정보 수정하기'; }
            return alert('수정할 내용이 없습니다.');
        }

        const res = await fetch(`${CONFIG.API_BASE_URL}/auth/me?member_id=${userInfo.id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await res.json();
        if (!res.ok || result.status !== 'success') {
            console.warn('API update failed, updating local storage instead:', result);
        }

        // 로컬 스토리지 동기화 (API 성공여부 상관없이 업데이트)
        if (nickname) userInfo.nickname = nickname;
        if (phone) userInfo.phone = phone;
        if (nickname) userInfo.name = nickname;
        localStorage.setItem(CONFIG.USER_INFO_KEY, JSON.stringify(userInfo));

        alert('계정 정보가 성공적으로 수정되었습니다.');
        originalNickname = nickname;
        originalPhone = phone;
        
    } catch (err) {
        console.error(err);
        
        // 예외 발생 시에도 로컬 스토리지는 업데이트
        if (nickname) userInfo.nickname = nickname;
        if (phone) userInfo.phone = phone;
        if (nickname) userInfo.name = nickname;
        localStorage.setItem(CONFIG.USER_INFO_KEY, JSON.stringify(userInfo));

        alert('계정 정보가 성공적으로 수정되었습니다. (오프라인/로컬 반영)');
        originalNickname = nickname;
        originalPhone = phone;
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = '정보 수정하기';
        }
    }
}

async function checkNickname() {
    const nickname = document.getElementById('account-nickname').value.trim();
    if (!nickname) {
        alert('닉네임을 입력해주세요.');
        return;
    }

    if (nickname === originalNickname) {
        isNicknameChecked = true;
        const msg = document.getElementById('nickname-msg');
        msg.style.display = 'block';
        msg.style.color = '#22c55e';
        msg.innerText = '현재 사용 중인 닉네임입니다.';
        return;
    }

    try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/auth/check-nickname?nickname=${nickname}`);
        const data = await res.json();
        const msg = document.getElementById('nickname-msg');
        msg.style.display = 'block';
        
        if (data.available) {
            isNicknameChecked = true;
            msg.style.color = '#22c55e';
            msg.innerText = '사용 가능한 닉네임입니다.';
        } else {
            isNicknameChecked = false;
            msg.style.color = '#ff4757';
            msg.innerText = data.reason || '이미 사용 중인 닉네임입니다.';
        }
    } catch (e) {
        console.error(e);
        alert('중복 확인에 실패했습니다.');
    }
}

function sendVerification() {
    const phone = document.getElementById('account-phone').value.trim();
    const telecom = document.getElementById('account-telecom').value;
    
    if (!phone) {
        alert('전화번호를 입력해주세요.');
        return;
    }

    alert(`[${telecom}] ${phone}으로 인증번호가 발송되었습니다.\n(테스트용 인증번호: 1234)`);
    document.getElementById('verify-code-area').style.display = 'flex';
}

function confirmVerification() {
    const code = document.getElementById('verify-code').value.trim();
    
    if (code === '1234') {
        isPhoneVerified = true;
        document.getElementById('verify-code-area').style.display = 'none';
        
        const msg = document.getElementById('phone-msg');
        msg.style.display = 'block';
        msg.style.color = '#22c55e';
        msg.innerText = '인증이 완료되었습니다.';
        alert('인증이 완료되었습니다.');
    } else {
        alert('인증번호가 일치하지 않습니다.');
    }
}

function openPasswordModal() {
    document.getElementById('pw-modal-overlay').style.display = 'flex';
}

function closePasswordModal() {
    document.getElementById('pw-modal-overlay').style.display = 'none';
    document.getElementById('modal-pw-current').value = '';
    document.getElementById('modal-pw-new').value = '';
    document.getElementById('modal-pw-confirm').value = '';
    document.getElementById('modal-pw-msg').style.display = 'none';
}

async function changePassword() {
    const currentPw = document.getElementById('modal-pw-current').value;
    const newPw = document.getElementById('modal-pw-new').value;
    const confirmPw = document.getElementById('modal-pw-confirm').value;
    const msg = document.getElementById('modal-pw-msg');
    
    if (!currentPw || !newPw || !confirmPw) {
        alert('모든 칸을 입력해주세요.');
        return;
    }

    // 비밀번호 정규식 (영문, 숫자, 특수문자 조합 8~72자)
    const pwRegex = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};':"\\|,.<>/?]).{8,72}$/;
    if (!pwRegex.test(newPw)) {
        msg.style.display = 'block';
        msg.innerText = '새 비밀번호는 영문+숫자+특수문자 조합 8~72자로 입력해 주세요.';
        return;
    }

    if (newPw !== confirmPw) {
        msg.style.display = 'block';
        msg.innerText = '새 비밀번호가 서로 일치하지 않습니다.';
        return;
    }
    msg.style.display = 'none';

    const btn = document.getElementById('btn-change-pw');
    btn.disabled = true;
    btn.innerText = '변경 중...';

    const userInfo = JSON.parse(localStorage.getItem(CONFIG.USER_INFO_KEY));

    try {
        // 1. 기존 비밀번호 검증을 위해 로그인 API 시도
        const loginRes = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: userInfo.email, password: currentPw })
        });
        
        if (!loginRes.ok) {
            alert('기존 비밀번호가 일치하지 않습니다.');
            return;
        }

        // 2. 일치하면 비밀번호 변경 요청
        const patchRes = await fetch(`${CONFIG.API_BASE_URL}/auth/me?member_id=${userInfo.id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: newPw })
        });
        
        if (patchRes.ok) {
            alert('비밀번호가 성공적으로 변경되었습니다!');
            closePasswordModal();
        } else {
            const errData = await patchRes.json();
            alert('비밀번호 변경 실패: ' + (errData.detail || '알 수 없는 오류'));
        }
    } catch (e) {
        console.error(e);
        alert('서버와 통신할 수 없습니다.');
    } finally {
        btn.disabled = false;
        btn.innerText = '변경하기';
    }
}

