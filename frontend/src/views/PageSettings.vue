<template>
<div class="settings-page">
    <a-card title="Settings">
        <div class="setting-block">
            <div class="dark-mode-block">
                <div>Dark Mode</div>
                <a-switch />
            </div>  
            <div class="settings-block">
                <div class="settings-type">Theme</div>
                <a-select placeholder="Select Theme" style="width: 100%">
                    <a-select-option value="blue">Blue</a-select-option>
                    <a-select-option value="yellow">Yellow</a-select-option>
                    <a-select-option value="green">Green</a-select-option>
                    <a-select-option value="red">Red</a-select-option>
                </a-select>
            </div>

            <div class="settings-block">
                <div class="settings-type">Font Size</div>
                <a-select placeholder="Select Font Size" style="width: 100%">
                    <a-select-option value="small">Small</a-select-option>
                    <a-select-option value="medium">Medium</a-select-option>
                    <a-select-option value="large">Large</a-select-option>
                </a-select>
            </div>
            <div class="settings-block">
                <div class="settings-type">Font Type</div>
                <a-select placeholder="Select Font Type" style="width: 100%">
                    <a-select-option value="default">Default</a-select-option>
                    <a-select-option value="sans-serif">Sans Serif</a-select-option>
                    <a-select-option value="TimesNewRoman">Times New Roman</a-select-option>
                </a-select>
            </div>
        </div>
    </a-card>
</div>

</template>



<script setup>

</script>


<style scoped>
.settings-page {
  max-width: 1000px;
  margin: 0 auto;
}

.setting-block {
  display: flex;
  flex-direction: column;
  gap: 24px;
}



.dark-mode-block {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.settings-type {  
    font-weight: 600;
}

</style>