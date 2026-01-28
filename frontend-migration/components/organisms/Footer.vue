<template>
  <footer class="bg-gray-800 text-gray-300 mt-auto">
    <div class="container-custom py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 class="text-white font-semibold mb-4">maSMP</h3>
          <p class="text-sm">
            Machine-Actionable Software Management Plan Metadata Extraction Tool.
          </p>
        </div>

        <div>
          <h3 class="text-white font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink to="/" class="hover:text-white">Home</NuxtLink></li>
            <li><NuxtLink to="/dashboard" class="hover:text-white">Dashboard</NuxtLink></li>
            <li><NuxtLink to="/fair-assessment" class="hover:text-white">FAIR Assessment</NuxtLink></li>
            <li><NuxtLink to="/best-practices" class="hover:text-white">Best Practices</NuxtLink></li>
          </ul>
        </div>

        <div>
          <h3 class="text-white font-semibold mb-4">Resources</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="hover:text-white">Documentation</a></li>
            <li><a href="#" class="hover:text-white">API Docs</a></li>
            <li><a href="#" class="hover:text-white">GitHub</a></li>
          </ul>
        </div>
      </div>

      <div class="mt-8 pt-8 border-t border-gray-700 text-center text-sm">
        <p>
          &copy; {{ new Date().getFullYear() }} maSMP Metadata Extractor. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>
