<template>
  <div class="body-container">
    <div class="grid">
      <TaskGroupCard title="Important & Urgent" color="red" :initialItems="urgentImportant" />
      <TaskGroupCard title="Important but Not Urgent" color="yellow" :initialItems="importantNotUrgent" />
      <TaskGroupCard title="Not Important but Urgent" color="blue" :initialItems="urgentNotImportant" />
      <TaskGroupCard title="Not Important & Not Urgent" color="green" :initialItems="notUrgentNotImportant" />
    </div>
  </div>
</template>

<script setup>
import TaskGroupCard from '../components/TaskGroupCard.vue'

const urgentImportant = [
  {
    id: 1, title: 'mock1', dueDate: '2026-03-05', done: false
  },
  {
    id: 2, title: 'mock2', dueDate: '2025-07-05', done: false
  },
  {
    id: 3, title: 'mock2', dueDate: '2026-07-05', done: true
  },
  {
    id: 4, title: 'mock2', dueDate: '2025-12-05', done: false
  },
]
const importantNotUrgent = []
const urgentNotImportant = []
const notUrgentNotImportant = []
</script>

<style scoped>
.body-container {
  margin: 0 auto;
  padding: 20px 50px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>