// PyFlow.ts runtime for TypeScript
export interface PyFlowRuntime {
  callFunction(moduleName: string, functionName: string, args: any): any;
  callMethod(className: string, methodName: string, args: any, constructorArgs: any, instanceObj?: any): any;
  createInstance(className: string, constructorArgs: any): any;
  registerInstance(obj: any, instanceId: string | undefined): void;
}

// Default implementation that uses fetch to call the Python API
class DefaultPyFlowRuntime implements PyFlowRuntime {
  apiUrl: string;
  debug: boolean;
  connectionErrorCount: number = 0;
  maxRetries: number = 3;
  isPortAutoDetectionEnabled: boolean = true;

  // Track instances by class and object ID
  private instanceCache = new Map<string, string>();
  private instanceIds = new Map<Object, string>();

  debugLog(message: string, data?: any) {
    if (this.debug) {
      if (data) {
        console.log(`[pyflow] ${message}`, data);
      } else {
        console.log(`[pyflow] ${message}`);
      }
    }
  }

  constructor(apiUrl: string = 'http://localhost:8000/api', debug: boolean = false) {
    this.apiUrl = apiUrl;
    this.debug = debug;
    this.debugLog(`Initialized with API URL: ${this.apiUrl}`);
  }

  // Auto-detect API server port if the main port is unavailable
  async detectApiPort(): Promise<boolean> {
    if (!this.isPortAutoDetectionEnabled) return false;

    this.debugLog(`Attempting to detect API server port...`);

    // Extract base URL and port from current apiUrl
    const url = new URL(this.apiUrl);
    const baseUrl = `${url.protocol}//${url.hostname}`;
    const currentPort = parseInt(url.port);

    // Try sequential ports
    for (let portOffset = 0; portOffset < 10; portOffset++) {
      const portToTry = currentPort + portOffset;
      const testUrl = `${baseUrl}:${portToTry}/api`;

      try {
        this.debugLog(`Testing connection to ${testUrl}...`);
        const response = await fetch(`${testUrl}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        if (response.ok) {
          if (portOffset > 0) {
            this.debugLog(`Found API server at port ${portToTry}!`);
            this.apiUrl = testUrl;
            return true;
          } else {
            this.debugLog(`Connection successful on current port.`);
            return false; // No change needed
          }
        }
      } catch (e) {
        // Continue trying next port
      }
    }

    this.debugLog(`Could not find API server on any nearby ports.`);
    return false;
  }

  async callFunction(moduleName: string, functionName: string, args: any): Promise<any> {
    this.debugLog(`Calling function: ${moduleName}.${functionName}`, {
      module: moduleName,
      function: functionName,
      args: args
    });

    // Convert any instance objects in args to their IDs
    const processedArgs = this.processArgs(args);

    try {
      const response = await fetch(`${this.apiUrl}/call-function`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          module: moduleName,
          function: functionName,
          args: processedArgs,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        this.debugLog(`Error calling function: ${errorText}`);

        // Try to parse as JSON to get structured error details
        try {
          const errorDetails = JSON.parse(errorText);
          throw new Error(`Failed to call Python function: ${errorDetails.detail || errorText}`);
        } catch (parseError) {
          // If not JSON, use text as is
          throw new Error(`Failed to call Python function: ${errorText}`);
        }
      }

      const data = await response.json();
      this.debugLog(`Function result:`, data.result);
      return data.result;
    } catch (error) {
      // Check for connection errors and attempt port detection
      if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError'))) {
        this.connectionErrorCount++;

        if (this.connectionErrorCount <= this.maxRetries) {
          this.debugLog(`Connection error: ${error.message}. Attempting to detect correct port...`);
          const portChanged = await this.detectApiPort();

          if (portChanged) {
            this.debugLog(`Port detected, retrying function call with new URL: ${this.apiUrl}`);
            return this.callFunction(moduleName, functionName, args);
          }
        }
      }

      throw error;
    }
  }

  // Process arguments to handle objects with instance IDs
  processArgs(args: any): any {
    if (!args) return {};

    const processedArgs: any = Array.isArray(args) ? [] : {};

    for (const key in args) {
      const value = args[key];

      if (value && typeof value === 'object') {
        // Check if this object has an instance ID
        if (this.instanceIds.has(value)) {
          // Replace object with reference
          processedArgs[key] = {
            __instance_id__: this.instanceIds.get(value),
            __object_ref__: true
          };
        }
        else if (Array.isArray(value)) {
          // Process array contents recursively
          processedArgs[key] = this.processArgs(value);
        }
        else if (Object.prototype.toString.call(value) === '[object Date]') {
          // Convert Date objects to ISO strings
          processedArgs[key] = value.toISOString();
        }
        else {
          // Process normal object recursively
          processedArgs[key] = this.processArgs(value);
        }
      } else {
        // Pass through primitive values
        processedArgs[key] = value;
      }
    }

    return processedArgs;
  }

  async createInstance(className: string, constructorArgs: any): Promise<string> {
    this.debugLog(`Creating instance of: ${className}`, {
      class: className,
      constructorArgs: constructorArgs
    });

    // Ensure constructor args aren't undefined and process them
    const safeArgs = this.processArgs(constructorArgs || {});

    try {
      const response = await fetch(`${this.apiUrl}/create-instance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          class: className,
          constructor_args: safeArgs,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        this.debugLog(`Error creating instance: ${errorText}`);

        // Try to parse error as JSON for structured error details
        try {
          const errorDetails = JSON.parse(errorText);
          throw new Error(`Failed to create instance: ${errorDetails.detail || errorText}`);
        } catch (parseError) {
          throw new Error(`Failed to create instance: ${errorText}`);
        }
      }

      const data = await response.json();
      const instanceId = data.instance_id;
      this.debugLog(`Created instance with ID: ${instanceId}`);

      // Store in the class-based cache - useful for some scenarios
      this.instanceCache.set(className, instanceId);

      return instanceId;
    } catch (error) {
      // Check for connection errors and attempt port detection
      if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError'))) {
        this.connectionErrorCount++;

        if (this.connectionErrorCount <= this.maxRetries) {
          this.debugLog(`Connection error: ${error.message}. Attempting to detect correct port...`);
          const portChanged = await this.detectApiPort();

          if (portChanged) {
            this.debugLog(`Port detected, retrying createInstance with new URL: ${this.apiUrl}`);
            return this.createInstance(className, constructorArgs);
          }
        }
      }

      throw error;
    }
  }

  // Register an object with an instance ID for tracking
  registerInstance(obj: any, instanceId: string | undefined) {
    if (obj && instanceId) {
      this.instanceIds.set(obj, instanceId);
      this.debugLog(`Registered object with instance ID: ${instanceId}`);
    }
  }

  async callMethod(className: string, methodName: string, args: any, constructorArgs: any, instanceObj?: any): Promise<any> {
    // Get instance ID from the object if provided
    let instanceId: string | null | undefined = null;
    if (instanceObj && this.instanceIds.has(instanceObj)) {
      instanceId = this.instanceIds.get(instanceObj);
      this.debugLog(`Found instance ID from object: ${instanceId}`);
    }

    // If not found, fall back to the class-based cache
    if (!instanceId) {
      instanceId = this.instanceCache.get(className);
      this.debugLog(`Using class-based instance ID: ${instanceId}`);
    }

    // Ensure args and constructorArgs aren't undefined
    const processedArgs = this.processArgs(args || {});
    const safeConstructorArgs = this.processArgs(constructorArgs || {});

    this.debugLog(`Calling method: ${className}.${methodName}`, {
      class: className,
      method: methodName,
      args: processedArgs,
      constructorArgs: safeConstructorArgs,
      instanceId: instanceId
    });

    try {
      const response = await fetch(`${this.apiUrl}/call-method`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          class: className,
          method: methodName,
          args: processedArgs,
          constructor_args: safeConstructorArgs,
          instance_id: instanceId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        this.debugLog(`Error calling method: ${errorText}`);

        // Try to parse as JSON for detailed error information
        try {
          const errorDetails = JSON.parse(errorText);
          throw new Error(`Failed to call Python method: ${errorDetails.detail || errorText}`);
        } catch (parseError) {
          // If not JSON, use text directly
          throw new Error(`Failed to call Python method: ${errorText}`);
        }
      }

      const data = await response.json();

      // If we got a new instance ID back, register it
      if (data.instance_id && data.instance_id !== instanceId) {
        this.instanceCache.set(className, data.instance_id);
        // If there's an instance object, register it too
        if (instanceObj) {
          this.registerInstance(instanceObj, data.instance_id);
        }
      }

      this.debugLog(`Method result:`, data.result);
      return data.result;
    } catch (error) {
      // Check for connection errors and attempt port detection
      if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError'))) {
        this.connectionErrorCount++;

        if (this.connectionErrorCount <= this.maxRetries) {
          this.debugLog(`Connection error: ${error.message}. Attempting to detect correct port...`);
          const portChanged = await this.detectApiPort();

          if (portChanged) {
            this.debugLog(`Port detected, retrying method call with new URL: ${this.apiUrl}`);
            return this.callMethod(className, methodName, args, constructorArgs, instanceObj);
          }
        }
      }

      throw error;
    }
  }
}

// Export a global instance
export const pyflowRuntime: PyFlowRuntime = new DefaultPyFlowRuntime();
