<template>
  <div class="min-h-screen flex flex-col bg-white">
    <Navigation />
    <main class="flex-grow bg-white">
      <slot />
    </main>
    <Footer />
  </div>
</template>

