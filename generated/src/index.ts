// Example usage of PyFlow.ts-generated TypeScript

// For Node.js < 18, uncomment this line if needed:
// import fetch from 'node-fetch';

// Import all exported items from the root index
import * as api from '../index.js';

// Log available APIs for debugging
console.log("Available API methods:", Object.keys(api));

// Example usage
async function main() {
    try {
        console.log("Available PyFlow.ts APIs:");

        // List all available functions and classes
        for (const key of Object.keys(api)) {
            if (typeof api[key] === 'function') {
                console.log(`- Function: ${key}`);
            } else if (typeof api[key] === 'object' || typeof api[key] === 'function') {
                console.log(`- Class/Object: ${key}`);
            }
        }

        console.log("\nTo use these APIs, import them from specific modules or the root index.");
        console.log("Example: import { SomeClass, someFunction } from '../index.js';");

    } catch (error) {
        console.error("Error:", error);
        console.log("\nTroubleshooting tips:");
        console.log("1. Make sure the PyFlow.ts server is running with: npm run start-server");
        console.log("2. Check that the import paths are correct");
        console.log("3. Verify that the API functions/classes match what's in your Python code");
    }
}

main().catch(error => {
    console.error("Error:", error);
});
