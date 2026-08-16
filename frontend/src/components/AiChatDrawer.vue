<template>
  <!-- Floating Button -->
  <a-button type="primary" shape="circle" size="large" class="ai-fab" @click="open = true">
    <template #icon>
      <MessageOutlined />
    </template>
  </a-button>

  <!-- Drawer -->
  <a-drawer
    v-model:open="open"
    title="AI Assistant"
    placement="right"
    :width="400"
    :body-style="{ padding: 0, display: 'flex', flexDirection: 'column', height: '100%' }"
  >
    <!-- Message List -->
    <div class="msg-list" ref="msgListRef">
      <div v-if="messages.length === 0" class="msg-empty">
        Ask me anything about your tasks.
      </div>
      <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
        <div class="msg-bubble">{{ msg.content }}</div>
      </div>
      <!-- Thinking -->
      <div v-if="waiting" class="msg-row assistant">
        <div class="msg-bubble thinking">Thinking{{ dots }}</div>
      </div>
      <!-- Confirm Banner -->
      <div v-if="pendingConfirm" class="confirm-banner">
        <div class="confirm-text">
          <div class="confirm-title">{{ formatConfirmTitle(pendingConfirm.tool) }}</div>
          <div class="confirm-desc">{{ formatConfirmDesc(pendingConfirm.tool, pendingConfirm.input) }}</div>
        </div>
        <div class="confirm-actions">
          <a-button size="small" type="primary" @click="sendConfirm(true)">Confirm</a-button>
          <a-button size="small" @click="sendConfirm(false)">Cancel</a-button>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <a-textarea
        v-model:value="inputText"
        placeholder="Type a message..."
        :auto-size="{ minRows: 1, maxRows: 4 }"
        :disabled="waiting"
        @keydown.enter.exact="handleEnter"
      />
      <a-button type="primary" :disabled="waiting || !inputText.trim()" @click="send">
        <template #icon>
          <SendOutlined />
        </template>
      </a-button>
    </div>
  </a-drawer>
</template>

<script setup>
import { ref, nextTick, watch, onUnmounted } from 'vue'
import { MessageOutlined, SendOutlined } from '@ant-design/icons-vue'
import { io } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_WS_URL || 'http://localhost:5077'

const open = ref(false)
const inputText = ref('')
const waiting = ref(false)
const messages = ref([])
const pendingConfirm = ref(null)
const msgListRef = ref(null)
const dots = ref('')

let socket = null
let dotsTimer = null

function startDots() {
  const cycle = ['.', '..', '...']
  let i = 0
  dotsTimer = setInterval(() => {
    dots.value = cycle[i % 3]
    i++
  }, 500)
}

function stopDots() {
  clearInterval(dotsTimer)
  dotsTimer = null
  dots.value = ''
}

onUnmounted(() => {
  stopDots()
  disconnect()
})

function connect() {
  const token = localStorage.getItem('authToken')
  if (!token) return

  socket = io(SOCKET_URL, { transports: ['polling'] })

  socket.on('ai_reply', (data) => {
    stopDots()
    messages.value.push({ role: 'assistant', content: data.reply })
    waiting.value = false
    scrollToBottom()
  })

  socket.on('ai_error', (data) => {
    stopDots()
    messages.value.push({ role: 'assistant', content: `Error: ${data.error}` })
    waiting.value = false
    scrollToBottom()
  })

  socket.on('confirm_required', (data) => {
    pendingConfirm.value = { tool: data.tool, input: data.input }
    scrollToBottom()
  })

  socket.on('disconnect', () => {
    stopDots()
    waiting.value = false
    pendingConfirm.value = null
    if (open.value) {
      messages.value.push({ role: 'assistant', content: 'Connection lost. Please reopen the chat.' })
      scrollToBottom()
    }
  })
}

function disconnect() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

watch(open, (val) => {
  if (val) connect()
  else disconnect()
})

function scrollToBottom() {
  nextTick(() => {
    if (msgListRef.value) {
      msgListRef.value.scrollTop = msgListRef.value.scrollHeight
    }
  })
}

function handleEnter(e) {
  e.preventDefault()
  send()
}

function send() {
  const text = inputText.value.trim()
  if (!text || waiting.value || !socket) return
  messages.value.push({ role: 'user', content: text })
  waiting.value = true
  nextTick(() => { inputText.value = '' })
  startDots()
  scrollToBottom()
  socket.emit('ai_chat', {
    token: localStorage.getItem('authToken'),
    prompt: text,
  })
}

function formatConfirmTitle(tool) {
  const titles = {
    create_tasks: 'Create Tasks',
    complete_task: 'Complete Task',
    delete_task: 'Delete Task',
    update_task: 'Update Task',
  }
  return titles[tool] ?? tool
}

function formatConfirmDesc(tool, input) {
  if (tool === 'create_tasks') {
    const tasks = input.tasks ?? []
    return tasks.map(t => `• ${t.task_title}`).join('\n')
  }
  if (tool === 'complete_task') return `Mark "${input.task_title}" as done`
  if (tool === 'delete_task') return `Delete "${input.task_title}"`
  if (tool === 'update_task') {
    const changes = []
    if (input.new_title) changes.push(`Rename to "${input.new_title}"`)
    if (input.new_due) changes.push(`Due: ${input.new_due}`)
    if (input.new_level) changes.push(`Priority: ${input.new_level}`)
    if (input.new_description) changes.push(`Description updated`)
    return `"${input.task_title}"\n` + changes.map(c => `• ${c}`).join('\n')
  }
  return ''
}

function sendConfirm(confirmed) {
  pendingConfirm.value = null
  socket?.emit('confirm', { confirmed })
}
</script>

<style scoped>
.ai-fab {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 200;
}

.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.msg-empty {
  text-align: center;
  color: #aaa;
  margin-top: 40px;
  font-size: 14px;
}

.msg-row {
  display: flex;
}

.msg-row.user {
  justify-content: flex-end;
}

.msg-row.assistant {
  justify-content: flex-start;
}

.msg-bubble {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-row.user .msg-bubble {
  background: #1677ff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-row.assistant .msg-bubble {
  background: #f0f0f0;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.confirm-banner {
  border: 1px solid #faad14;
  border-radius: 8px;
  padding: 12px;
  background: #fffbe6;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.confirm-title {
  font-weight: 600;
  font-size: 13px;
  color: #d48806;
  margin-bottom: 4px;
}

.confirm-desc {
  font-size: 13px;
  color: #555;
  white-space: pre-wrap;
  line-height: 1.6;
}

.confirm-actions {
  display: flex;
  gap: 8px;
}

.input-area {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #eef0f3;
}

.input-area .ant-input {
  flex: 1;
}
</style>
