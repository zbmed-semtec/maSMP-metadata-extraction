<template>
  <v-container class="text-center">
    <h2 style="color: #1f78b4; font-family: 'Roboto', sans-serif;">
      Automated Metadata Extraction Compliant with Machine-actionable Software Management Plans
    </h2>
    <h3 style="color: #333; font-weight: 500; margin-top: 8px;">
      Transforming GitHub Repositories into FAIR and Machine-Actionable Metadata
    </h3>
    <v-row justify="center" align="center" class="mt-4">
      <v-col cols="auto">
        <v-icon size="50" color="#b2df8a">mdi-github</v-icon>
        <div style="font-size: 12px; color: #b2df8a;">GitHub</div>
      </v-col>
      <v-col cols="auto">
        <div class="arrow-container"></div>
      </v-col>
      <v-col cols="auto">
        <v-icon size="50" color="#1f78b4">mdi-cog</v-icon>
      </v-col>
      <v-col cols="auto">
        <div class="arrow-container"></div>
      </v-col>
      <v-col cols="auto">
        <v-icon size="50" color="#b2df8a">mdi-file-document</v-icon>
        <div style="font-size: 12px; color: #b2df8a;">JSON</div>
      </v-col>
    </v-row>
    <p style="max-width: 800px; margin: 12px auto; font-size: 16px; color: #444;">
      In today’s research ecosystem, managing software and its associated metadata has become increasingly important 
      for transparency, reproducibility, and reusability. Our project addresses this need by automating the extraction 
      of metadata from GitHub repositories to generate Machine-Actionable Software Management Plans (maSMPs) that are 
      aligned with FAIR principles and widely adopted metadata standards.
    </p>
    <v-row justify="center" class="mt-8">
      <v-col cols="12" sm="6" v-for="(card, index) in cards" :key="index">
        <div class="flip-card">
          <div class="flip-card-inner">
            <div class="flip-card-front">
              <v-card class="d-flex align-center justify-center pa-4" height="200" color="#1f78b4" rounded="xl">
                <v-card-title class="white--text text-center" style="word-break: break-word;">
                  {{ card.title }}
                  <v-icon class="hover-hint" color="white" small>mdi-cursor-default-click</v-icon>
                </v-card-title>
              </v-card>
            </div>
            <div class="flip-card-back">
              <v-card class="d-flex align-center justify-center pa-4" height="200" color="#b2df8a" rounded="xl">
                <v-card-text class="black--text text-justify">
                  {{ card.content }}
                </v-card-text>
              </v-card>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Stylized Section: Our Approach -->
    <v-container class="mt-12">
      <v-row justify="center">
        <v-col cols="12" md="10">
          <div class="section-block approach-section">
            <h2 class="section-title">
              <v-icon left color="#1f78b4" class="mr-2">mdi-lightbulb-on-outline</v-icon>
              Our Approach
            </h2>
            <p>
              We are committed to making software and software management plans more <strong>FAIR</strong> by developing a metadata schema specifically tailored for maSMPs. To do this, we have extended existing standards like <strong>schema.org</strong> and <strong>CodeMeta</strong>:
            </p>
            <ul>
              <li><strong>schema.org</strong> is widely used for describing research artifacts and offers excellent interoperability.</li>
              <li><strong>CodeMeta</strong> is a community-driven standard for software metadata, providing detailed descriptors for software-related content.</li>
            </ul>
            <p>
              Together, these serve as a robust foundation for our maSMP schema.
              <br />
              <a href="https://zbmed-semtec.github.io/maSMPs" target="_blank" class="approach-link">
                Learn more
              </a>
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!-- Stylized Section: Community Alignment -->
    <v-container class="mt-8">
      <v-row justify="center">
        <v-col cols="12" md="10">
          <div class="section-block community-section">
            <h2 class="section-title">
              <v-icon left color="#b2df8a" class="mr-2">mdi-account-group-outline</v-icon>
              Community Alignment
            </h2>
            <p align="left">
              Our maSMP schema is continuously refined and aligned with community efforts such as:
            </p>
            <ul>
              <li>ELIXIR’s Software Management Plan initiatives</li>
              <li>The Netherlands eScience Center’s SMP work</li>
              <li>Max Planck Digital Libraries</li>
            </ul>
            <p>
              We also incorporate feedback and insights gathered from community events, including hackathons and metadata workshops, to ensure relevance and adaptability.
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!-- Stylized Section: Metadata Extraction Process Timeline -->
    <v-container class="mt-12">
      <h2 class="section-title text-center mb-6">
        <v-icon left color="#1f78b4" class="mr-2">mdi-timeline-text-outline</v-icon>
        Metadata Extraction Process
      </h2>
      <v-timeline align-top>
        <v-timeline-item
          v-for="(item, index) in items"
          :key="index"
          :color="item.color"
          :dot-color="item.color"
          :icon="item.icon"
          fill-dot
          small
        >
          <v-card
            class="pa-4 d-flex flex-column justify-space-between text-left"
            :color="item.cardColor"
            elevation="8"
            style="min-height: 220px;"
            rounded="xl"
          >
            <v-card-title class="text-h6 font-weight-bold mb-2">
              {{ item.title }}
            </v-card-title>
            <v-card-text class="mb-0 mt-10">
              {{ item.text }}
            </v-card-text>
            <!-- <h3 class="text-h6 font-weight-bold mb-2"></h3> -->
            <!-- <p class="mb-0">{{ item.text }}</p> -->
          </v-card>
        </v-timeline-item>
      </v-timeline>

    </v-container>



    <!-- Contributors Section -->
    <v-container class="mt-12 text-center">
      <h2 class="section-title">
        <v-icon left color="#1f78b4" class="mr-2">mdi-account-circle-outline</v-icon>
        Contributors
      </h2>
      <v-row justify="center" align="center" class="mt-4">
        <v-col cols="6" sm="3" v-for="contributor in contributors" :key="contributor.name" class="text-center">
          <a :href="contributor.orcid" target="_blank">
            <v-avatar size="80" class="mx-auto mb-2">
              <v-img :src="contributor.avatar" alt="Avatar" />
            </v-avatar>
            <div style="font-weight: 500; color: #333;">{{ contributor.name }}</div>
          </a>
        </v-col>
      </v-row>
    </v-container>

  </v-container>
</template>

<script>
export default {
  data() {
    return {
      cards: [
        {
          title: "FAIR and Machine-Actionable Metadata",
          content: "FAIR stands for Findable, Accessible, Interoperable, and Reusable. These guiding principles aim to improve the infrastructure supporting the reuse of scholarly data and digital artifacts. When metadata is machine-actionable, it can be automatically interpreted, linked, and processed by software agents, enabling seamless integration and discovery across systems."
        },
        {
          title: "Machine-Actionable Software Management Plan",
          content: "A Software Management Plan (SMP) outlines how software used or developed in a research project will be managed throughout its lifecycle. A machine-actionable SMP enhances this by structuring the plan in a way that allows automatic processing, validation, and interlinking with other digital research outputs and registries."
        }
      ],
      items: [
        {
          title: 'Step 1: GitHub API Integration',
          text: 'Automatically gathers repository-level metadata such as contributors, issues, topics, and commit history.',
          icon: 'mdi-api',
          color: 'green',
          cardColor: '#e8f5e9',
        },
        {
          title: 'Step 2: File Parsing',
          text: ' Analyzes repository contents like README files, license files, and configuration files to extract structured metadata.',
          icon: 'mdi-file-code',
          color: 'blue',
          cardColor: '#e3f2fd',
        },
        {
          title: 'Step 3: External Data Enrichment',
          text: 'Augments data using external sources such as OpenAlex, Software Heritage Archive, Wayback Machine (Internet Archive).',
          icon: 'mdi-link-variant',
          color: 'green',
          cardColor: '#e8f5e9',
        },
      ],
      contributors: [
        {
          name: "Dhwani Solanki",
          orcid: "https://orcid.org/0009-0004-1529-0095",
          avatar: "https://avatars.githubusercontent.com/u/55695957?v=4"
        },
        {
          name: "Leyla Jael Castro",
          orcid: "https://orcid.org/0000-0003-3986-0510",
          avatar: "https://avatars.githubusercontent.com/u/2734205?v=4"
        },
        {
          name: "Dietrich Rebholz-Schuhmann",
          orcid: "https://orcid.org/0000-0002-1018-0370",
          avatar: "https://avatars.githubusercontent.com/u/595775?v=4"
        },
        {
          name: "Suhasini Venkatesh",
          orcid: "https://orcid.org/0009-0005-7305-3052",
          avatar: "https://avatars.githubusercontent.com/u/115443248?v=4"
        }
      ]


    };
  }
};
</script>

<style scoped>
.arrow-container {
  width: 60px;
  height: 20px;
  position: relative;
  overflow: hidden;
}

.arrow-container::before {
  content: "> > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > >";
  font-size: 16px;
  color: black;
  position: absolute;
  white-space: nowrap;
  animation: slideArrows 2.5s infinite linear;
}

@keyframes slideArrows {
  0% { transform: translateX(-50%); }
  100% { transform: translateX(0); }
}

.flip-card {
  perspective: 1000px;
  height: 200px;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
}

.flip-card-back {
  transform: rotateY(180deg);
}

.hover-hint {
  margin-left: 8px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

.section-block { 
  padding: 32px; 
  border-left: 6px solid #1f78b4; 
  border-top: 3px solid #1f78b4; 
  border-radius: 20px; 
  background-color: #f9f9f9; 
  color: #333; margin-bottom: 40px;
  } 
  
.approach-section { 
  border-color: #1f78b4; 
} 

.community-section { 
  border-color: #b2df8a; 
  } 

.section-title { 
  font-size: 24px; 
  font-weight: 600; 
  display: flex; 
  align-items: center; 
  color: #1f78b4; 
  margin-bottom: 16px; 
  } 
  
.community-section .section-title { 
  color: #b2df8a; 
  } 
  
ul { 
  text-align: left; 
  padding-left: 20px; 
  margin-top: 10px; 
  margin-bottom: 10px; 
  } 
  
ul li { 
  margin-bottom: 6px; 
} 

.approach-link { 
  color: #1f78b4; 
  font-weight: bold; 
  text-decoration: underline; } 

.timeline-bounce {
  animation: fadeInUp 0.8s ease forwards;
  opacity: 0;
}

  @keyframes fadeInUp {
    0% {
      transform: translateY(30px);
      opacity: 0;
    }
    100% {
      transform: translateY(0);
      opacity: 1;
    }
  }

</style>

