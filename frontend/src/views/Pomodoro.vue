<template>
  <a-card title="Pomodoro">
    <!-- pomodoro statics -->
    <div class="statics-row">
      <a-card>
        <a-statistic title="Today" :value="todayCount" suffix="🍅"></a-statistic>
      </a-card>
      <a-card>
        <a-statistic title="This Week" :value="weekCount" suffix="🍅"></a-statistic>
      </a-card>
      <a-card>
        <a-statistic title="Total" :value="totalCount" suffix="🍅"></a-statistic>
      </a-card>
    </div>
    <a-divider />
    <!-- pomodoro timer -->
    <div class="timer">
      <span>Working on</span>
      <a-select v-model:value="selectedTaskId" placeholder="related task (optimal)" allow-clear style="width: 300px;">
        <a-select-option v-for="task in tasks" :key="task.id" :value="task.id" :style="{color: levelColor(task.task_level)}">{{ task.title }}</a-select-option>
      </a-select>
      <p class="time-display">{{ formattedTime }}</p>
      <div class="round-dots">
        <span v-for="i in 4" :key="i" class="dot"
          :class="{ active: i <= activeDots }"></span>
      </div>
      <div class="timer-buttons">
        <a-button type="primary" @click="toggleTimer">
          {{ isRunning ? "pause" : "start" }}
        </a-button>
        <a-button @click="resetTimer">reset</a-button>
      </div>
    </div>
    <a-divider/>
    <div ref="chartRef" style="width: 100%; height: 250px;"></div>
  </a-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch, nextTick } from 'vue';
import { getTaskList, increaseTaskPomodoro } from '../api/tasks';
import { getPomodoroRange, getPomodoroToday, logPomodoro } from '../api/pomodoro'

import * as echarts from 'echarts'
import { getPalette, getThemeColor, uiSettings } from '../stores/uiSettings'

// pomodoro related variables
const mode = ref(localStorage.getItem('pomodoroMode') || 'focus') // 'focus' | 'short' | 'long'
const round = ref(parseInt(localStorage.getItem('pomodoroRound')) || 0)
watch(mode, (val) => localStorage.setItem('pomodoroMode', val))
watch(round, (val) => {localStorage.setItem('pomodoroRound', val)})
const DURATIONS = {
  focus: 25 * 60,
  short: 5 * 60,
  long: 15 * 60,
}
const timeLeft = ref(25 * 60)
const isRunning = ref(false)
let timer = null

// tasks
const tasks = ref([])
const selectedTaskId = ref(null)

// statics
const todayCount = ref(0)
const weekCount = ref(0)
const totalCount = ref(0)

// everyday pomodoro statics
const chartRef = ref(null)
let chartInstance = null
function onResize() { chartInstance?.resize() }

onMounted(async () => {
  tasks.value = await getTaskList()

  const leftAt = localStorage.getItem('pomodoroLeftAt')
  const savedTimeLeft = localStorage.getItem('pomodoroTimeLeft')
  const savedTaskId = localStorage.getItem('pomodoroTaskId')
  selectedTaskId.value = savedTaskId ? Number(savedTaskId) : null

  localStorage.removeItem('pomodoroLeftAt')
  localStorage.removeItem('pomodoroTimeLeft')
  localStorage.removeItem('pomodoroTaskId')

  if (leftAt && savedTimeLeft && isRunning.value === false){
    const elapsed = Math.floor((Date.now() - Number(leftAt)) / 1000)
    const restored = parseInt(savedTimeLeft) - elapsed
    timeLeft.value = restored > 0 ? restored : 0
    
    if (restored <= 0){
      await onPomodoroComplete()
    }else{
      toggleTimer()
    }
  }

  const todayRecord = await getPomodoroToday()
  todayCount.value = todayRecord?.count ?? 0

  const today = new Date()
  const dayOfWeek = today.getDay()
  const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
  const startOfWeek = new Date(today.setDate(diff))
  const startOfWeekStr = startOfWeek.toISOString().slice(0, 10)
  const todayStr = new Date().toISOString().slice(0, 10)

  const weekRecords = await getPomodoroRange(startOfWeekStr, todayStr)
  weekCount.value = weekRecords.reduce((sum, r) => sum + r.count, 0)

  const totalRecords = await getPomodoroRange('1970-01-01', todayStr)
  totalCount.value = totalRecords.reduce((sum, r) => sum + r.count, 0)

  await nextTick()
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    await renderHeatmap()
    window.addEventListener('resize', onResize)
  }
})

onBeforeUnmount(() => {
  if (isRunning.value){
    localStorage.setItem('pomodoroLeftAt', Date.now())
    localStorage.setItem('pomodoroTimeLeft', timeLeft.value)
    localStorage.setItem('pomodoroTaskId', selectedTaskId.value ?? '')
    localStorage.setItem('pomodoroMode', mode.value)
    localStorage.setItem('pomodoroRound', round.value)
  }
  clearInterval(timer)
  window.removeEventListener('resize', onResize)
  chartInstance?.dispose()
})

const activeDots = computed(() => {
  if (round.value === 0) return 0
  const r = round.value % 4
  return r === 0 ? 4 : r
})

// format second to mm:ss
const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60)
  const s = timeLeft.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

// start or pause timer
function toggleTimer() {
  if (isRunning.value) {
    clearInterval(timer)
    isRunning.value = false
  } else {
    isRunning.value = true
    timer = setInterval(() => {
      if (timeLeft.value <= 0) {
        await onPomodoroComplete()
      } else {
        timeLeft.value -= 1
      }
    }, 1000);
  }
}

function switchMode(newMode) {
  clearInterval(timer)
  isRunning.value = false
  mode.value = newMode
  timeLeft.value = DURATIONS[newMode]
}

function resetTimer() {
  clearInterval(timer)
  isRunning.value = false
  timeLeft.value = DURATIONS[mode.value]
}

async function onPomodoroComplete(){
  clearInterval(timer)
  isRunning.value = false

  if(mode.value === 'focus'){
    round.value += 1
    await logPomodoro()
    if(selectedTaskId.value !== null){
      await increaseTaskPomodoro(selectedTaskId.value)
    }
    if (round.value % 4 === 0){
      switchMode('long')
    }else{
      switchMode('short')
    }
  } else{
    switchMode('focus')
  }
}

function levelColor(level){
  const colors = {
    1: '#ef4444',
    2: '#f59e0b',
    3: '#3b82f6',
    4: '#10b981',
  }

  return colors[level] || '#666'
}

async function renderHeatmap() {
  const todayStr = new Date().toISOString().slice(0, 10)
  const year = new Date().getFullYear()
  const records = await getPomodoroRange(`${year}-01-01`, todayStr)
  const data = records.map(r => [r.date, r.count])

  const primaryColor = getThemeColor(uiSettings.theme)
  const palette = getPalette()

  chartInstance.setOption({
    tooltip: {
      formatter: (params) => `${params.value[0]}: ${params.value[1]} 🍅`,
    },
    visualMap: {
      min: 0,
      max: Math.max(...records.map(r => r.count), 4),
      calculable: false,
      show: false,
      inRange: {
        color: ['#f5f5f5', primaryColor],
      },
    },
    calendar: {
      top: 30,
      left: 30,
      right: 30,
      cellSize: ['auto', 20],
      range: year,
      itemStyle: {
        borderWidth: 1,
        borderColor: palette.border,
      },
      yearLabel: {
        show: false,
      },
      dayLabel: {
        firstDay: 1,
        nameMap: 'en',
        color: palette.subtext,
      },
      monthLabel: {
        color: palette.subtext,
      },
    },
    series: [
      {
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data,
      },
    ],
  })
}

</script>

<style scoped>
.timer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.time-display {
  font-size: 64px;
  font-weight: bold;
  letter-spacing: 4px;
  margin: 0;
}

.timer-buttons {
  display: flex;
  gap: 12px;
}

.round-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #d9d9d9;
}

.dot.active {
  background: var(--app-primary, #ff4d4f);
}

.statics-row{
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.statics-row .ant-card{
  flex: 1;
  text-align: center;
}
</style>