<template>
    <div>
      <VApp>
        <Header />
        <Sidebar />
        <VMain>
          <VContainer>
            <slot />
          </VContainer>
        </VMain>
        <Footer />
      </VApp>
    </div>
  </template>
  
  <script>
  import Header from '/components/Header.vue';
  import Sidebar from '/components/Sidebar.vue';
  import Footer from '/components/Footer.vue';
  
  export default {
    components: {
      Header,
      Sidebar,
      Footer
    }
  };
  </script>