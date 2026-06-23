import { request } from "./request";

const POMODORO_API = "/pomodoro"

export async function logPomodoro(){
    const res = await request(`${POMODORO_API}`, {
        method: "POST"
    })

    if (!res.ok){
        const data = await res.json().catch(() => null)
        throw new Error(data?.message || "log pomodoro fail")
    }

    return res.json()
}

export async function getPomodoroToday() {
    const res = await request(`${POMODORO_API}/today`)

    if (!res.ok){
        const data = await res.json().catch(() => null)
        throw new Error(data?.message || "get today's pomodoro fail")
    }

    return res.json()
}

export async function getPomodoroRange(startDate, endDate) {
    const res = await request(`${POMODORO_API}/range?start_date=${startDate}&end_date=${endDate}`)

    if (!res.ok){
        const data = await res.json().catch(() => null)
        throw new Error(data?.message || "get pomodoro range fail")
    }

    return res.json()
}

