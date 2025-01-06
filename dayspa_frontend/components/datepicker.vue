<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'
import {
  DateFormatter,
  type DateValue,
  getLocalTimeZone,
} from '@internationalized/date'
import { Calendar as CalendarIcon } from 'lucide-vue-next'
import { ref, defineProps, defineEmits } from 'vue'

// Define props to accept modelValue
const props = defineProps({
  modelValue: {
    type: Object as PropType<DateValue>, // Use PropType to specify DateValue type
    required: false,
  },
})
const emit = defineEmits(['update:modelValue'])

const df = new DateFormatter('en-US', {
  dateStyle: 'long',
})

// Use the value passed from the parent or initialize it if not provided
const value = ref(props.modelValue)

const updateValue = (newValue: DateValue) => {
  value.value = newValue
  emit('update:modelValue', newValue) // Emit updated value to parent
}
</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button
          variant="outline"
          :class="cn(
          'w-[280px] justify-start text-left font-normal',
          !value && 'text-muted-foreground',
        )"
      >
        <CalendarIcon class="mr-2 h-4 w-4" />
        {{ value ? df.format(value.toDate(getLocalTimeZone())) : "Pick a date" }}
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0">
      <Calendar v-model="value" @update:modelValue="updateValue" initial-focus />
    </PopoverContent>
  </Popover>
</template>
