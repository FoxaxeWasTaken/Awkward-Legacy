import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
    },
    video: false,
    screenshotOnRunFailure: true,
    experimentalStudio: false,
  },
  env: {
  }
});
