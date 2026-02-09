<template>
  <footer class="bg-secondary-800 text-white mt-auto">
    <div class="container-custom py-6 sm:py-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
        <div>
          <h3 class="text-white font-semibold mb-4">CoMET-RS</h3>
          <p class="text-sm text-gray-300">
            Machine-Actionable Software Management Plan Metadata Extraction Tool.
          </p>
        </div>

        <div>
          <h3 class="text-white font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink to="/" class="hover:text-cyan-300 transition-colors">Home</NuxtLink></li>
            <li><NuxtLink to="/dashboard" class="hover:text-cyan-300 transition-colors">Dashboard</NuxtLink></li>
            <li><NuxtLink to="/fair-assessment" class="hover:text-cyan-300 transition-colors">FAIR Assessment</NuxtLink></li>
            <li><NuxtLink to="/best-practices" class="hover:text-cyan-300 transition-colors">Best Practices</NuxtLink></li>
          </ul>
        </div>

        <div>
          <h3 class="text-white font-semibold mb-4">Resources</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="hover:text-cyan-300 transition-colors">Documentation</a></li>
            <li><a href="#" class="hover:text-cyan-300 transition-colors">API Docs</a></li>
            <li><a href="#" class="hover:text-cyan-300 transition-colors">GitHub</a></li>
          </ul>
        </div>
      </div>

      <div class="mt-6 sm:mt-8 pt-6 sm:pt-8 border-t border-secondary-600 text-center text-xs sm:text-sm">
        <p>
          &copy; {{ new Date().getFullYear() }} CoMET-RS - maSMP Metadata Extractor. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>
