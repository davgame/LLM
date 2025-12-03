<template>
  <div class="w-full flex flex-col items-center mt-10">

    <!-- Заголовок -->
    <h1 class="text-5xl font-bold mb-8">Новый проект<span class="text-black/20">○</span></h1>

    <!-- Поле ввода -->
    <div class="relative w-[480px]">
      <input
        v-model="text"
        @input="debouncedFetch"
        placeholder="Воображение важнее, чем знание"
        class="w-full p-5 pb-15 border border-blue-400 rounded-2xl text-lg outline-none"
      />

      <!-- Smart Mood toggle -->
      <button
        @click="smartMood = !smartMood; debouncedFetch()"
        class="absolute left-4 bottom-3 bg-white shadow px-3 py-1 rounded-lg border text-sm flex items-center gap-2"
      >
        <span class="text-gray-700">Smart Mood</span>
        <span v-if="smartMood" class="text-green-500">●</span>
      </button>

      <!-- Микрофон -->
      <button class="absolute right-3 top-1/3 -translate-y-1/2 bg-blue-500 text-white p-3 rounded-full">
        🎤
      </button>
    </div>

    <!-- Выпадающий список -->
    <div
      v-if="names.length"
      class="mt-4 w-[480px] border border-blue-400 rounded-2xl bg-white shadow-lg p-2"
    >
      <div
        v-for="(name, index) in names"
        :key="index"
        @click="selectName(name)"
        class="p-3 rounded-xl cursor-pointer flex items-center gap-2 hover:bg-blue-100"
        :class="{ 'bg-blue-500 text-white hover:bg-blue-500': selectedIndex === index }"
        @mouseover="selectedIndex = index"
      >
        <span>↗</span>
        <span>{{ name }}</span>
      </div>
    </div>

    <!-- Кнопка Далее -->
    <button
      class="mt-12 bg-black text-white px-16 py-4 rounded-2xl text-xl hover:bg-black/80"
    >
      Далее
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";

const text = ref("");
const names = ref([]);
const smartMood = ref(false);
const selectedIndex = ref(null);
let timeout = null;

const debouncedFetch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(fetchNames, 500);
};

async function fetchNames() {
  if (text.value.length < 3) return;

  try {
    const res = await fetch("http://localhost:3001/api/names", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text.value,
        smartMood: smartMood.value,
      }),
    });

    if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`);

    const data = await res.json();
    // Добавляем лог, чтобы проверить, что вернул сервер
    console.log("Ответ сервера:", data);

    // разбиваем строку на массив имён
    names.value = data.result
      .split("\n")
      .map(t => t.replace(/^\d+\.\s*/, "").trim())
      .filter(t => t.length > 2);
  } catch (err) {
    console.error("Ошибка запроса:", err);
  }
}
</script>