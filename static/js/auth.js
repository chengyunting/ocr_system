// // 登录表单提交处理
// document.getElementById('loginForm').addEventListener('submit', async (e) => {
//     e.preventDefault();
//
//     const formData = new FormData(e.target);
//
//     const response = await fetch('/login', {
//         method: 'POST',
//         body: formData
//     });
//
//     if (response.redirected) {
//         window.location.href = response.url;
//     } else {
//         const data = await response.json();
//         if (data.error_type === 'user_not_found') {
//             new bootstrap.Modal(document.getElementById('userNotRegisteredModal')).show();
//         } else if (data.error_type === 'wrong_password') {
//             alert(data.message);
//         }
//     }
// });
//
// // 注册表单提交处理
// document.getElementById('registerForm').addEventListener('submit', async (e) => {
//     e.preventDefault();
//
//     const formData = new FormData(e.target);
//
//     // 前端验证密码一致性
//     if (formData.get('password') !== formData.get('confirm_password')) {
//         alert('两次输入的密码不一致！');
//         return;
//     }
//
//     const response = await fetch('/register', {
//         method: 'POST',
//         body: formData
//     });
//
//     if (response.redirected) {
//         window.location.href = response.url;
//     } else {
//         const data = await response.json();
//         if (data.error_type === 'user_exists') {
//             new bootstrap.Modal(document.getElementById('userExistsModal')).show();
//         }
//     }
// });
