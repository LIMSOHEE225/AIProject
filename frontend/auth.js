document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.querySelector('.auth-form'); // signup.html과 login.html 모두 .auth-form 사용 중

    if (!signupForm) return;

    // 이메일 중복 확인 로직 추가
    // 이메일 중복 확인 로직
    const emailInput = document.getElementById('email-input');
    const btnCheckEmail = document.getElementById('btn-check-email');
    const emailMsg = document.getElementById('email-msg');
    const emailContainer = document.getElementById('email-group-container');

    if (btnCheckEmail && emailInput) {
        btnCheckEmail.addEventListener('click', async () => {
            const email = emailInput.value;
            if (!email) {
                alert("이메일을 입력해 주세요.");
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                emailMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> *올바른 이메일 형식이 아닙니다.';
                emailMsg.className = "status-msg error";
                emailMsg.style.display = "block";
                return;
            }

            try {
                const response = await fetch(`${CONFIG.API_BASE_URL}/auth/check-email?email=${encodeURIComponent(email)}`);
                const result = await response.json();

                if (response.ok) {
                    if (result.available) {
                        emailMsg.innerHTML = '<i class="fa-solid fa-circle-check"></i> 사용 가능한 이메일입니다.';
                        emailMsg.className = "status-msg success";
                        emailMsg.style.display = "block";
                        emailContainer.classList.add('success');
                    } else {
                        emailMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> *이미 사용 중인 이메일입니다.';
                        emailMsg.className = "status-msg error";
                        emailMsg.style.display = "block";
                        emailContainer.classList.remove('success');
                    }
                } else {
                    // API 에러 발생 (400, 500 등)
                    emailMsg.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> *${result.detail || "오류가 발생했습니다."}`;
                    emailMsg.className = "status-msg error";
                    emailMsg.style.display = "block";
                    emailContainer.classList.remove('success');
                }
            } catch (error) {
                emailMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> *서버와 통신 중 오류가 발생했습니다.';
                emailMsg.className = "status-msg error";
                emailMsg.style.display = "block";
            }
        });

        emailInput.addEventListener('input', () => {
            emailMsg.style.display = "none";
            emailContainer.classList.remove('success');
        });
    }

    // 닉네임 중복 확인 로직 추가
    const nicknameInput = document.getElementById('nickname-input');
    const btnCheckNickname = document.getElementById('btn-check-nickname');
    const nicknameMsg = document.getElementById('nickname-msg');
    const nicknameContainer = document.getElementById('nickname-group-container');

    if (btnCheckNickname && nicknameInput) {
        btnCheckNickname.addEventListener('click', async () => {
            const nickname = nicknameInput.value;
            if (!nickname) {
                alert("닉네임을 입력해 주세요.");
                return;
            }

            if (nickname.length < 2) {
                nicknameMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> *닉네임은 2자 이상 입력해 주세요.';
                nicknameMsg.className = "status-msg error";
                nicknameMsg.style.display = "block";
                return;
            }

            try {
                const response = await fetch(`${CONFIG.API_BASE_URL}/auth/check-nickname?nickname=${encodeURIComponent(nickname)}`);
                const result = await response.json();

                if (response.ok) {
                    if (result.available) {
                        nicknameMsg.innerHTML = '<i class="fa-solid fa-circle-check"></i> 사용 가능한 닉네임입니다.';
                        nicknameMsg.className = "status-msg success";
                        nicknameMsg.style.display = "block";
                        nicknameContainer.classList.add('success');
                    } else {
                        nicknameMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> *이미 사용 중인 닉네임입니다.';
                        nicknameMsg.className = "status-msg error";
                        nicknameMsg.style.display = "block";
                        nicknameContainer.classList.remove('success');
                    }
                } else {
                    // API 에러 발생
                    nicknameMsg.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> *${result.detail || "오류가 발생했습니다."}`;
                    nicknameMsg.className = "status-msg error";
                    nicknameMsg.style.display = "block";
                    nicknameContainer.classList.remove('success');
                }
            } catch (error) {
                nicknameMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> *서버와 통신 중 오류가 발생했습니다.';
                nicknameMsg.className = "status-msg error";
                nicknameMsg.style.display = "block";
            }
        });

        nicknameInput.addEventListener('input', () => {
            nicknameMsg.style.display = "none";
            nicknameContainer.classList.remove('success');
        });
    }

    // 비밀번호 유효성 검사 로직 추가
    const passwordInput = document.getElementById('password-input');
    const passwordConfirmInput = document.getElementById('password-confirm-input');
    const passwordMsg = document.getElementById('password-msg');
    const passwordConfirmMsg = document.getElementById('password-confirm-msg');

    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            const pw = passwordInput.value;
            // 영문, 숫자, 특수문자 조합 8~72자
            const pwRegex = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};':"\\|,.<>/?]).{8,72}$/;

            if (passwordMsg) {
                if (pw.length === 0) {
                    passwordMsg.style.display = "none";
                } else if (!pwRegex.test(pw)) {
                    passwordMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> 영문+숫자+특수문자 조합 8~72자로 입력해 주세요.';
                    passwordMsg.className = "status-msg error";
                    passwordMsg.style.display = "block";
                } else {
                    passwordMsg.innerHTML = '<i class="fa-solid fa-circle-check"></i> 안전한 비밀번호입니다.';
                    passwordMsg.className = "status-msg success";
                    passwordMsg.style.display = "block";
                }
            }

            // 비밀번호 확인 칸도 같이 체크
            checkPasswordMatch();
        });
    }

    if (passwordConfirmInput) {
        passwordConfirmInput.addEventListener('input', checkPasswordMatch);
    }

    function checkPasswordMatch() {
        if (!passwordConfirmInput || !passwordInput) return;

        const pw = passwordInput.value;
        const pwConfirm = passwordConfirmInput.value;

        if (passwordConfirmMsg) {
            if (pwConfirm.length === 0) {
                passwordConfirmMsg.style.display = "none";
            } else if (pw !== pwConfirm) {
                passwordConfirmMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> 비밀번호가 일치하지 않습니다.';
                passwordConfirmMsg.className = "status-msg error";
                passwordConfirmMsg.style.display = "block";
            } else {
                passwordConfirmMsg.innerHTML = '<i class="fa-solid fa-circle-check"></i> 비밀번호가 일치합니다.';
                passwordConfirmMsg.className = "status-msg success";
                passwordConfirmMsg.style.display = "block";
            }
        }
    }

    const birthdateInput = document.getElementById('birthdate-input');
    const phoneGroup = document.getElementById('phone-verification-group');
    const btnSignupSubmit = document.getElementById('btn-signup-submit');

    // 만 14세 미만 관련 상태
    let isParentalConsented = false;
    let isUnder14 = false;

    const btnPhoneVerify = document.getElementById('btn-phone-verify');
    const phoneMsg = document.getElementById('phone-msg');
    const smsCodeGroup = document.getElementById('sms-code-group');
    const btnSmsConfirm = document.getElementById('btn-sms-confirm');
    const smsCodeInput = document.getElementById('sms-code-input');
    const smsTimer = document.getElementById('sms-timer');
    let isPhoneVerified = false;
    let timerInterval;

    const originalSubmitBtnColor = btnSignupSubmit ? getComputedStyle(btnSignupSubmit).backgroundColor : '';
    const greenColor = '#03C75A'; // 네이버 그린 스타일

    function updateSubmitButtonState() {
        if (!btnSignupSubmit) return;

        if (isUnder14 && !isParentalConsented) {
            btnSignupSubmit.innerText = "보호자인증";
            btnSignupSubmit.style.backgroundColor = greenColor;
        } else {
            btnSignupSubmit.innerText = "회원가입 완료";
            btnSignupSubmit.style.backgroundColor = ''; // CSS 기본값으로 복구
        }
    }

    if (btnPhoneVerify) {
        btnPhoneVerify.addEventListener('click', () => {
            const phone = document.getElementById('phone-input').value;
            const telecom = document.getElementById('telecom-select').value;

            if (!telecom) {
                alert("통신사를 선택해 주세요.");
                return;
            }
            if (!phone) {
                alert("휴대폰 번호를 입력해 주세요.");
                return;
            }

            // 1. 메시지 발송 시뮬레이션
            alert(`[${telecom}] ${phone} 번호로 인증번호가 발송되었습니다.`);

            // 2. 입력칸 노출
            smsCodeGroup.style.display = 'block';
            btnPhoneVerify.innerText = "재발송";

            // 3. 타이머 시작 (3분)
            startTimer(180);
        });
    }

    if (btnSmsConfirm) {
        btnSmsConfirm.addEventListener('click', () => {
            const code = smsCodeInput.value;

            // 4. 확인 버튼 클릭 시 검증 (데모용: 123456)
            if (code === "123456") {
                alert("본인인증이 완료되었습니다.");
                isPhoneVerified = true;

                // 5. 하단에 인증되었습니다 문구 노출 및 UI 정리
                phoneMsg.innerHTML = '<i class="fa-solid fa-circle-check"></i> 본인인증이 완료되었습니다.';
                phoneMsg.className = "status-msg success";
                phoneMsg.style.display = "block";

                smsCodeGroup.style.display = 'none';
                btnPhoneVerify.disabled = true;
                btnPhoneVerify.innerText = "인증완료";
                clearInterval(timerInterval);
            } else {
                alert("인증번호가 일치하지 않습니다. (데모: 123456)");
            }
        });
    }

    function startTimer(seconds) {
        clearInterval(timerInterval);
        let timeLeft = seconds;

        timerInterval = setInterval(() => {
            const min = Math.floor(timeLeft / 60);
            const sec = timeLeft % 60;
            smsTimer.innerText = `남은 시간 ${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;

            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                smsTimer.innerText = "인증 시간이 만료되었습니다. 다시 시도해주세요.";
                btnSmsConfirm.disabled = true;
            }
            timeLeft--;
        }, 1000);
    }

    if (birthdateInput) {
        birthdateInput.addEventListener('change', () => {
            const birthdateValue = birthdateInput.value;
            if (!birthdateValue) return;

            const birthDate = new Date(birthdateValue);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }

            if (age < 14) {
                // 만 14세 미만
                isUnder14 = true;
                phoneGroup.style.display = 'none';

                // 휴대폰 번호 입력 필드 초기화 및 비필수화
                const telecomSelect = document.getElementById('telecom-select');
                const phoneInput = document.getElementById('phone-input');
                if (telecomSelect) telecomSelect.required = false;
                if (phoneInput) phoneInput.required = false;
                isPhoneVerified = false;
            } else {
                // 만 14세 이상
                isUnder14 = false;
                phoneGroup.style.display = 'block';

                const telecomSelect = document.getElementById('telecom-select');
                const phoneInput = document.getElementById('phone-input');
                if (telecomSelect) telecomSelect.required = true;
                if (phoneInput) phoneInput.required = true;
                isParentalConsented = false;
            }
            updateSubmitButtonState();
        });
    }

    signupForm.addEventListener('submit', async (e) => {
        // 만 14세 미만이고 아직 인증 전이라면 인증 절차 진행
        if (isUnder14 && !isParentalConsented) {
            e.preventDefault();
            if (confirm("만 14세 미만 회원은 보호자 동의가 필요합니다. 보호자 인증을 진행하시겠습니까?")) {
                setTimeout(() => {
                    alert("보호자 인증이 완료되었습니다.");
                    isParentalConsented = true;
                    updateSubmitButtonState(); // 버튼을 '회원가입 완료'로 변경
                }, 500);
            }
            return;
        }

        e.preventDefault();

        const isSignup = window.location.pathname.includes('signup.html');
        const submitBtn = signupForm.querySelector('button[type="submit"]');

        // 가입 시에만 유효성 검사 추가 확인
        if (isSignup) {
            const pw = passwordInput.value;
            const pwConfirm = passwordConfirmInput.value;
            const pwRegex = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};':"\\|,.<>/?]).{8,72}$/;

            if (!pwRegex.test(pw)) {
                alert("비밀번호 형식이 올바르지 않습니다.");
                passwordInput.focus();
                return;
            }
            if (pw !== pwConfirm) {
                alert("비밀번호가 일치하지 않습니다.");
                passwordConfirmInput.focus();
                return;
            }
        }

        // 폼 데이터 수집
        const formData = {
            email: document.getElementById('email-input').value,
            password: document.getElementById('password-input').value,
        };

        if (isSignup) {
            formData.nickname = document.getElementById('nickname-input')?.value;
            formData.real_name = document.getElementById('realname-input')?.value || '사용자';
            formData.birthdate = document.getElementById('birthdate-input')?.value || null;
            formData.gender = document.getElementById('gender-select')?.value || null;

            if (!isUnder14) {
                if (!isPhoneVerified) {
                    alert("휴대폰 본인인증이 필요합니다.");
                    return;
                }
                formData.telecom = document.getElementById('telecom-select')?.value || null;
                formData.phone = document.getElementById('phone-input')?.value || null;
            } else {
                if (!isParentalConsented) {
                    alert("보호자 인증이 필요합니다.");
                    return;
                }
                formData.parental_consent = true;
            }

            formData.bio = document.getElementById('bio-input')?.value || null;
        }

        try {
            submitBtn.disabled = true;
            submitBtn.innerText = isSignup ? "가입 처리 중..." : "로그인 중...";

            const endpoint = isSignup ? "/auth/signup" : "/auth/login";
            const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "오류가 발생했습니다.");
            }

            if (isSignup) {
                // 가입 성공 시 토큰과 유저 정보 저장 (자동 로그인)
                if (result.access_token) {
                    localStorage.setItem(CONFIG.AUTH_TOKEN_KEY, result.access_token);
                }
                if (result.user) {
                    localStorage.setItem(CONFIG.USER_INFO_KEY, JSON.stringify(result.user));
                }

                alert("회원가입이 완료되었습니다! 톡지트에 오신 것을 환영합니다.");
                window.location.href = 'index.html';
            } else {
                localStorage.setItem(CONFIG.AUTH_TOKEN_KEY, result.access_token);
                localStorage.setItem(CONFIG.USER_INFO_KEY, JSON.stringify(result.user));

                alert("로그인되었습니다.");
                window.location.href = 'index.html';
            }

        } catch (error) {
            alert(error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = isSignup ? "가입하기" : "로그인";
        }
    });
});
