<template>
  <div class="h-screen flex flex-col bg-white overflow-hidden">
    <header role="banner" class="shrink-0">
      <Navigation />
    </header>
    <main class="flex-1 min-h-0 overflow-y-auto bg-white" role="main">
      <slot />
    </main>
    <footer role="contentinfo" class="shrink-0">
      <Footer />
    </footer>
  </div>
</template>
