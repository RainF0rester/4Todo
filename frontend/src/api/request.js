const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function request(path, options = {}) {
    const token = localStorage.getItem('authToken')

    const res = await fetch(`${BASE_URL}${path}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(options.headers ? options.headers : {}),
        },
    })

    if (res.status === 401) {
        const newToken = await tryRefresh()
        // refresh fail, logout
        if (!newToken) {
            localStorage.removeItem('authToken')
            window.location.href = 'auth'
            return
        }
        // refresh success, request again
        return fetch(`${BASE_URL}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { Authorization: `Bearer ${newToken}` } : {}),
                ...options.headers,
            }
        })
    }
    return res
}

async function tryRefresh() {
    const token = localStorage.getItem('authToken')
    if (!token) return null

    // use fetch, not request() function, to avoid unfinit loop
    const res = await fetch(`${BASE_URL}/users/auth/refresh`, {
        headers: { Authorization: `Bearer ${token}` }
    })

    if (!res.ok) return null

    const data = await res.json()
    localStorage.setItem('authToken', data.token)
    return data.token
}