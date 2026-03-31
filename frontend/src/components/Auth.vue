<!-- The code on this page was generated with AI and then modified. -->
<template>
    <a-card class="auth-card">
        <div class="header">
            <h2>{{ mode === 'login' ? 'Login' : 'Register' }}</h2>
        </div>

        <a-form :layout="'vertical'" @submit.prevent>
            <a-form-item label="Username">
                <a-input v-model:value="username" @input="onUsernameInput" @blur="onUsernameBlur"
                    placeholder="Enter username" />
                <div v-if="errors.username" class="ant-form-item-explain">{{ errors.username }}</div>
            </a-form-item>

            <a-form-item label="UNSW Email">
                <a-input ref="emailInput" v-model:value="email" @input="onEmailInput" @blur="onEmailBlur"
                    placeholder="you@unsw.edu.au" autocomplete="email" />
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
import { message } from 'ant-design-vue'

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
    const unswRegex = /^[^@\s]+@([a-z0-9.-]+\.)?unsw\.edu\.au$/i
    if (!unswRegex.test(v)) {
        errors.value.email = 'Please enter your UNSW email address (must end with @unsw.edu.au).'
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
function onEmailBlur() {
    // If user typed local part only (no @), append UNSW domain on blur
    if (email.value && !email.value.includes('@')) {
        email.value = email.value.trim() + '@unsw.edu.au'
    }
    validateEmailField()
}
function onPasswordInput() { validatePasswordField() }
function onPasswordBlur() { validatePasswordField() }

// reuse field validators in overall validate
function validate() {
    // resetErrors() intentionally not called here to preserve per-field messages during typing
    const u = validateUsernameField()
    const e = validateEmailField()
    const p = validatePasswordField()
    return u && e && p
}

async function handleSubmit() {
    if (!validate()) return

    loading.value = true

    try {
        const payload = {
            username: username.value.trim(),
            email: email.value.trim(),
            password: password.value, // plain text per acceptance
        }

        if (mode.value === 'register') {
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
            // store token if backend returned one
            const token = data?.token || data?.access_token || data?.auth_token
            if (token) {
                localStorage.setItem('authToken', token)
            }
            message.success('Registration successful. Redirecting...')
            router.push('/')
        } else {
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
            // store token if backend returned one
            const token = data?.token || data?.access_token || data?.auth_token
            if (token) {
                localStorage.setItem('authToken', token)
            }
            message.success('Login successful. Redirecting...')
            router.push('/')
        }
    } catch (e) {
        console.error(e)
        message.error(e?.message || 'Authentication failed.')
    } finally {
        loading.value = false
    }
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
        email.value = '@unsw.edu.au'
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
    localStorage.setItem('authGuest', '1')
    message.info('Continuing as guest')
    router.push('/list')
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
