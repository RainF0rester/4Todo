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