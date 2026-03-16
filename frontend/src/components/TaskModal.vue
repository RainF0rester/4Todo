<template>
    <a-modal :open="open" :title="mode === 'edit' ? 'Edit Task' : 'Add Task'" :okText="mode === 'edit' ? 'Save' : 'Add'"
        cancelText="Cancel" @ok="submitForm" @cancel="close" destroyOnClose>
        <a-form ref="formRef" :model="formState" :rules="rules">
            <a-form-item name="title" label="Task title">
                <a-input v-model:value="formState.title" placeholder="Task title" />
            </a-form-item>

            <a-form-item name="dueDate" label="Due date">
                <a-date-picker v-model:value="formState.dueDate" style="width:100%;" format="YYYY-MM-DD"
                    valueFormat="YYYY-MM-DD" />
            </a-form-item>

            <a-form-item name="assignee" label="Assignee">
                <a-select v-model:value="formState.assignee" :options="props.people" placeholder="Select a person"
                    allowClear style="width:100%;" />
            </a-form-item>
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
    dueDate: dayjs().format('YYYY-MM-DD'),
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
    formState.dueDate = dayjs().format('YYYY-MM-DD')
    formRef.value?.clearValidate?.()
    formState.assignee = null
}

function fillForEdit(t) {
    formState.id = t?.id ?? null
    formState.title = t?.title ?? ''
    formState.dueDate = t?.dueDate ?? dayjs().format('YYYY-MM-DD')
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

function submitForm() {
    formRef.value
        .validate()
        .then(() => {
            emit('submit', {
                id: formState.id,
                title: formState.title.trim(),
                dueDate: formState.dueDate,
                assignee: formState.assignee,
                mode: props.mode,
            })
            close()
        })
        .catch(() => { })
}
</script>