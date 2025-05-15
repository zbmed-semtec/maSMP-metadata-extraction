<template>
  <v-bottom-navigation
    class="py-4 px-6 elevation-8"
    style="background: #1f78b4; border-top: 1px solid #e0e0e0;"
  >
    <v-container fluid class="d-flex align-center justify-space-between">
      <span class="text-caption text-white font-weight-medium">
        © 2025 ZBMED. All rights reserved.
      </span>
      <div class="d-flex align-center">
        <v-btn
          href="https://www.nfdi4datascience.de/"
          target="_blank"
          variant="text"
          class="mx-2 animated-btn smaller-text"
          color="#ffffff"
        >
          <v-img
            src="/images/NFDI4DS_Logo.png"
            class="nfdi-small-icon"
          ></v-img>
        </v-btn>
        <v-btn
          href="https://www.zbmed.de"
          target="_blank"
          variant="text"
          class="mx-2 animated-btn smaller-text"
          color="#ffffff"
        >
          <v-img
            src="/images/ZBMED_Logo.png"
            class="zbmed-small-icon"
          ></v-img>
        </v-btn>
        <v-btn
          href="https://zbmed-semtec.github.io/maSMPs/"
          target="_blank"
          variant="text"
          class="mx-2 animated-btn smaller-text"
          color="#ffffff"
        >
          <v-icon left class="mr-1 smaller-icon" color="#ffffff">mdi-web</v-icon>
          <span class="text-caption text-white font-weight-medium">
            Official Page
          </span>
        </v-btn>
      </div>
    </v-container>
  </v-bottom-navigation>
</template>

<style scoped>
.v-bottom-navigation {
transition: background-color 0.3s ease;
}

.animated-btn {
transition: transform 0.2s ease, color 0.2s ease;
}

.animated-btn:hover {
transform: translateY(-2px);
}

.animated-btn .v-img,
.animated-btn .v-icon {
transition: transform 0.2s ease;
}

.animated-btn:hover .v-img,
.animated-btn:hover .v-icon {
transform: scale(1.1);
}

.text-caption {
letter-spacing: 0.5px;
}

.smaller-text {
font-size: 0.85rem !important;
text-transform: none;
}

.smaller-icon {
width: 20px !important;
height: 20px !important;
}

.zbmed-small-icon{
  width: 45px !important;
  height: 45px !important;    
}

.nfdi-small-icon{
  width: 65px !important;
  height: 55px !important;    
}
</style>