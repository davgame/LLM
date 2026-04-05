<template>
  <div class="w-full flex flex-col items-center lg:mt-16 mt-7">
    <!-- Заголовок -->
    <h1 class="lg:text-5xl text-[33px] font-bold lg:mb-12 mb-8">Новый проект<span class="text-[#222222]"></span></h1>

    <!-- Поле ввода -->
     <div class="items-center justify-between  lg:px-[100px]">
    <div class="relative lg:w-[480px] mb-6 align-items justify-center">
      <textarea
        ref="textarea"
        rows="1"
        v-model="query"
        @input="handleInput"
        @keydown.enter.exact.prevent="fetchSuggestions"
        @keydown.enter.shift.exact.prevent="query += '\n'"
        placeholder="Воображение важнее, чем знание"
        class="w-full min-w-[330px] lg:min-h-[140px] min-h-[125px] max-h-[200px] p-6 border-2 border-blue-300 rounded-3xl lg:text-lg text-[15px] outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200 resize-none overflow-hidden"
      ></textarea>

      <!-- Smart Mood toggle -->
    <button
      @click="toggleSmartMood"
      class="cursor-pointer lg:mb-3 mb-2 absolute left-4 bottom-3 px-3 py-2 rounded-[13px] border text-sm flex items-center gap-2 transition-all duration-200 group"
      :class="[
      // Базовые классы
      'border',
      // Когда ВКЛЮЧЕНО (синий фон сразу)
      smartMood ? 'bg-blue-500/26 text-[#0066FF] border-blue-500/26' : '',
      // Когда ВЫКЛЮЧЕНО (белый фон)
      !smartMood ? 'bg-white text-gray-700 border-[#000000]/10' : '',
      // Hover эффект только для выключенного состояния
      !smartMood ? 'hover:bg-blue-500/26 hover:text-[#0066FF] hover:border-[#000000]/10' : '',
      ]"
    >
      <!-- Иконка -->
      <div class="relative w-5 h-5">
        <!-- Синяя иконка (когда Smart Mood включен или при hover) -->
        <img
          v-if="smartMood || true"
          src="/icons/smart_active.svg"
          class="w-full h-full transition-all duration-300"
          :class="[
            smartMood ? 'opacity-100' : 'opacity-0 group-hover:opacity-100',
            'absolute inset-0'
          ]"
          alt="Smart Mood Active"
        />
        
        <!-- Серая иконка (только когда Smart Mood выключен и нет hover) -->
        <img
          src="/icons/smart.svg"
          class="w-full h-full transition-all duration-300 filter grayscale"
          :class="[
            !smartMood ? 'opacity-100' : 'opacity-0',
            'group-hover:opacity-0 absolute inset-0'
          ]"
          alt="Smart Mood"
        />
      </div>
      
      <!-- Текст -->
      <span class="font-medium transition-colors duration-200">
        Smart Mood
      </span>
    </button>

      <!-- Кнопка запроса -->
      <button
        @click="fetchSuggestions"
        :disabled="loading || !query.trim()"
        class="absolute right-3 lg:top-1/3 top-[40px] -translate-y-1/2 bg-blue-500 text-white p-2 rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        🔍
      </button>
    </div>
  </div>

    <!-- Статус -->
    <div v-if="loading" class="lg:w-[480px] w-[330px] align-items justify-center mb-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
      <div class="flex items-center justify-center gap-3">
        <div class="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <span class="text-blue-700 font-medium">Генерация рекомендаций...</span>
      </div>
      <p class="mt-2 text-sm text-blue-600 text-center">Модель анализирует запрос</p>
    </div>

    <!-- Ошибка -->
    <div v-if="error" class="lg:w-[480px] w-[330px] align-items justify-center mb-4 mb-4 p-4 bg-red-50 rounded-xl border border-red-200">
      <div class="flex items-center gap-2 text-red-700">
        <span>⚠️</span>
        <span class="font-medium">{{ error }}</span>
      </div>
      <p class="mt-2 text-sm text-red-600">Проверьте, что бэкенд запущен на порту 3001</p>
    </div>

    <!-- Результаты -->
    <div v-if="suggestions.length" class="lg:w-[480px] w-[330px] align-items justify-center mb-4 border-2 border-blue-300 rounded-2xl bg-white shadow-lg overflow-hidden">
      <div class="p-3 bg-blue-50 border-b border-blue-200">
        <h3 class="font-semibold text-[#0066FF]">Рекомендации от AI:</h3>
      </div>
      <div  class="divide-y divide-gray-100 max-h-[195px] overflow-y-auto"
            style="scrollbar-width: thin; scrollbar-color: #C9DFFB #f0f9ff;">
        <div
          v-for="(suggestion, index) in suggestions"
          :key="index"
          @click="selectSuggestion(suggestion)"
          @mouseenter="hoveredIndex = index"
          @mouseleave="hoveredIndex = -1"
          :class="[
            'p-5 cursor-pointer transition-all duration-200',
            hoveredIndex === index ? 'bg-blue-50' : 'hover:bg-gray-50',
            selectedIndex === index ? 'bg-blue-100 border-l-4 border-blue-500' : ''
          ]"
        >
          <div class="flex items-start gap-3">
            <img
              src="/icons/up.svg"
              class="w-5 h-5 transition-all duration-300 filter grayscale"
              alt="Smart Mood"
            />
            <div>
              <p class="font-medium text-[#32383E]">{{ suggestion }}</p>
              
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Состояние пустого результата -->
    <div v-if="!loading && !error && suggestions.length === 0 && query.trim() && hasSearched" 
         class="w-[480px] p-6 text-center text-gray-500 border border-dashed border-gray-300 rounded-xl">
      <p>Введите запрос и нажмите Enter или кнопку 🔍</p>
    </div>
    <!-- Кнопка "Подробнее" -->
    <button class="btn-more bg-[#222222] hover:bg-[#4286F7] text-white font-medium py-4 lg:px-28 px-30 text-[20px] rounded-[18px] fixed bottom-10 left-1/2 transform -translate-x-1/2 z-40 transition-colors duration-300">
      Далее
    </button>
  </div>
  
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'

// Реактивные данные
const query = ref('')
const smartMood = ref(true)
const textarea = ref(null)
const suggestions = ref([])
const loading = ref(false)
const error = ref('')
const hoveredIndex = ref(-1)
const selectedIndex = ref(-1)
const hasSearched = ref(false)

// Таймер для debounce
let inputTimer = null


// Обработчик ввода с debounce и авторегулировкой высоты
const handleInput = () => {
  // Авторегулировка высоты
  autoResize()
  
  // Debounce для запросов
  error.value = ''
  clearTimeout(inputTimer)
  inputTimer = setTimeout(() => {
    if (query.value.trim()) {
      fetchSuggestions()
    }
  }, 800)
}

// Авторегулировка высоты textarea
const autoResize = () => {
  nextTick(() => {
    if (textarea.value) {
      textarea.value.style.height = 'auto'
      const scrollHeight = textarea.value.scrollHeight
      // Устанавливаем высоту, но не меньше 130px и не больше 200px
      const newHeight = Math.max(130, Math.min(scrollHeight, 200))
      textarea.value.style.height = newHeight + 'px'
    }
  })
}

// Переключение Smart Mood
const toggleSmartMood = () => {
  smartMood.value = !smartMood.value
  console.log('Smart Mood:', smartMood.value ? 'включен' : 'выключен')
}

// Основная функция запроса
const fetchSuggestions = async () => {
  if (!query.value.trim()) {
    suggestions.value = []
    return
  }

  loading.value = true
  error.value = ''
  hasSearched.value = true
  suggestions.value = []
  selectedIndex.value = -1

  try {
    console.log('📡 Отправляю запрос к бэкенду...')
    
    const response = await fetch('http://localhost:3001/api/names', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        text: query.value,
        smartMood: smartMood.value
      })
    })

    console.log('✅ Статус ответа:', response.status)

    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.status}`)
    }

    const data = await response.json()
    console.log('📦 Получены данные:', data)

    if (data && Array.isArray(data.result)) {
      suggestions.value = data.result
      console.log(`🎉 Получено ${data.result.length} рекомендаций`)
    } else {
      throw new Error('Неверный формат ответа от сервера')
    }

  } catch (err) {
    console.error('❌ Ошибка:', err)
    error.value = err.message
    
  } finally {
    loading.value = false
  }
}

// Выбор рекомендации
const selectSuggestion = (suggestion) => {
  console.log('👉 Выбрано:', suggestion)
  query.value = suggestion
  selectedIndex.value = suggestions.value.indexOf(suggestion)
  
  // Через 2 секунды сбрасываем выделение
  setTimeout(() => {
    selectedIndex.value = -1
  }, 2000)
}

// Очистка таймера при размонтировании компонента
onUnmounted(() => {
  clearTimeout(inputTimer)
})
</script>
