import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    video: false,
    screenshotOnRunFailure: true,
    experimentalStudio: false,
  },
  env: {
  }
});
