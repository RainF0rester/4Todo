<template>
  <a-config-provider :theme="antdTheme">
    <a-layout style="min-height:100vh;background:#f5f7fb">
    <!-- Top Nav -->
    <a-layout-header v-if="showHeader" class="topbar">
      <div class="brand" @click="homePage">Task Tracker</div>
      <a-menu mode="horizontal" :selectedKeys="[activeKey]" class="topmenu" @click="onMenuClick">
        <a-menu-item key="/list">List</a-menu-item>
        <a-menu-item key="/dashboard">Dashboard</a-menu-item>
        <a-menu-item key="/calendar">Calendar</a-menu-item>
        <a-menu-item key="/pomodoro" disabled>Pomodoro</a-menu-item>
      </a-menu>

      <div class="right">
        <div v-if="!isGuest">
          <a-dropdown>
            <a class="user" @click.prevent>
              <a-avatar size="small">{{ userInitial }}</a-avatar>
            </a>
            <template #overlay>
              <a-menu @click="onMenuClick">
                <a-menu-item key="profile">Profile</a-menu-item>
                <a-menu-item key="settings">Settings</a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout">Logout</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
        <div v-else>
          <div class="auth-buttons">
            <a-button type="primary" @click="goToLogin">Login</a-button>
            <a-button @click="goToRegister">Register</a-button>
          </div>
        </div>
      </div>
    </a-layout-header>

    <!-- Page Content -->
    <a-layout-content :class="['content', { centered: !showHeader }]">
      <router-view />
    </a-layout-content>
    </a-layout>
  </a-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFontFamilyToken, getFontSizeToken, getThemeColor, initUiSettings, resetUiThemeToDefault, uiSettings } from './stores/uiSettings'

const route = useRoute()
const router = useRouter()
initUiSettings()

const activeKey = computed(() => route.path)
const showHeader = computed(() => route.path !== '/auth')
const isGuest = computed(() => {
  void route.path
  const hasToken = !!localStorage.getItem('authToken')
  const guestMode = !!localStorage.getItem('authGuest')
  return guestMode || !hasToken
})
const userInitial = computed(() => {
  void route.path
  const email = localStorage.getItem('authEmail') || ''
  return email.trim().charAt(0).toUpperCase() || 'B'
})

const antdTheme = computed(() => ({
  token: {
    colorPrimary: getThemeColor(uiSettings.theme),
    fontSize: getFontSizeToken(uiSettings.fontSize),
    fontFamily: getFontFamilyToken(uiSettings.fontType),
  },
}))


function goToRegister() {
  localStorage.removeItem('authGuest')
  router.push({ path: '/auth', query: { mode: 'register' } })
  console.log('Redirecting to auth page for registration...')
}
function goToLogin() {
  localStorage.removeItem('authGuest')
  router.push({ path: '/auth', query: { mode: 'login' } })
  console.log('Redirecting to auth page for login...')
}
function homePage() {
  router.push('/home')
}

function onMenuClick({ key }) {
  console.log('Logged out, redirecting to auth page...')

  if (key === 'logout') {
    localStorage.removeItem('authToken')
    localStorage.removeItem('authGuest')
    localStorage.removeItem('authEmail')
    resetUiThemeToDefault()
    router.push('/auth')
    return
  }
  if (key === 'settings') {
    router.push('/settings')
    return
  }
  router.push(key)
}
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--app-surface, #ffffff);
  border-bottom: 1px solid var(--app-border, #eef0f3);
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 20px;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text, #1f2937);
  cursor: pointer;
  white-space: nowrap;
}

.topmenu {
  flex: 1;
  min-width: 0;
  border-bottom: none;
}

.right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search {
  width: 260px;
  border-radius: 999px;
}

.user {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--app-text, #1f2937);
}

.user :deep(.ant-avatar-sm) {
  width: 30px;
  height: 30px;
  line-height: 28px;
  border: 1px solid var(--app-border, #eef0f3);
}


.name {
  font-size: 14px;
}

.content {
  padding: 24px;
  color: var(--app-text, #1f2937);
}

.auth-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  align-items: center;
}

.content.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 0px);
}
</style>