<template>
  <nav class="border-gray-200 bg-[#FFFFFF]">
    <div class="flex fixed top-0 left-0 w-full bg-white shadow-2xs z-50 items-center justify-between px-6 py-4 sm:px-6 md:px-[100px] lg:px-[80px]">
      <!--Логотип-->
      <div href="#" class="flex items-start space-x-3 w-1/2">
        <img src="/src/assets/images/Logo_menu1.png" alt="Innova" class="w-[42px] h-auto"/>
        <div class="text-left">
          <h1 class="text-[17px] font-rubik text-black font-bold">Инноваторы</h1>
          <p class="text-[13px] mt-[-4px] font-rubik text-black font-medium">Краснодар</p>
        </div>
      </div>
      <div class="ml-auto flex items-center gap-2">
        <a
          href="#"
          class="desktop-button mr-[3px] text-black focus:ring-4 focus:ring-blue-300 font-rubik font-medium rounded-[10px] border-1 text-sm px-[35px] py-2.5 focus:outline-none border-[#9A9A9A]/20 hover:bg-gray-100"
        >
          Войти
        </a>
        <a
          href="#"
          class="desktop-button mr-[15px] text-white bg-[#4286F7] hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-rubik border-[#9A9A9A]/20 font-medium rounded-[10px] text-sm px-5 py-2.5 focus:outline-none"
        >
          Регистрация
        </a>
      </div>
      <button
        @click="isOpen = !isOpen"
        type="button"
        class="cursor-pointer inline-flex items-center justify-center p-2 w-10 h-10 text-sm text-[#111827] border-1 border-[#9A9A9A]/20 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
        aria-controls="navbar-hamburger"
        aria-expanded="false"
      >
        <span class="sr-only">Open main menu</span>
        <svg
          class="w-5 h-5"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 17 14"
        >
          <path
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M1 1h15M1 7h15M1 13h15"
          />
        </svg>
      </button>
    </div>
    <!-- Добавляем отступ, чтобы контент не перекрывался меню -->
    <div class="pt-[90px]">
      <!-- Здесь основной контент страницы -->
    </div>

    <!-- FULLSCREEN МЕНЮ -->
    <Transition name="slide-menu">
    <div 
      v-show="isOpen"
      class="fixed inset-0 bg-[#4286F7] text-white flex flex-col transition-all duration-300 z-50"
    >
      <div class="flex items-center justify-between px-6 py-4 sm:px-6 md:px-[100px] lg:px-[80px] no-scrollbar">
        <!--Логотип-->
        <div href="#" class="flex items-sart space-x-3 w-1/2">
          <img src="/src/assets/images/Logo_menu2.png" alt="Innova" class="w-[42px] h-auto" />
          <div class="text-left">
            <h1 class="text-[17px] font-rubik text-white font-bold">Инноваторы</h1>
            <p class="text-[13px] mt-[-4px] font-rubik text-white font-medium">Краснодар</p>
          </div>
        </div>
        <!--Кнопки-->
        <div class="ml-auto flex gap-2">
          <a
            href="#"
            class="desktop-button mr-[3px] text-white focus:ring-4 focus:ring-blue-300 font-rubik font-medium rounded-[10px] border-1 text-sm px-[35px] py-2.5 focus:outline-none border-white"
          >
            Войти
          </a>
          <a
            href="#"
            class="desktop-button mr-[15px] text-[#4286F7] bg-white focus:ring-4 focus:ring-blue-300 font-rubik font-medium rounded-[10px] text-sm px-5 py-2.5 focus:outline-none"
          >
            Регистрация
          </a>
        </div>
        <button
          @click="isOpen = false"
          class="cursor-pointer w-10 h-10 grid place-items-center border border-white rounded-lg text-white"
        >
          <span class="text-3xl leading-none py-[2px] mb-[4px]">×</span>
        </button>
      </div>

      <div class="container mx-auto">
        <div class="w-full h-[1px]  bg-gray-100 my-1 max-w-[calc(100%-3rem)] lg:max-w-[calc(100%-1rem)] mx-auto"></div>
      </div>
      <!--Инноваторы продукт СНО-->
      <div class="flex items-start justify-start m-2 flex-1 sm:flex-none sm:justify-start sm:pl-4">
        <div
          class="hidden lg:inline-block h-full flex-col justify-between w-full md:ml-[87px] sm:ml-4 sm:mt-4 md:mt-[250px]"
        >
          <h1
            class="md:transform md:rotate-90 md:text-[80px] lg:text-[100px] text-left lg:transform lg:rotate-0 font-bold text-[#9CB8FF]"
          >
            Инноваторы
          </h1>
          <p
            class="md:rotate-90 md:text-[18px] md:mr-[72px] lg:text-[32px] text-left lg:transform lg:rotate-0 font-regular mt-[-8px] text-[#9CB8FF] whitespace-nowrap"
          >
            Продукт СНО КУбГТУ
          </p>
          <div class="flex space-x-8 mt-36">
            <a href="#" target="_blank">
              <img src="/src/assets/images/vk.png" alt="VK" class="w-12 h-12" />
            </a>
            <a href="#" target="_blank">
              <img src="/src/assets/images/tg.png" alt="Telegram" class="w-12 h-12" />
            </a>
            <a href="#" target="_blank">
              <img src="/src/assets/images/whatsApp.png" alt="whatsApp" class="w-12 h-12" />
            </a>
          </div>
        </div>

        <!-- Навигация по центру -->
        <nav
          class="flex flex-col justify-start items-start w-full pl-12 pr-4 text-[55px] md:text-[55px] md:pr-[35px] lg:text-[85px] lg:mr-[30px] lg:max-w-none"
        >
          <a
            href="#"
            @click="isOpen = false"
            class="hover:text-[#FFBA26] ml-auto mb-2 text-[#FFBA26]"
            >главная</a
          >
          <a href="#" @click="isOpen = false" class="hover:text-[#FFBA26] ml-auto mb-2">поиск</a>
          <a href="#" @click="isOpen = false" class="hover:text-[#FFBA26] ml-auto mb-2">отклики</a>
          <a href="#" @click="isOpen = false" class="hover:text-[#FFBA26] ml-auto mb-2">faq</a>
          <a href="#" @click="isOpen = false" class="hover:text-[#FFBA26] ml-auto">контакты</a>

          <div class="flex justify-end w-full lg:hidden mt-5">
            <a
              href="#"
              class="w-[240px] h-[64px] text-[#4286F7] bg-white focus:ring-4 focus:ring-blue-300 font-medium rounded-[20px] text-center text-[27px] px-5 py-2.5 focus:outline-none"
            >
              Регистрация
            </a>
          </div>
          <div class="flex justify-end w-full space-x-8 mt-10 lg:hidde">
            <a href="#" target="_blank">
              <img src="/src/assets/images/vk.png" alt="VK" class="w-10 h-10 block lg:hidden" />
            </a>
            <a href="#" target="_blank">
              <img
                src="/src/assets/images/tg.png"
                alt="Telegram"
                class="w-10 h-10 block lg:hidden"
              />
            </a>
            <a href="#" target="_blank">
              <img
                src="/src/assets/images/whatsApp.png"
                alt="whatsApp"
                class="w-10 h-10 block lg:hidden"
              />
            </a>
          </div>
        </nav>
      </div>
    </div>
    </Transition>
  </nav>
</template>

<style scoped>
  /* ВЫЕЗД МЕНЮ СПРАВА */
.slide-menu-enter-from {
  transform: translateX(100%);
}

.slide-menu-enter-to {
  transform: translateX(0);
}

.slide-menu-leave-from {
  transform: translateX(0);
}

.slide-menu-leave-to {
  transform: translateX(100%);
}

.slide-menu-enter-active,
.slide-menu-leave-active {
  transition: transform 0.35s ease-in-out;
}

@media (max-width: 1023px) {
  .desktop-button {
    display: none;
  }
}

/* Скрываем скроллбар */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;  /* IE и Edge */
  scrollbar-width: none;      /* Firefox */
}
</style>

<script setup>
import { ref, watch } from 'vue'

// реактивная переменная для управления меню
const isOpen = ref(false)
watch(isOpen, (value) => {
  document.body.style.overflow = value ? 'hidden' : ''
})
</script>
