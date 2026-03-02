<template>
  <a-layout style="min-height:100vh;background:#f5f7fb">
    <!-- Top Nav -->
    <a-layout-header class="topbar">
      <div class="brand">Task Tracker</div>

      <a-menu
        mode="horizontal"
        :selectedKeys="[activeKey]"
        class="topmenu"
        @click="onMenuClick"
      >
        <a-menu-item key="/list">List</a-menu-item>
        <a-menu-item key="/calendar" disabled>Calendar</a-menu-item>
        <a-menu-item key="/dashboard" disabled>Dashboard</a-menu-item>
        <a-menu-item key="/pomodoro" disabled>Pomodoro</a-menu-item>
      </a-menu>

      <div class="right">
        <a-dropdown>
          <a class="user" @click.prevent>
            <a-avatar size="small">B</a-avatar>
            <span class="name">COMP9820</span>
          </a>
          <template #overlay>
            <a-menu>
              <a-menu-item key="profile">Profile</a-menu-item>
              <a-menu-item key="settings">Settings</a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout">Logout</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </a-layout-header>

    <!-- Page Content -->
    <a-layout-content class="content">
      <router-view />
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeKey = computed(() => route.path)

function onMenuClick({ key }) {
  router.push(key)
}
</script>

<style scoped>
.topbar{
  position: sticky;
  top: 0;
  z-index: 10;
  background: #ffffff;
  border-bottom: 1px solid #eef0f3;
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 20px;
}

.brand{
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  white-space: nowrap;
}

.topmenu{
  flex: 1;
  min-width: 0;
  border-bottom: none;
}

.right{
  display: flex;
  align-items: center;
  gap: 12px;
}

.search{
  width: 260px;
  border-radius: 999px;
}

.user{
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2937;
}

.name{
  font-size: 14px;
}

.content{
  padding: 24px;
}
</style>