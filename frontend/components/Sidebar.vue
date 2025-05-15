<template>
    <VNavigationDrawer color="#b2df8a" permanent elevation="15">
      <VList density="compact" nav class="custom-list">
        <VListItem to="/" title="About" prepend-icon="mdi-information-outline" class="custom-list-item"/>
        <VListItem to="/extractor" title="Get Started!" prepend-icon="mdi-rocket-launch" class="custom-list-item"/>
        <VListItem 
          href="https://github.com/zbmed-semtec/maSMP-metadata-extraction" 
          prepend-icon="mdi-github" 
          append-icon="mdi-open-in-new"
          title="Github" 
          target="_blank"
          class="custom-list-item"
        />
      </VList>
    </VNavigationDrawer>
  </template>
  
  <style scoped>
  :deep(.v-list-item__prepend) {
    display: inline !important;
    margin-right: 16px;
  }
  :deep(.v-list-item__append) {
    margin-left: 8px;
  }
  .custom-list-item {
    border-radius: 10px !important;
    margin: 4px 8px;
    padding: 8px 16px;
    transition: all 0.3s ease;
    color: #000000;
    font-family: 'Roboto', sans-serif;
    font-size: 1rem;
    font-weight: 400;
  }
  .custom-list-item:hover {
    background-color: #b2df8a;
    color: #000000;
    transform: translateX(3px);
  }
  :deep(.v-list-item--active) {
    background-color: #1f78b4 !important;
    color: #ffffff !important;
  }
  :deep(.v-list-item--active .icon-style) {
    color: #ffffff !important;
  }
  .icon-style {
    color: #ffffff;
    transition: color 0.3s ease;
  }
  .custom-list-item:hover .icon-style {
    color: #ffffff;
  }
  </style>