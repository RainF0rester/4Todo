<!-- Note: Portions of this implementation were generated with AI assistance. -->
<template>
  <a-card title="Calendar">
    <div class="calendar-toolbar">
      <button type="button" class="calendar-year-control" @click="changeYear(-1)">Previous Year</button>
      <span class="calendar-year-label">{{ selectedYear }}</span>
      <button type="button" class="calendar-year-control" @click="changeYear(1)">Next Year</button>
    </div>
    <div class="calendar-chart-wrapper">
      <div ref="chartRef" class="calendar-chart" />
    </div>
  </a-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { getTaskList } from '../api/tasks'
import { getPalette, getThemeColor, uiSettings } from '../stores/uiSettings'

const chartRef = ref(null)
let chartInstance = null
const selectedYear = ref(dayjs().year())

function buildHeatmapData(tasks) {
  const counts = {}
  tasks.forEach((task) => {
    if (!task.dueDate) return
    const date = dayjs(task.dueDate).format('YYYY-MM-DD')
    if (!dayjs(date).isValid()) return
    counts[date] = (counts[date] || 0) + 1
  })
  return Object.entries(counts).map(([date, count]) => [date, count])
}

function resizeChart() {
  chartInstance?.resize()
}

async function renderCalendarHeatmap() {
  const tasks = await getTaskList()
  const data = buildHeatmapData(tasks)
  const year = selectedYear.value
  const maxCount = data.length ? Math.max(...data.map(([, count]) => count)) : 5
  const primaryColor = getThemeColor(uiSettings.theme)
  const palette = getPalette()

  chartInstance.setOption({
    tooltip: {
      formatter: (params) => `${params.value[0]}: ${params.value[1]} task${params.value[1] === 1 ? '' : 's'}`,
    },
    visualMap: {
      min: 0,
      max: Math.max(maxCount, 5),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      top: 300,
      inRange: {
        color: ['#f5f5f5', primaryColor],
      },
      textStyle: {
        color: palette.text,
      },
    },
    calendar: {
      top: 60,
      left: 30,
      right: 30,
      cellSize: ['auto', 25],
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

onMounted(async () => {
  await nextTick()
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    await renderCalendarHeatmap()
    window.addEventListener('resize', resizeChart)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

function changeYear(delta) {
  selectedYear.value += delta
  renderCalendarHeatmap()
}

watch(
  () => uiSettings.theme,
  () => {
    if (chartInstance) {
      renderCalendarHeatmap()
    }
  },
)
</script>

<style scoped>
.calendar-chart-wrapper {
  width: 100%;
  min-height: 420px;
}

.calendar-chart {
  width: 100%;
  height: 100%;
  min-height: 420px;
}

.calendar-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
}

.calendar-year-control {
  border: 1px solid var(--app-border, #d9d9d9);
  background: var(--app-surface, #ffffff);
  color: var(--app-text, #1f2937);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.calendar-year-label {
  font-weight: 600;
  color: var(--app-text, #1f2937);
}
</style>