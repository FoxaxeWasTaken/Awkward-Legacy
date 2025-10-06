import { defineConfig } from "cypress";

export default defineConfig({
  projectId: "ma59wi",
  e2e: {
    video: false,
    screenshotOnRunFailure: true,
    experimentalStudio: false,
  },
  env: {
  }
});
