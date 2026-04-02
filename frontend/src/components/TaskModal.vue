<template>
    <a-modal :open="open" :title="mode === 'edit' ? 'Edit Task' : 'Add Task'" :okText="mode === 'edit' ? 'Save' : 'Add'"
        cancelText="Cancel" @ok="submitForm" @cancel="close" destroyOnClose>
        <a-form ref="formRef" :model="formState" :rules="rules">
            <a-form-item name="title" label="Task title">
                <a-input v-model:value="formState.title" placeholder="Task title" />
            </a-form-item>

            <a-form-item name="dueDate" label="Due date">
                <a-date-picker v-model:value="formState.dueDate" style="width: 100%" format="YYYY-MM-DD HH:mm"
                    valueFormat="YYYY-MM-DD HH:mm" :show-time="{ format: 'HH:mm' }" :disabled-date="disabledDate"
                    :allowClear="true" :disabled-time="disabledDateTime" />
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
    assignee: null
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
    formState.assignee = null
}

function fillForEdit(t) {
    formState.id = t?.id ?? null
    formState.title = t?.title ?? ''
    formState.dueDate = normalizeDueDate(t?.dueDate)
    formState.assignee = t?.assignee ?? null
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
        disabledHours: () =>
            Array.from({ length: currentHour }, (_, i) => i),

        disabledMinutes: (selectedHour) => {
            if (selectedHour === currentHour) {
                return Array.from({ length: currentMinute }, (_, i) => i)
            }
            return []
        }
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
                mode: props.mode,
            })
            close()
        })
        .catch(() => { })
}

function normalizeDueDate(value) {
    if (!value) return null

    const dateTime = dayjs(value, 'YYYY-MM-DD HH:mm', true)
    if (dateTime.isValid()) {
        return dateTime.format('YYYY-MM-DD HH:mm')
    }

    const dateOnly = dayjs(value, 'YYYY-MM-DD', true)
    if (dateOnly.isValid()) {
        return `${dateOnly.format('YYYY-MM-DD')} 00:00`
    }

    return null
}

function toBackendDueDate(value) {
    if (!value) return null
    return normalizeDueDate(value)
}
</script>