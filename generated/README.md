# PyFlow.ts Project: codegen

## Run
In seperate terminals:
'''
npm run start-server
'''
'''
npm run start-ts
'''



This project was automatically generated with PyFlow.ts.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

This will start both the Python API server (on port 8000) and TypeScript compilation in watch mode.

## Using Your API

The generated `src/index.ts` file contains example code showing how to use your Python API from TypeScript:

```typescript
import * as api from '../index.js';

// Example usage
async function main() {
    // Use your API here
    // For example:
    if (api.someFunction) {
        const result = await api.someFunction();
        console.log(result);
    }
}
```

## Troubleshooting

### TypeScript Import Issues

If you encounter TypeScript errors related to imports:

1. **Missing Extensions**: Ensure all imports have `.js` extensions when using ES modules:
   ```typescript
   // Correct:
   import * as api from './module/index.js';
   ```

2. **Module Not Found**: If the import path doesn't match your file structure, you may need to adjust it.
   Try looking at the generated directories and update the path accordingly.

### Server Connection

If your TypeScript code can't connect to the Python server:

1. Make sure the server is running (should start with `npm start`)
2. Check that you're using the correct port number
3. Look for any error messages in the server console

## Project Structure

- `src/index.ts`: Main entry point for your TypeScript code
- `dist/`: Contains compiled JavaScript output
- `_server/`: Contains the FastAPI server code
- `_client/`: Contains client libraries for API access

## Available Scripts

- `npm start`: Start both the Python server and TypeScript compiler
- `npm run start-server`: Start only the Python server
- `npm run start-ts`: Start only the TypeScript compiler
- `npm run build`: Build TypeScript files
- `npm run serve`: Run the built JavaScript
- `npm run dev`: Run TypeScript directly with ts-node
