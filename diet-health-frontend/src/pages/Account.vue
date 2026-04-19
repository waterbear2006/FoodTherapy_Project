<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUser, getJoinDays, clearAllUserData, updateUser } from '../utils/userStorage'

const router = useRouter()

// 用户信息
const user = ref({
  name: '',
  avatar: '',
  joinDays: 0
})

// 弹窗控制
const showConfirmModal = ref(false)
const confirmAction = ref(null)

onMounted(() => {
  const userData = getUser()
  user.value = {
    name: userData.name,
    avatar: userData.avatar,
    joinDays: getJoinDays()
  }
})

// 清除所有数据
function handleClearData() {
  confirmAction.value = 'clearData'
  showConfirmModal.value = true
}

// 重置用户信息
function handleResetUser() {
  confirmAction.value = 'resetUser'
  showConfirmModal.value = true
}

// 确认操作
function confirmActionHandler() {
  if (confirmAction.value === 'clearData') {
    clearAllUserData()
    alert('所有数据已清除！')
    router.push('/')
  } else if (confirmAction.value === 'resetUser') {
    const defaultUser = updateUser({
      name: '养生达人',
      avatar: '👤'
    })
    user.value = {
      name: defaultUser.name,
      avatar: defaultUser.avatar,
      joinDays: getJoinDays()
    }
    alert('用户信息已重置！')
  }
  showConfirmModal.value = false
}

// 取消操作
function cancelAction() {
  showConfirmModal.value = false
  confirmAction.value = null
}

// 返回上一页
function goBack() {
  router.back()
}
</script>

<template>
  <div class="page-account app-page">
    <header class="page-header">
      <button class="back-btn" @click="goBack">←</button>
      <h1 class="page-title">账号管理</h1>
      <div class="placeholder"></div>
    </header>

    <section class="account-section">
      <div class="user-card">
        <div class="avatar-wrap">
          <div class="avatar">{{ user.avatar || '👤' }}</div>
        </div>
        <div class="user-info">
          <h2 class="user-name">{{ user.name }}</h2>
          <p class="user-days">已加入 {{ user.joinDays }} 天</p>
        </div>
      </div>
    </section>

    <section class="settings-section">
      <h2 class="section-title">数据管理</h2>
      
      <div class="settings-list">
        <div class="settings-item" @click="handleResetUser">
          <div class="item-left">
            <span class="item-icon">🔄</span>
            <div class="item-content">
              <div class="item-title">重置用户信息</div>
              <div class="item-desc">恢复默认昵称和头像</div>
            </div>
          </div>
          <span class="item-arrow">›</span>
        </div>

        <div class="settings-item" @click="handleClearData">
          <div class="item-left">
            <span class="item-icon">🗑️</span>
            <div class="item-content">
              <div class="item-title">清除所有数据</div>
              <div class="item-desc">删除用户信息和健康档案</div>
            </div>
          </div>
          <span class="item-arrow">›</span>
        </div>
      </div>

      <div class="tips-box">
        <p class="tips-title">💡 温馨提示</p>
        <ul class="tips-list">
          <li>所有数据都存储在您的本地浏览器中</li>
          <li>清除数据后无法恢复，请谨慎操作</li>
          <li>更换浏览器或清除缓存会导致数据丢失</li>
        </ul>
      </div>
    </section>

    <!-- 确认弹窗 -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="cancelAction">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">确认操作</h3>
          <button class="modal-close" @click="cancelAction">×</button>
        </div>
        <div class="modal-body">
          <p v-if="confirmAction === 'clearData'" class="confirm-text">
            ⚠️ 确定要清除所有数据吗？<br/>
            此操作不可逆，用户信息和健康档案都将被删除！
          </p>
          <p v-else-if="confirmAction === 'resetUser'" class="confirm-text">
            确定要重置用户信息吗？<br/>
            昵称和头像将恢复为默认值。
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="cancelAction">取消</button>
          <button class="btn-confirm" @click="confirmActionHandler">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-account {
  background: var(--bg);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0 20px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-h);
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
}

.placeholder {
  width: 40px;
}

.account-section {
  margin-bottom: 24px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.avatar-wrap {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #fff8e7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar {
  font-size: 32px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 6px;
}

.user-days {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.settings-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 12px;
}

.settings-list {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: background 0.2s;
}

.settings-item:last-child {
  border-bottom: none;
}

.settings-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-icon {
  font-size: 24px;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-h);
}

.item-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.item-arrow {
  font-size: 24px;
  color: var(--text-muted);
}

.tips-box {
  margin-top: 20px;
  background: var(--primary-light);
  border-radius: var(--radius);
  padding: 16px;
  border-left: 4px solid var(--primary);
}

.tips-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-dark);
  margin: 0 0 8px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
}

.tips-list li {
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
  margin-bottom: 4px;
}

/* 确认弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-card);
  border-radius: var(--radius);
  width: 100%;
  max-width: 360px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.05);
}

.modal-body {
  padding: 24px 20px;
}

.confirm-text {
  font-size: 15px;
  color: var(--text);
  line-height: 1.6;
  margin: 0;
  text-align: center;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text);
}

.btn-cancel:hover {
  background: rgba(0, 0, 0, 0.1);
}

.btn-confirm {
  background: #ff4d4f;
  color: #fff;
}

.btn-confirm:hover {
  background: #ff7875;
}
</style>
