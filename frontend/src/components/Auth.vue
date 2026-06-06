<!-- The code on this page was generated with AI and then modified. -->
<template>
    <a-card class="auth-card">
        <div class="header">
            <h2>{{ mode === 'login' ? 'Login' : 'Register' }}</h2>
        </div>

        <a-form :layout="'vertical'" @submit.prevent>
            <a-form-item v-if="mode === 'register'" label="Username">
                <a-input v-model:value="username" @input="onUsernameInput" @blur="onUsernameBlur"
                    placeholder="Enter username" />
                <div v-if="errors.username" class="ant-form-item-explain">{{ errors.username }}</div>
            </a-form-item>

            <a-form-item label="Email">
                <a-input ref="emailInput" v-model:value="email" @input="onEmailInput" @blur="onEmailBlur"
                    placeholder="Enter Eemail" autocomplete="email" />
                <div v-if="errors.email" class="ant-form-item-explain">{{ errors.email }}</div>
            </a-form-item>

            <a-form-item label="Password">
                <a-input-password v-model:value="password" @input="onPasswordInput" @blur="onPasswordBlur"
                    placeholder="Password" autocomplete="current-password" />
                <div v-if="errors.password" class="ant-form-item-explain">{{ errors.password }}</div>
            </a-form-item>

            <a-form-item>
                <div class="actions">
                    <div class="primary-row">
                        <a-button class="primary-btn" type="primary" @click="handleSubmit" :loading="loading">
                            {{ mode === 'login' ? 'Login' : 'Register' }}
                        </a-button>
                    </div>
                    <div class="links-row">
                        <a-button type="link" html-type="button" @click.stop="toggleMode">
                            {{ mode === 'login' ? 'Create an account' : 'Already have an account? Login' }}
                        </a-button>
                        <a-button type="link" html-type="button" @click.stop="continueAsGuest">Continue as
                            Guest</a-button>
                    </div>
                </div>
            </a-form-item>
        </a-form>
    </a-card>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { addTask, saveGuestTasks } from '../api/tasks'
import { initUiSettings } from '../stores/uiSettings'

const router = useRouter()
const route = useRoute()
const emailInput = ref(null)
const mode = ref('login') // 'login' | 'register'
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const errors = ref({ username: '', email: '', password: '' })

function resetErrors() {
    errors.value = { username: '', email: '', password: '' }
}

// per-field validators
function validateUsernameField() {
    const v = username.value?.trim()
    if (!v) {
        errors.value.username = 'Username is required.'
        return false
    }
    if (v.length > 16) {
        errors.value.username = 'Username must not exceed 16 characters.'
        return false
    }
    errors.value.username = ''
    return true
}

function validateEmailField() {
    const v = email.value?.trim()
    if (!v) {
        errors.value.email = 'Email is required.'
        return false
    }
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if(!emailRegex.test(v)){
        errors.value.email = "Please enter a valid email address."
        return false
    }
    errors.value.email = ''
    return true
}

function validatePasswordField() {
    const v = password.value || ''
    if (!v) {
        errors.value.password = 'Password cannot be empty.'
        return false
    }
    if (v.length > 30) {
        errors.value.password = 'Password must not exceed 30 characters.'
        return false
    }
    errors.value.password = ''
    return true
}

// input / blur handlers
function onUsernameInput() { validateUsernameField() }
function onUsernameBlur() { validateUsernameField() }
function onEmailInput() { validateEmailField() }
function onEmailBlur() {validateEmailField() }
function onPasswordInput() { validatePasswordField() }
function onPasswordBlur() { validatePasswordField() }

// reuse field validators in overall validate
function validate() {
    // register requires all fields, login requires email + password
    if (mode.value === 'register') {
        const u = validateUsernameField()
        const e = validateEmailField()
        const p = validatePasswordField()
        return u && e && p
    } else {
        // login: require email and password only
        const hasEmail = !!email.value && email.value.trim() !== ''
        if (!hasEmail) {
            errors.value.email = 'Email is required.'
            return false
        }
        errors.value.email = ''
        const p = validatePasswordField()
        return p
    }
}

async function handleSubmit() {
    if (!validate()) return

    loading.value = true

    try {
        if (mode.value === 'register') {
            const payload = {
                username: username.value.trim(),
                email: email.value.trim(),
                password: password.value,
            }

            const res = await fetch('/api/users/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            })
            // read full response text for better debugging
            const text = await res.text().catch(() => '')
            let data = null
            try { data = text ? JSON.parse(text) : null } catch (err) { data = null }
            if (!res.ok) {
                const errMsg = data?.message || text || `Server returned ${res.status}`
                console.error('Register failed:', res.status, text)
                message.error(errMsg)
                return
            }
            let token = data?.token || data?.access_token || data?.auth_token
            if (!token) {
                const loginRes = await fetch('/api/users/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ identify: email.value.trim(), password: password.value }),
                })
                const loginText = await loginRes.text().catch(() => '')
                let loginData = null
                try { loginData = loginText ? JSON.parse(loginText) : null } catch (err) { loginData = null }
                if (!loginRes.ok) {
                    const errMsg = loginData?.message || loginText || `Server returned ${loginRes.status}`
                    console.error('Login after register failed:', loginRes.status, loginText)
                    message.error(`Registration succeeded, but auto-login failed: ${errMsg}`)
                    return
                }
                token = loginData?.token || loginData?.access_token || loginData?.auth_token
            }
            if (token) {
                localStorage.setItem('authToken', token)
                localStorage.setItem('authEmail', email.value.trim())
                localStorage.removeItem('authGuest')
                initUiSettings()
            }
            message.success('Registration successful. Redirecting...')
            router.push('/home')
        } else {
            // login: send identify (email only)
            const identify = email.value.trim()
            const payload = {
                identify,
                password: password.value,
            }

            const res = await fetch('/api/users/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            })
            // read full response text for better debugging
            const text = await res.text().catch(() => '')
            let data = null
            try { data = text ? JSON.parse(text) : null } catch (err) { data = null }
            if (!res.ok) {
                const errMsg = data?.message || text || `Server returned ${res.status}`
                console.error('Login failed:', res.status, text)
                message.error(errMsg)
                return
            }
            const token = data?.token || data?.access_token || data?.auth_token
            if (token) {
                localStorage.setItem('authToken', token)
                localStorage.setItem('authEmail', email.value.trim())
                localStorage.removeItem('authGuest')
                initUiSettings()
            }
            await handlePostAuth()
            message.success('Login successful. Redirecting...')
            router.push('/home')
        }
    } catch (e) {
        console.error(e)
        message.error(e?.message || 'Authentication failed.')
    } finally {
        loading.value = false
    }
}

async function handlePostAuth() {
    const raw = localStorage.getItem('guest_tasks')
    let guestTasks = []
    try {
        guestTasks = raw ? JSON.parse(raw) : []
    } catch (err) {
        guestTasks = []
    }
    if (!guestTasks || guestTasks.length === 0) return

    Modal.confirm({
        title: 'Import guest tasks?',
        content: `Detected ${guestTasks.length} guest task(s). Do you want to import them into your account?`,
        okText: 'Import',
        cancelText: 'Discard',
        async onOk() {
            localStorage.removeItem('authGuest')
            try {
                const importedIds = []
                const skippedIds = []
                const failed = []
                for (const t of guestTasks) {
                    const payload = {
                        task_title: t.task_title,
                        task_level: t.task_level ?? 0,
                        is_pinned: t.is_pinned ? 1 : 0,
                    }
                    if (t.task_due) payload.task_due = t.task_due
                    try {
                        const taskRes = await addTask(payload)
                        importedIds.push(t.id)
                    } catch (err) {
                        console.error('Failed to import task', t, err)
                        failed.push(t)
                    }
                }
                const remaining = guestTasks.filter(t => !importedIds.includes(t.id))
                if (remaining.length > 0) {
                    saveGuestTasks(remaining)
                } else {
                    localStorage.removeItem('guest_tasks')
                }

                const importedCount = importedIds.length
                const skippedCount = skippedIds.length
                const failedCount = failed.length
                message.success(`Import finished. Imported: ${importedCount}, Skipped (past due): ${skippedCount}, Failed: ${failedCount}`)
                router.push('/').catch(() => { })
                setTimeout(() => window.location.reload(), 300)
            } catch (err) {
                console.error('Failed to import guest tasks', err)
                message.error('Failed to import guest tasks. Your local guest data is kept.')
            }
        },
        onCancel() {
            localStorage.removeItem('guest_tasks')
            localStorage.removeItem('authGuest')
            message.info('Guest data discarded.')
        }
    })
}

function toggleMode() {
    mode.value = mode.value === 'login' ? 'register' : 'login'
    resetErrors()
    // if we're on /auth, reflect mode in query so URL can be shared
    if (route.path === '/auth') {
        router.replace({ query: { mode: mode.value } })
    }
}

// honor ?mode=register when arriving via goToRegister
onMounted(() => {
    if (route.query.mode === 'register') {
        mode.value = 'register'
    }
    // Prefill domain on initial render so user can type local part before it
    if (!email.value) {
        email.value = ''
        nextTick(() => {
            try {
                const comp = emailInput.value
                const inputEl = comp?.$el?.querySelector('input') || comp?.$el?.querySelector('textarea')
                if (inputEl) {
                    inputEl.focus()
                    // place caret at start so typing inserts local part before @
                    inputEl.setSelectionRange(0, 0)
                }
            } catch (err) {
                // ignore
            }
        })
    }
})

// update mode if query changes
watch(() => route.query.mode, (m) => {
    if (m === 'register') mode.value = 'register'
    else mode.value = 'login'
})

function continueAsGuest() {
    // set a lightweight guest flag so router guard allows access
    localStorage.removeItem('authEmail')
    localStorage.setItem('authGuest', '1')
    message.info('Continuing as guest')
    router.push('/')
}

</script>

<style scoped>
.auth-card {
    width: 420px;
    margin: 40px auto;
}

.header {
    text-align: center;
    margin-bottom: 16px;
}

.actions {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-direction: column;
}

.primary-row {
    width: 100%;
}

.primary-btn {
    width: 100%;
}

.links-row {
    display: flex;
    gap: 12px;
}
</style>
