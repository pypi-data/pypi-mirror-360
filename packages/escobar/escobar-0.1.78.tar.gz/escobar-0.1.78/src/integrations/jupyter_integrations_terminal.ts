import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, functions } from './jupyter_integrations'
import { generateUUID } from '../voitta/pythonBridge_browser'


function stripAnsi(text: any): string {
    return text.replace(
        // ANSI escape sequence pattern
        /\x1b\[[0-9;?]*[a-zA-Z]/g,
        ''
    );
}

const max_stdout_return = 16000
const min_stdout_return = 16 // if no text after the marker, return the text before it

export async function findTerminalByName(
    app: JupyterFrontEnd,
    name: string
): Promise<ReturnType<typeof app.serviceManager.terminals.connectTo> | null> {
    const { terminals } = app.serviceManager;

    await terminals.ready;

    const runningIterator = await terminals.running();
    // Convert to array for easier manipulation
    const running = Array.from(runningIterator);

    // Log all available terminals for debugging
    console.log("All available terminals:", running.map(term => ({
        name: term.name
    })));
    console.log("Looking for terminal with name:", name);

    // First try exact match
    for (const term of running) {
        if (term.name === name) {
            console.log("Found exact terminal match:", term.name);
            return terminals.connectTo({ model: term });
        }
    }

    // If no exact match, try numeric match (in case name is just a number)
    if (/^\d+$/.test(name)) {
        for (const term of running) {
            // Check if the terminal name contains the number
            if (term.name.includes(name)) {
                console.log("Found numeric terminal match:", term.name, "for input:", name);
                return terminals.connectTo({ model: term });
            }
        }
    }

    // If still no match and we only have one terminal, use that one
    if (running.length === 1) {
        console.log("No match found but only one terminal exists, using:", running[0].name);
        return terminals.connectTo({ model: running[0] });
    }

    console.log("No terminal found with name:", name);
    return null;
}

function extractBetweenMarkers(text: string, marker: string): string {
    const start = text.indexOf(marker);

    if (start === -1) {
        return ''; // Marker not found
    }

    const end = text.indexOf(marker, start + marker.length);

    if (end === -1) {
        // Only one occurrence found
        const afterMarker = text.substring(start + marker.length).trim();
        if (afterMarker.length < min_stdout_return) {
            return text.substring(0, start).slice(-max_stdout_return).trim(); // Return text before the marker
        } else {
            return afterMarker.slice(-max_stdout_return);
        }
    }

    const betweenText = text.substring(start + marker.length, end).trim();
    return betweenText.slice(-max_stdout_return);
}


// Map to store terminal outputs for async terminals
const terminalOutputs: { [key: string]: string } = {};

export function init_terminal() {
    functions["startTerminal"] = {
        "def": {
            "name": "startTerminal",
            "description": "Opens a command line terminal",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            const terminals = app.serviceManager.terminals;
            const name = "";

            const session = await terminals.startNew();

            await app.commands.execute('terminal:open', { name: session.name });

            terminalOutputs[session.name] = ""

            const listener = (_, msg: any) => {
                if (msg.type === 'stdout') {
                    if (Array.isArray(msg.content)) {
                        for (var i = 0; i < msg.content.length; i++) {
                            const content = stripAnsi(msg.content[i]);
                            terminalOutputs[session.name] += content;
                        }
                    }
                }
            };

            // Connect the listener
            session.messageReceived.connect(listener);



            return JSON.stringify({ "staus": "ok", "terminal_name": session.name })

        }
    }

    functions["runCommandInTerminal"] = {
        "def": {
            "name": "runCommandInTerminal",
            "description": "Runs a command in a terminal. This will block until the command ends, only use for very short-lived tasks!",
            "arguments": {
                "name": {
                    "type": "string",
                    "name": "Name for the terminal to run the command in"
                },
                "command": {
                    "type": "string",
                    "name": "Command to run in the terminal. Make sure to properly escape control sequnces like '!' "
                },
                "timeout": {
                    "type": "integer",
                    "name": "Timeout in milliseconds, default 10000"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            let name = args["name"] || "";
            const command = args["command"] || "";
            const timeout = args["timeout"] || 60000;

            console.log(`Attempting to run command in terminal: ${name}`);

            // If name is a JSON string (from getActiveTabInfo), parse it
            if (name.startsWith('{') && name.endsWith('}')) {
                try {
                    const parsed = JSON.parse(name);
                    if (parsed.name) {
                        name = parsed.name;
                        console.log(`Parsed terminal name from JSON: ${name}`);
                    }
                } catch (e) {
                    console.log(`Failed to parse terminal name as JSON: ${e.message}`);
                }
            }

            const { terminals } = app.serviceManager;

            // If no name provided, try to use the first available terminal
            if (!name) {
                const runningIterator = await terminals.running();
                const running = Array.from(runningIterator);
                if (running.length > 0) {
                    name = running[0].name;
                    console.log(`No terminal name provided, using first available: ${name}`);
                } else {
                    // No terminals available, create a new one
                    console.log("No terminals available, creating a new one");
                    const session = await terminals.startNew();
                    name = session.name;
                    await app.commands.execute('terminal:open', { name: name });
                    // Wait a bit for the terminal to initialize
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }

            const term = await findTerminalByName(app, name);
            if (term === null) {
                return JSON.stringify({
                    "status": "failure",
                    "message": `Terminal with name ${name} not found`
                });
            }

            // Make sure the terminal is open and visible
            await app.commands.execute('terminal:open', { name: name });

            // Send the command

            const signature = generateUUID();

            const commandPromise = new Promise<void>((resolve) => {
                const listener = (_, msg: any) => {
                    if (msg.type === 'stdout') {
                        if (Array.isArray(msg.content)) {
                            for (var i = 0; i < msg.content.length; i++) {
                                const content = stripAnsi(msg.content[i]);
                                stdout += content;
                                // Check if __TERMINATOR__ is in the output
                                if (content.includes(`__${signature}__`)) {
                                    isTerminated = true;
                                    resolve();
                                }
                            }
                        } else {
                            console.log("> >", msg);
                        }
                    } else {
                        console.log("> >", msg);
                    }
                };

                // Connect the listener
                term.messageReceived.connect(listener);
            });

            const timeoutPromise = new Promise<void>(resolve => setTimeout(resolve, timeout));

            var stdout = "";
            var isTerminated = false;

            term.send({
                type: 'stdin',
                content: [`${command} ; echo "cwd: $(pwd)"; echo __${signature}__ \n`]
            });

            await Promise.race([commandPromise, timeoutPromise]);

            const clean_stdout = extractBetweenMarkers(stdout, `__${signature}__`)

            return JSON.stringify({
                "status": "success",
                "stop": isTerminated ? "natural" : "timeout",
                "result": clean_stdout.trim()
            });
        }
    }

    functions["runCommandInTerminalAsync"] = {
        "def": {
            "name": "runCommandInTerminalAsync",
            "description": `Runs a command in a terminal without waiting for completion. 
            Returns immediately with 'ok' status. 
            Use this for long-running commands where you don't need to wait for the result.
            Always check the terminal output before sending new commands to this terminal!`,
            "arguments": {
                "name": {
                    "type": "string",
                    "name": "Name for the terminal to run the command in"
                },
                "command": {
                    "type": "string",
                    "name": "Command to send to the terminal. Mak sur to proprly escape contol sequences like '!' "
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            let name = args["name"] || "";
            const command = args["command"] || "";

            console.log(`Attempting to run command asynchronously in terminal: ${name}`);

            // If name is a JSON string (from getActiveTabInfo), parse it
            if (name.startsWith('{') && name.endsWith('}')) {
                try {
                    const parsed = JSON.parse(name);
                    if (parsed.name) {
                        name = parsed.name;
                        console.log(`Parsed terminal name from JSON: ${name}`);
                    }
                } catch (e) {
                    console.log(`Failed to parse terminal name as JSON: ${e.message}`);
                }
            }

            const { terminals } = app.serviceManager;

            // If no name provided, try to use the first available terminal
            if (!name) {
                const runningIterator = await terminals.running();
                const running = Array.from(runningIterator);
                if (running.length > 0) {
                    name = running[0].name;
                    console.log(`No terminal name provided, using first available: ${name}`);
                } else {
                    // No terminals available, create a new one
                    console.log("No terminals available, creating a new one");
                    const session = await terminals.startNew();
                    name = session.name;
                    await app.commands.execute('terminal:open', { name: name });
                    // Wait a bit for the terminal to initialize
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }

            const term = await findTerminalByName(app, name);
            if (term === null) {
                return JSON.stringify({
                    "status": "failure",
                    "message": `Terminal with name ${name} not found`
                });
            }

            // Make sure the terminal is open and visible
            await app.commands.execute('terminal:open', { name: name });

            // Initialize or clear the output buffer for this terminal
            //terminalOutputs[name] = "";

            // Send the command without waiting for completion
            term.send({
                type: 'stdin',
                content: [`${command}\n`]
            });

            // Return immediately
            return JSON.stringify({
                "status": "success",
                "message": "Command sent to terminal"
            });
        }
    }

    functions["sendCommandToAsyncTerminal"] = {
        "def": {
            "name": "sendCommandToAsyncTerminal",
            "description": "Sends a command to an existing async terminal without waiting for completion. Use this to send additional commands to terminals started with runCommandInTerminalAsync.",
            "arguments": {
                "name": {
                    "type": "string",
                    "name": "Name of the terminal to send the command to"
                },
                "command": {
                    "type": "string",
                    "name": "Command to send to the terminal"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            let name = args["name"] || "";
            const command = args["command"] || "";

            console.log(`Sending command to async terminal: ${name}`);

            // If name is a JSON string (from getActiveTabInfo), parse it
            if (name.startsWith('{') && name.endsWith('}')) {
                try {
                    const parsed = JSON.parse(name);
                    if (parsed.name) {
                        name = parsed.name;
                        console.log(`Parsed terminal name from JSON: ${name}`);
                    }
                } catch (e) {
                    console.log(`Failed to parse terminal name as JSON: ${e.message}`);
                }
            }

            const term = await findTerminalByName(app, name);
            if (term === null) {
                return JSON.stringify({
                    "status": "failure",
                    "message": `Terminal with name ${name} not found`
                });
            }

            // Make sure the terminal is open and visible
            await app.commands.execute('terminal:open', { name: name });

            // Send the command without waiting for completion
            term.send({
                type: 'stdin',
                content: [`${command}\n`]
            });

            // Return immediately
            return JSON.stringify({
                "status": "success",
                "message": "Command sent to terminal"
            });
        }
    }

    functions["getAsyncTerminalOutput"] = {
        "def": {
            "name": "getAsyncTerminalOutput",
            "description": "Retrieves the current output from an async terminal. Use this to check progress or results from terminals started with runCommandInTerminalAsync.",
            "arguments": {
                "name": {
                    "type": "string",
                    "name": "Name of the terminal to get output from"
                },
                "clear": {
                    "type": "boolean",
                    "name": "Whether to clear the output buffer after retrieving (default: false)"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            let name = args["name"] || "";
            const clear = args["clear"] || false;

            // If name is a JSON string (from getActiveTabInfo), parse it
            if (name.startsWith('{') && name.endsWith('}')) {
                try {
                    const parsed = JSON.parse(name);
                    if (parsed.name) {
                        name = parsed.name;
                        console.log(`Parsed terminal name from JSON: ${name}`);
                    }
                } catch (e) {
                    console.log(`Failed to parse terminal name as JSON: ${e.message}`);
                }
            }

            const term = await findTerminalByName(app, name);
            if (term === null) {
                return JSON.stringify({
                    "status": "failure",
                    "message": `Terminal with name ${name} not found`
                });
            }

            // Get the current output
            const output = terminalOutputs[name] || "";

            // Clear the output buffer if requested
            if (clear) {
                terminalOutputs[name] = "";
            }

            return JSON.stringify({
                "status": "success",
                "output": output
            });
        }
    }
}
