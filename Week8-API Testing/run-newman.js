const newman = require("newman");

newman.run(
  {
    collection: require("./API Testing.postman_collection.json"),
    environment: require("./API testing.postman_environment.json"),
    reporters: ["cli", "json", "html"],
    reporter: {
      json: { export: "./newman-results.json" },
      html: { export: "./newman-report.html" },
    },
  },
  function (err) {
    if (err) {
      console.error(err);
      process.exit(1);
    }
    console.log("Collection run complete!");
  }
);
