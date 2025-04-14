// main.js - HTMX関連とユーティリティ関数

document.addEventListener('DOMContentLoaded', function() {
    // ナビゲーションのアクティブ状態の設定
    setActiveNavigation();
    
    // フォームバリデーション
    setupFormValidation();
    
    // ファイルアップロードプレビュー
    setupFileUploadPreview();
    
    // HTMXイベントハンドラ
    setupHtmxEventHandlers();
    
    // モバイルメニュートグル
    setupMobileMenu();
  });
  
  // 現在のURLに基づいてナビゲーションのアクティブ状態を設定
  function setActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
      const linkPath = link.getAttribute('href');
      if (linkPath === currentPath || 
          (linkPath !== '/' && currentPath.startsWith(linkPath))) {
        link.classList.add('text-blue-600', 'font-medium');
        link.classList.remove('text-gray-600');
      }
    });
  }
  
  // フォームバリデーション
  function setupFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
      form.addEventListener('submit', function(event) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');
                      // エラーメッセージの表示
          const errorMsg = field.nextElementSibling;
          if (errorMsg && errorMsg.classList.contains('field-error')) {
            errorMsg.textContent = 'この項目は必須です';
          } else {
            const newError = document.createElement('p');
            newError.className = 'field-error';
            newError.textContent = 'この項目は必須です';
            field.parentNode.insertBefore(newError, field.nextSibling);
          }
        } else {
          field.classList.remove('border-red-500');
          const errorMsg = field.nextElementSibling;
          if (errorMsg && errorMsg.classList.contains('field-error')) {
            errorMsg.textContent = '';
          }
        }
      });
      
      if (!isValid) {
        event.preventDefault();
      }
    });
  });
}

// ファイルアップロードプレビュー
function setupFileUploadPreview() {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  
  fileInputs.forEach(input => {
    const previewContainer = document.getElementById(input.dataset.preview);
    if (!previewContainer) return;
    
    input.addEventListener('change', function() {
      previewContainer.innerHTML = '';
      
      if (this.files && this.files.length > 0) {
        for (let i = 0; i < this.files.length; i++) {
          const file = this.files[i];
          
          // ファイルサイズのフォーマット
          let fileSize;
          if (file.size < 1024) {
            fileSize = file.size + ' bytes';
          } else if (file.size < 1024 * 1024) {
            fileSize = Math.round(file.size / 1024) + ' KB';
          } else {
            fileSize = Math.round(file.size / (1024 * 1024) * 10) / 10 + ' MB';
          }
          
          // プレビューアイテムの作成
          const fileItem = document.createElement('div');
          fileItem.className = 'flex justify-between items-center p-2 bg-gray-50 rounded-md mb-2';
          
          fileItem.innerHTML = `
            <div class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span class="text-sm font-medium">${file.name}</span>
              <span class="text-xs text-gray-500 ml-2">(${fileSize})</span>
            </div>
            <button type="button" class="text-red-500 hover:text-red-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          `;
          
          // 削除ボタンのイベントハンドラ
          const deleteButton = fileItem.querySelector('button');
          deleteButton.addEventListener('click', function() {
            fileItem.remove();
            
            // FileListは直接操作できないため、DataTransferオブジェクトを使用
            const dt = new DataTransfer();
            for (let j = 0; j < input.files.length; j++) {
              if (j !== i) {
                dt.items.add(input.files[j]);
              }
            }
            input.files = dt.files;
          });
          
          previewContainer.appendChild(fileItem);
        }
      }
    });
  });
}

// HTMXイベントハンドラ
function setupHtmxEventHandlers() {
  // HTMXリクエスト開始時
  document.body.addEventListener('htmx:beforeRequest', function(event) {
    // ボタンのローディング状態を設定
    const triggerElement = event.detail.elt;
    if (triggerElement.tagName === 'BUTTON' || 
        (triggerElement.tagName === 'A' && triggerElement.classList.contains('btn'))) {
      
      // 元のテキストを保存
      triggerElement.dataset.originalText = triggerElement.innerHTML;
      
      // ローディングスピナーを追加
      triggerElement.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        処理中...
      `;
      
      // 無効化
      triggerElement.disabled = true;
    }
  });
  
  // HTMXリクエスト完了時
  document.body.addEventListener('htmx:afterRequest', function(event) {
    // ボタンの状態を元に戻す
    const triggerElement = event.detail.elt;
    if (triggerElement.tagName === 'BUTTON' || 
        (triggerElement.tagName === 'A' && triggerElement.classList.contains('btn'))) {
      
      // 元のテキストを復元
      if (triggerElement.dataset.originalText) {
        triggerElement.innerHTML = triggerElement.dataset.originalText;
        delete triggerElement.dataset.originalText;
      }
      
      // 有効化
      triggerElement.disabled = false;
    }
  });
  
  // HTMXレスポンスエラー時
  document.body.addEventListener('htmx:responseError', function(event) {
    console.error('HTMX Response Error:', event.detail);
    
    // エラーメッセージの表示
    const errorMessage = document.createElement('div');
    errorMessage.className = 'fixed bottom-4 right-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-md';
    errorMessage.innerHTML = `
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm">エラーが発生しました。もう一度お試しください。</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button class="inline-flex bg-red-100 text-red-500 rounded-md p-1.5 hover:bg-red-200 focus:outline-none" onclick="this.parentNode.parentNode.parentNode.parentNode.remove()">
              <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(errorMessage);
    
    // 5秒後に自動的に消える
    setTimeout(() => {
      errorMessage.remove();
    }, 5000);
  });
  
  // HTMXスワップ後
  document.body.addEventListener('htmx:afterSwap', function(event) {
    // モーダルが追加された場合、自動的にフォーカスを設定
    const modal = event.detail.target.querySelector('[role="dialog"]');
    if (modal) {
      const focusElement = modal.querySelector('input, button, [tabindex="0"]');
      if (focusElement) {
        focusElement.focus();
      }
    }
  });
}

// モバイルメニュートグル
function setupMobileMenu() {
  const menuToggle = document.getElementById('mobile-menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', function() {
      mobileMenu.classList.toggle('hidden');
    });
  }
  
  // 画面外クリックでメニューを閉じる
  document.addEventListener('click', function(event) {
    if (menuToggle && mobileMenu && !mobileMenu.classList.contains('hidden')) {
      if (!menuToggle.contains(event.target) && !mobileMenu.contains(event.target)) {
        mobileMenu.classList.add('hidden');
      }
    }
  });
}

// 通知表示関数
function showNotification(message, type = 'success') {
  const notification = document.createElement('div');
  const typeClasses = {
    'success': 'bg-green-100 border-green-500 text-green-700',
    'error': 'bg-red-100 border-red-500 text-red-700',
    'warning': 'bg-yellow-100 border-yellow-500 text-yellow-700',
    'info': 'bg-blue-100 border-blue-500 text-blue-700'
  };
  
  notification.className = `fixed bottom-4 right-4 ${typeClasses[type]} border-l-4 p-4 rounded shadow-md animate-fade-in`;
  notification.innerHTML = `
    <div class="flex">
      <div class="ml-3">
        <p class="text-sm">${message}</p>
      </div>
      <div class="ml-auto pl-3">
        <div class="-mx-1.5 -my-1.5">
          <button class="inline-flex rounded-md p-1.5 focus:outline-none ${typeClasses[type]} hover:${type === 'success' ? 'bg-green-200' : type === 'error' ? 'bg-red-200' : type === 'warning' ? 'bg-yellow-200' : 'bg-blue-200'}" onclick="this.parentNode.parentNode.parentNode.parentNode.remove()">
            <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // 5秒後に自動的に消える
  setTimeout(() => {
    notification.classList.add('opacity-0');
    notification.style.transition = 'opacity 0.5s ease-in-out';
    
    // トランジション完了後に要素を削除
    setTimeout(() => {
      notification.remove();
    }, 500);
  }, 5000);
  
  return notification;
}

// 日付フォーマット
function formatDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(date);
}

// タイムスタンプをXX時間前などの相対時間に変換
function timeAgo(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffSec < 60) {
    return 'たった今';
  } else if (diffMin < 60) {
    return `${diffMin}分前`;
  } else if (diffHour < 24) {
    return `${diffHour}時間前`;
  } else if (diffDay < 7) {
    return `${diffDay}日前`;
  } else {
    return formatDate(dateString);
  }
}