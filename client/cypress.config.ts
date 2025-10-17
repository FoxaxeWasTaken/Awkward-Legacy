import { defineConfig } from "cypress";

export default defineConfig({
  projectId: "ma59wi",
  e2e: {
    baseUrl: 'http://client-dev:5173',
    video: false,
    screenshotOnRunFailure: true,
    experimentalStudio: false,
    supportFile: 'cypress/support/e2e.ts',
  },
  env: {
    apiUrl: 'http://server-dev:8000'
  }
});
