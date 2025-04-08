const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5001',
    fixturesFolder: 'cypress/fixtures',
    specPattern: 'cypress/integration/**/*.js',
    supportFile: 'cypress/support/commands.js',
    setupNodeEvents(on, config) {
      return config;
    },
  },
});
