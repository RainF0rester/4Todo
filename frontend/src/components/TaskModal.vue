<template>
    <a-modal :open="open" :title="mode === 'edit' ? 'Edit Task' : 'Add Task'" :okText="mode === 'edit' ? 'Save' : 'Add'"
        cancelText="Cancel" @ok="submitForm" @cancel="close" destroyOnClose>
        <a-form ref="formRef" :model="formState" :rules="rules" layout="vertical">
            <a-form-item name="title" label="Task title">
                <a-input v-model:value="formState.title" placeholder="Task title" />
            </a-form-item>
            <a-form-item name="dueDate" label="Due date">
                <a-date-picker v-model:value="formState.dueDate" style="width: 100%" format="YYYY-MM-DD HH:mm"
                    valueFormat="YYYY-MM-DD HH:mm" :show-time="{ format: 'HH:mm' }" :allowClear="true"
                    :disabled-date="disabledDate" :disabled-time="disabledDateTime" />
            </a-form-item>
            <a-form-item v-if="mode === 'edit'" name="taskLevel" label="Urgency Level">
                <a-select v-model:value="formState.task_level" :options="urgencyOptions" placeholder="Select urgency" />
            </a-form-item>
            <a-form-item name="pinned">
                <a-row :gutter="24">
                    <a-col :span="20">
                        <span>Pin to top</span>
                    </a-col>
                    <a-col :span="4">
                        <a-switch v-model:checked="formState.pinned" />
                    </a-col>
                </a-row>
            </a-form-item>

            <!-- <a-form-item name="assignee" label="Assignee">
                <a-select v-model:value="formState.assignee" :options="props.people" placeholder="Select a person"
                    allowClear style="width:100%;" />
            </a-form-item> -->
        </a-form>
    </a-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
    open: { type: Boolean, default: false },
    mode: { type: String, default: 'add' }, // 'add' | 'edit'
    task: { type: Object, default: null },  // edit {id,title,dueDate,done,...}
    people: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:open', 'submit'])
const formRef = ref()
const formState = reactive({
    id: null,
    title: '',
    dueDate: null,
    assignee: null,
    pinned: false,
    task_level: null,
})
const rules = {
    title: [{ required: true, message: 'Task title is required', trigger: 'blur' },
    { max: 100, message: 'Task title cannot exceed 100 characters', trigger: ['blur', 'change'] }
    ],
}

function resetForAdd() {
    formState.id = null
    formState.title = ''
    formState.dueDate = null
    formRef.value?.clearValidate?.()
    formState.assignee = null,
        formState.pinned = false
}

function fillForEdit(t) {
    formState.id = t?.id ?? null
    formState.title = t?.title ?? ''
    formState.dueDate = normalizeDueDate(t?.dueDate)
    formState.assignee = t?.assignee ?? null
    formState.pinned = Boolean(t?.pinned)
    formState.task_level = t?.task_level ?? null
    formRef.value?.clearValidate?.()
}

// init
watch(
    () => props.open,
    (v) => {
        if (!v) return
        if (props.mode === 'edit') fillForEdit(props.task)
        else resetForAdd()
    }
)

watch(
    () => props.task,
    (t) => {
        if (props.open && props.mode === 'edit') fillForEdit(t)
    },
    { deep: true }
)

function close() {
    emit('update:open', false)
}

function disabledDate(current) {
    if (!current) return false
    return current.isBefore(dayjs().startOf('day'))
}

function disabledDateTime(current) {
    if (!current) return {}
    const now = dayjs()
    if (!current.isSame(now, 'day')) {
        return {}
    }

    const currentHour = now.hour()
    const currentMinute = now.minute()

    return {
        disabledHours: () => Array.from({ length: currentHour }, (_, i) => i),
        disabledMinutes: (selectedHour) => {
            if (selectedHour === currentHour) {
                return Array.from({ length: currentMinute }, (_, i) => i)
            }
            return []
        },
        disabledSeconds: () => []
    }
}

function submitForm() {
    formRef.value
        .validate()
        .then(() => {
            emit('submit', {
                id: formState.id,
                title: formState.title.trim(),
                dueDate: toBackendDueDate(formState.dueDate),
                assignee: formState.assignee,
                pinned: formState.pinned,
                task_level: formState.task_level,
                mode: props.mode,
            })
            close()
        })
        .catch(() => { })
}

function normalizeDueDate(value) {
    if (!value) return null
    if (dayjs.isDayjs(value)) {
        return value.isValid() ? value.format('YYYY-MM-DD HH:mm') : null
    }
    if (typeof value === 'string') {
        const parsed = dayjs(value, ['YYYY-MM-DD HH:mm', 'YYYY-MM-DD'], true)
        if (parsed.isValid()) return parsed.format('YYYY-MM-DD HH:mm')
        const fallback = dayjs(value)
        return fallback.isValid() ? fallback.format('YYYY-MM-DD HH:mm') : null
    }
    return null
}

function toBackendDueDate(value) {
    if (!value) return null
    return normalizeDueDate(value)
}

const urgencyOptions = [
    { label: 'Important & Urgent', value: 1 },
    { label: 'Important but Not Urgent', value: 2 },
    { label: 'Not Important but Urgent', value: 3 },
    { label: 'Not Important & Not Urgent', value: 4 },
]
</script>