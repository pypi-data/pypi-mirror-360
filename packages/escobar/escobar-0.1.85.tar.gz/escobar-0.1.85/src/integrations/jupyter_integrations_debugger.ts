import { JupyterFrontEnd } from '@jupyterlab/application';
import { Debugger, IDebugger } from '@jupyterlab/debugger';
import { app, notebookTracker, debuggerService, functions } from './jupyter_integrations';
import { getActiveNotebook } from './jupyter_integrations';
import { Cell, CodeCell } from '@jupyterlab/cells';

export function init_debugger() {
    // Register debugger-related functions here

    functions["startDebugger"] = {
        "def": {
            "name": "startDebugger",
            "description": "Turn on the debugger for the current notebook",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            const notebook = getActiveNotebook(app);
            if (!notebook || !notebook.sessionContext) {
                return JSON.stringify({ error: "No active notebook found" });
            }

            try {
                // Check if debugging is available for this kernel
                const isAvailable = await debuggerService.isAvailable(notebook.sessionContext.session);
                if (!isAvailable) {
                    return JSON.stringify({
                        error: "Debugging is not available for the current kernel"
                    });
                }

                // Set the current session connection to the debugger service
                if (debuggerService.session) {
                    debuggerService.session.connection = notebook.sessionContext.session;
                }

                // Start the debugger
                await debuggerService.start();

                // Restore state and display variables
                await debuggerService.restoreState(true);
                await debuggerService.displayDefinedVariables();

                // Create a handler for the notebook
                // This is the critical step to enable breakpoints and debugging UI
                const handler = new Debugger.Handler({
                    type: 'notebook',
                    shell: app.shell,
                    service: debuggerService
                });

                // Update the handler with the current notebook
                await handler.updateContext(notebook, notebook.sessionContext);

                // Activate the debugger sidebar
                if (app.commands.hasCommand('debugger:show-panel')) {
                    app.commands.execute('debugger:show-panel');
                }

                // Set data attributes for CSS styling
                document.body.dataset.jpDebuggerActive = 'true';

                // If the debugger has stopped threads, set that attribute too
                if (debuggerService.hasStoppedThreads()) {
                    document.body.dataset.jpDebuggerStoppedThreads = 'true';
                }

                return JSON.stringify({
                    success: true,
                    message: "Debugger started successfully and UI activated"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error starting debugger: ${error.message}`
                });
            }
        }
    };

    functions["stopDebugger"] = {
        "def": {
            "name": "stopDebugger",
            "description": "Turn off the debugger for the current notebook",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            try {
                if (!debuggerService.isStarted) {
                    return JSON.stringify({
                        success: true,
                        message: "Debugger is not running"
                    });
                }

                // Stop the debugger
                await debuggerService.stop();

                // Clean up UI state
                delete document.body.dataset.jpDebuggerActive;
                delete document.body.dataset.jpDebuggerStoppedThreads;

                // Collapse the right sidebar to hide the debugger panel
                // Use any type to bypass TypeScript checking
                const shell = app.shell as any;
                if (shell && typeof shell.collapseRight === 'function') {
                    shell.collapseRight();
                }

                return JSON.stringify({
                    success: true,
                    message: "Debugger stopped successfully"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error stopping debugger: ${error.message}`
                });
            }
        }
    };

    functions["isDebuggerAvailable"] = {
        "def": {
            "name": "isDebuggerAvailable",
            "description": "Check if debugging is available for the current notebook",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            const notebook = getActiveNotebook(app);
            if (!notebook || !notebook.sessionContext) {
                return JSON.stringify({ error: "No active notebook found" });
            }

            try {
                const isAvailable = await debuggerService.isAvailable(notebook.sessionContext.session);

                return JSON.stringify({
                    success: true,
                    available: isAvailable
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error checking debugger availability: ${error.message}`
                });
            }
        }
    };

    functions["getDebuggerState"] = {
        "def": {
            "name": "getDebuggerState",
            "description": "Get the current state of the debugger",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            try {
                return JSON.stringify({
                    success: true,
                    isStarted: debuggerService.isStarted,
                    hasStoppedThreads: debuggerService.hasStoppedThreads()
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error getting debugger state: ${error.message}`
                });
            }
        }
    };

    // Breakpoint Management Functions

    functions["setBreakpoint"] = {
        "def": {
            "name": "setBreakpoint",
            "description": "Set a breakpoint in the current notebook cell",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to set breakpoint in"
                },
                "lineNumber": {
                    "type": "integer",
                    "name": "Line number to set breakpoint at (1-based)"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            const notebook = getActiveNotebook(app);
            if (!notebook || !notebook.content) {
                return JSON.stringify({ error: "No active notebook found" });
            }

            try {
                const index = typeof args.index === "string" ? parseInt(args.index, 10) : args.index;
                const lineNumber = typeof args.lineNumber === "string" ? parseInt(args.lineNumber, 10) : args.lineNumber;

                if (index < 0 || index >= notebook.content.widgets.length) {
                    return JSON.stringify({ error: "Invalid cell index" });
                }

                if (!lineNumber || lineNumber < 1) {
                    return JSON.stringify({ error: "Invalid line number" });
                }

                // Get the cell content
                const cell = notebook.content.widgets[index];
                const code = cell.model.sharedModel.getSource();

                // Create breakpoint object
                const breakpoints = [{
                    line: lineNumber,
                    verified: false
                }];

                // Update breakpoints
                await debuggerService.updateBreakpoints(code, breakpoints);

                return JSON.stringify({
                    success: true,
                    message: "Breakpoints set successfully"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error setting breakpoints: ${error.message}`
                });
            }
        }
    };

    functions["clearBreakpoints"] = {
        "def": {
            "name": "clearBreakpoints",
            "description": "Clear all breakpoints in the notebook",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            try {
                await debuggerService.clearBreakpoints();

                return JSON.stringify({
                    success: true,
                    message: "All breakpoints cleared"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error clearing breakpoints: ${error.message}`
                });
            }
        }
    };

    // Stepping Through Code Functions

    functions["stepOver"] = {
        "def": {
            "name": "stepOver",
            "description": "Step over to the next line of code",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            if (!debuggerService.hasStoppedThreads()) {
                return JSON.stringify({ error: "Debugger is not paused at a breakpoint" });
            }

            try {
                await debuggerService.next();

                return JSON.stringify({
                    success: true,
                    message: "Stepped over to next line"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error stepping over: ${error.message}`
                });
            }
        }
    };

    functions["stepInto"] = {
        "def": {
            "name": "stepInto",
            "description": "Step into a function or method",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            if (!debuggerService.hasStoppedThreads()) {
                return JSON.stringify({ error: "Debugger is not paused at a breakpoint" });
            }

            try {
                await debuggerService.stepIn();

                return JSON.stringify({
                    success: true,
                    message: "Stepped into function"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error stepping into: ${error.message}`
                });
            }
        }
    };

    functions["stepOut"] = {
        "def": {
            "name": "stepOut",
            "description": "Step out of the current function or method",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            if (!debuggerService.hasStoppedThreads()) {
                return JSON.stringify({ error: "Debugger is not paused at a breakpoint" });
            }

            try {
                await debuggerService.stepOut();

                return JSON.stringify({
                    success: true,
                    message: "Stepped out of function"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error stepping out: ${error.message}`
                });
            }
        }
    };

    functions["continueExecution"] = {
        "def": {
            "name": "continueExecution",
            "description": "Continue execution until the next breakpoint or end of program",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            if (!debuggerService.hasStoppedThreads()) {
                return JSON.stringify({ error: "Debugger is not paused at a breakpoint" });
            }

            try {
                await debuggerService.continue();

                return JSON.stringify({
                    success: true,
                    message: "Execution continued"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error continuing execution: ${error.message}`
                });
            }
        }
    };

    functions["pauseExecution"] = {
        "def": {
            "name": "pauseExecution",
            "description": "Pause the execution of the current program",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            try {
                await debuggerService.pause();

                return JSON.stringify({
                    success: true,
                    message: "Execution paused"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error pausing execution: ${error.message}`
                });
            }
        }
    };

    // Variable Inspection Functions

    functions["evaluateExpression"] = {
        "def": {
            "name": "evaluateExpression",
            "description": "Evaluate an expression in the current debug context",
            "arguments": {
                "expression": {
                    "type": "string",
                    "name": "Expression to evaluate"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            if (!debuggerService.hasStoppedThreads()) {
                return JSON.stringify({ error: "Debugger is not paused at a breakpoint" });
            }

            try {
                const expression = args.expression;
                if (!expression) {
                    return JSON.stringify({ error: "No expression provided" });
                }

                const result = await debuggerService.evaluate(expression);

                return JSON.stringify({
                    success: true,
                    result: result
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error evaluating expression: ${error.message}`
                });
            }
        }
    };

    functions["inspectVariables"] = {
        "def": {
            "name": "inspectVariables",
            "description": "Get all variables in the current scope",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            try {
                await debuggerService.displayDefinedVariables();

                // Get the variables from the model
                const scopes = debuggerService.model.variables.scopes;

                return JSON.stringify({
                    success: true,
                    scopes: scopes
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error inspecting variables: ${error.message}`
                });
            }
        }
    };

    functions["inspectVariable"] = {
        "def": {
            "name": "inspectVariable",
            "description": "Inspect a specific variable by reference ID",
            "arguments": {
                "variableReference": {
                    "type": "integer",
                    "name": "Reference ID of the variable to inspect"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            try {
                const variableReference = args.variableReference;
                if (!variableReference) {
                    return JSON.stringify({ error: "No variable reference provided" });
                }

                // First, update the model by requesting the variable
                // We don't await this call to avoid hanging
                debuggerService.inspectVariable(variableReference);

                // Give the model a moment to update
                await new Promise(resolve => setTimeout(resolve, 100));

                // Return all variables from the model
                // The client can filter by variableReference if needed
                const allVariables = debuggerService.model.variables;

                return JSON.stringify({
                    success: true,
                    variables: allVariables
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error inspecting variable: ${error.message}`
                });
            }
        }
    };

    // Advanced Debugging Features

    functions["getCallStack"] = {
        "def": {
            "name": "getCallStack",
            "description": "Get the current call stack when execution is paused",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            if (!debuggerService.hasStoppedThreads()) {
                return JSON.stringify({ error: "Debugger is not paused at a breakpoint" });
            }

            try {
                const frames = debuggerService.model.callstack.frames;

                return JSON.stringify({
                    success: true,
                    callstack: frames
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error getting call stack: ${error.message}`
                });
            }
        }
    };

    functions["setPauseOnExceptions"] = {
        "def": {
            "name": "setPauseOnExceptions",
            "description": "Configure the debugger to pause on exceptions",
            "arguments": {
                "filter": {
                    "type": "string",
                    "name": "Exception type to pause on (e.g., 'uncaught' or 'raised')"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app || !debuggerService) {
                return JSON.stringify({ error: "JupyterLab app or debugger service not initialized" });
            }

            if (!debuggerService.isStarted) {
                return JSON.stringify({ error: "Debugger is not running" });
            }

            try {
                const filter = args.filter || "";

                if (!filter) {
                    return JSON.stringify({ error: "No filter provided" });
                }

                await debuggerService.pauseOnExceptionsFilter(filter);

                return JSON.stringify({
                    success: true,
                    message: "Exception breakpoints configured"
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error setting exception breakpoints: ${error.message}`
                });
            }
        }
    };

    functions["waitForDebugger"] = {
        "def": {
            "name": "waitForDebugger",
            "description": "Wait for either a breakpoint to be hit or cell execution to complete",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell being executed"
                },
                "maxWaitTime": {
                    "type": "integer",
                    "name": "Maximum time to wait in milliseconds",
                    "optional": true
                },
                "pollInterval": {
                    "type": "integer",
                    "name": "Interval between checks in milliseconds",
                    "optional": true
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            const { index, maxWaitTime = 10000, pollInterval = 100 } = args;

            const current = notebookTracker.currentWidget;
            if (!current) {
                return JSON.stringify({
                    error: "No active notebook"
                });
            }

            const tracked_notebook = current.content;
            if (index < 0 || index >= tracked_notebook.widgets.length) {
                return JSON.stringify({
                    error: "Invalid cell index"
                });
            }

            const cell = tracked_notebook.widgets[index];
            const startTime = Date.now();

            // Poll until timeout
            while (Date.now() - startTime < maxWaitTime) {
                // Check if the debugger has stopped at a breakpoint
                if (debuggerService?.isStarted && debuggerService.hasStoppedThreads()) {
                    const elapsedTime = Date.now() - startTime;
                    return JSON.stringify({
                        completed: false,
                        breakpointHit: true,
                        timedOut: false,
                        elapsedTime
                    });
                }

                // Check if execution completed
                if ((cell as CodeCell).model.executionState === 'idle') {
                    const elapsedTime = Date.now() - startTime;
                    return JSON.stringify({
                        completed: true,
                        breakpointHit: false,
                        timedOut: false,
                        elapsedTime
                    });
                }

                // Wait before checking again
                await new Promise(resolve => setTimeout(resolve, pollInterval));
            }

            // If we reached here, we timed out
            const elapsedTime = Date.now() - startTime;
            return JSON.stringify({
                completed: false,
                breakpointHit: false,
                timedOut: true,
                elapsedTime
            });
        }
    };
}
