const fs = require('fs');

// Read the swagger.js file
const swaggerJsContent = fs.readFileSync('swagger.js', 'utf8');

// Create a mock window object to capture the options
let capturedOptions = null;

const mockWindow = {
  onload: null,
  location: {
    search: '',
    origin: 'http://localhost'
  }
};

// Create mock SwaggerUI objects
const SwaggerUIBundle = function(options) {
  capturedOptions = options;
  return {
    initOAuth: () => {},
    authActions: { authorize: () => {} },
    preauthorizeApiKey: () => true
  };
};

SwaggerUIBundle.presets = { apis: {} };
SwaggerUIBundle.plugins = { DownloadUrl: {} };

const SwaggerUIStandalonePreset = {};

// Set up the environment
global.window = mockWindow;
global.SwaggerUIBundle = SwaggerUIBundle;
global.SwaggerUIStandalonePreset = {};

// Execute the swagger.js code
eval(swaggerJsContent);

// Call the onload function to trigger the options setup
if (mockWindow.onload) {
  mockWindow.onload();
}

// Extract the swaggerDoc
if (capturedOptions && capturedOptions.spec) {
  const spec = capturedOptions.spec;
  
  // Fix the server/servers field name
  if (spec.server) {
    spec.servers = spec.server;
    delete spec.server;
  }
  
  // Fix the malformed URL if present
  if (spec.servers && spec.servers[0] && spec.servers[0].url) {
    spec.servers[0].url = spec.servers[0].url.replace(/}$/, '');
  }
  
  // Write the complete OpenAPI spec to file
  fs.writeFileSync('openapi_spec.json', JSON.stringify(spec, null, 2));
  
  console.log('Successfully extracted OpenAPI specification!');
  console.log(`- OpenAPI version: ${spec.openapi}`);
  console.log(`- Title: ${spec.info.title}`);
  console.log(`- Version: ${spec.info.version}`);
  console.log(`- Paths: ${Object.keys(spec.paths).length}`);
  console.log(`- Schemas: ${Object.keys(spec.components.schemas).length}`);
  console.log('\nSample endpoints:');
  Object.keys(spec.paths).slice(0, 5).forEach(path => {
    const methods = Object.keys(spec.paths[path]).filter(m => m !== 'parameters');
    console.log(`  ${path} - ${methods.join(', ').toUpperCase()}`);
  });
} else {
  console.error('Failed to extract swaggerDoc from the file');
}