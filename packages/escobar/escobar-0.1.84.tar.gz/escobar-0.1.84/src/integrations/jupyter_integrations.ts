import { JupyterFrontEnd } from '@jupyterlab/application';
import { Contents } from '@jupyterlab/services';
import { NotebookPanel, NotebookModel, NotebookActions } from '@jupyterlab/notebook';
import { Cell, CellModel, ICellModel, CodeCell, MarkdownCell } from '@jupyterlab/cells';
import { ICodeCellModel, IMarkdownCellModel } from '@jupyterlab/cells';
import { callPython, registerFunction, get_ws } from '../voitta/pythonBridge_browser'
import { Widget } from '@lumino/widgets';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { FileEditor } from '@jupyterlab/fileeditor';
import { MainAreaWidget } from '@jupyterlab/apputils';
import { IDocumentWidget } from '@jupyterlab/docregistry';

import { init_fs, ensurePathExists } from "./jupyter_integrations_fs"
import { init_terminal, findTerminalByName } from "./jupyter_integrations_terminal"
import { init_cells } from "./jupyter_integrations_cells"
import { init_output } from "./jupyter_integrations_output"
import { init_settings } from "./jupyter_integrations_settings"
import { init_diff } from "./jupyter_integrations_diff"
import { init_debugger } from "./jupyter_integrations_debugger"

import { INotebookTracker } from '@jupyterlab/notebook'
import { IDebugger } from '@jupyterlab/debugger';

export var streamingState = {}

export var app: JupyterFrontEnd | undefined;
export var notebookTracker: INotebookTracker | undefined;
export var debuggerService: IDebugger | undefined;
export var memoryBank = {};

export const functions = {}
init_fs()
init_terminal()
init_cells()
init_output()
init_settings()
init_diff()
init_debugger()

const O: { [key: string]: (...args: any[]) => any } = {};

var functions_registred = false;

/**
 * Get the currently active notebook panel using the app
 */
export function getActiveNotebook(jupyterApp: JupyterFrontEnd): NotebookPanel | null {
  const { shell } = jupyterApp;
  const widget = shell.currentWidget;

  if (!widget) {
    return null;
  }

  // Check if the current widget is a notebook panel
  if (widget instanceof NotebookPanel) {
    return widget;
  }

  return null;
}

/**
 * Get the currently active notebook panel using the notebookTracker
 */
export function getActiveNotebookFromTracker(): NotebookPanel | null {
  if (!notebookTracker) {
    return null;
  }

  return notebookTracker.currentWidget;
}

/**
 * Validate a cell index in a notebook
 */
export function validateCellIndex(notebook: NotebookPanel, index: number): boolean {
  if (!notebook || !notebook.content) {
    return false;
  }

  const count = notebook.content.widgets.length;
  return index >= 0 && index < count;
}

export async function register_functions(
  _app: JupyterFrontEnd,
  _notebookTracker: INotebookTracker,
  _debuggerService: IDebugger
) {
  console.log("=============== register_functions ===============");
  app = _app;
  notebookTracker = _notebookTracker;
  debuggerService = _debuggerService;


  for (const name of Object.keys(functions)) {
    console.log("register function:", name);
    registerFunction(name, true, functions[name]["func"], functions[name], true);
  }
}

export async function get_tools(app: JupyterFrontEnd,
  notebookTracker: INotebookTracker, debuggerService: IDebugger) {
  if (!(functions_registred)) {
    await register_functions(app, notebookTracker, debuggerService);
    functions_registred = true;
  }
  const tools = [];
  for (const func of Object.values(functions)) {
    tools.push(func["def"]);
  }
  return tools;
}


export async function get_opened_tabs(): Promise<any[]> {
  const mainAreaWidgets = app.shell.widgets('main');

  const currentWidget = app.shell.currentWidget;

  const openedTabs = [];
  //const widgets = []


  Array.from(mainAreaWidgets).forEach(widget => {
    let tabInfo = {
      id: widget.id,
      title: widget.title.label || 'Untitled',
      type: 'unknown',
      isVisible: false
    };



    // Determine widget type
    if (widget instanceof NotebookPanel) {
      tabInfo.type = 'notebook';
      tabInfo['path'] = (widget.context?.path) || '';
    } else if (widget instanceof FileEditor ||
      (widget as any).context?.path?.includes('.')) {
      tabInfo.type = 'file';
      tabInfo['path'] = (widget as any).context?.path || '';
    } else if (widget.id.startsWith('terminal') ||
      widget.title?.label?.toLowerCase().includes('terminal')) {
      tabInfo.type = 'terminal';
      tabInfo['name'] = widget.title.label.replace('Terminal ', '') || '';
    }

    tabInfo["isVisible"] = widget.isVisible;
    openedTabs.push(tabInfo);

  });

  return openedTabs;
}



functions["listAvailableKernels"] = {
  "def": {
    "name": "listAvailableKernels",
    "description": "Lists kernels (such as python) available on the system",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    const kernelSpecs = await app.serviceManager.kernelspecs.refreshSpecs();
    await app.serviceManager.kernelspecs.refreshSpecs();
    const specs = app.serviceManager.kernelspecs.specs?.kernelspecs;

    const result = Object.values(specs).map(spec => ({
      name: spec.name,
      display_name: spec.display_name,
      language: spec.language
    }));

    return JSON.stringify(result);
  }
}


functions["createAndOpenNotebook"] = {
  "def": {
    "name": "createAndOpenNotebook",
    "description": "Creates and opens a new notebook",
    "arguments": {
      "name": {
        "type": "string",
        "name": "Name for the new notebook"
      },
      "kernelName": {
        "type": "string",
        "name": "Name of kernel to use"
      }
    }
  },
  "func": async (args: any): Promise<string> => {
    let name = args["name"];
    const kernelName = args["kernelName"];
    const contents = app.serviceManager.contents;
    const kernelspecs = app.serviceManager.kernelspecs.specs?.kernelspecs;

    if (!name.endsWith('.ipynb')) {
      name += '.ipynb';
    }

    const path = name.startsWith('./') ? name.slice(2) : name;

    // Get display_name and language from kernel specs (fallback to name)
    const kernelSpec = kernelspecs?.[kernelName];
    const displayName = kernelSpec?.display_name ?? kernelName;
    const language = kernelSpec?.language ?? "python";

    try {
      await contents.get(path);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // Notebook doesn't exist — create with metadata
        await contents.save(path, {
          type: 'notebook',
          format: 'json',
          content: {
            cells: [],
            metadata: {
              kernelspec: {
                name: kernelName,
                display_name: displayName,
                language: language
              }
            },
            nbformat: 4,
            nbformat_minor: 5
          }
        });
      } else {
        console.error(err);
        return "There was an error retrieving notebook info.";
      }
    }

    // Open the notebook and attach the kernel
    await app.commands.execute('docmanager:open', {
      path,
      factory: 'Notebook',
      options: {
        kernel: {
          name: kernelName
        }
      }
    });

    return "done";
  }
};



functions["openNotebook"] = {
  "def": {
    "name": "openNotebook",
    "description": "Opens an existing notebook",
    "arguments": {
      "name": {
        "type": "string",
        "name": "Name for the notebook to open"
      }
    }
  },
  "func": async (args: any): Promise<string> => {
    const name = args.name;
    const contents = app.serviceManager.contents;

    try {
      await contents.get(name);
    } catch (err) {
      return `Notebook ${name} does not exit`
    }

    await app.commands.execute('docmanager:open', {
      path: name,
      factory: 'Notebook'
    });
    return "done";
  }
}


functions["restartKernel"] = {
  "def": {
    "name": "restartKernel",
    "description": "Restart the kernel of the active notebook",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.sessionContext) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Restart the kernel
      if (notebook.sessionContext.session?.kernel) {
        await notebook.sessionContext.session.kernel.restart();
      } else {
        throw new Error("No kernel available to restart");
      }

      return JSON.stringify({
        success: true,
        message: "Kernel restarted successfully"
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error restarting kernel: ${error.message}`
      });
    }
  }
}

functions["stopExecution"] = {
  "def": {
    "name": "stopExecution",
    "description": "Stop the execution of the active notebook by interrupting the kernel",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.sessionContext) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Interrupt the kernel
      await notebook.sessionContext.session?.kernel?.interrupt();

      return JSON.stringify({
        success: true,
        message: "Execution interrupted"
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error interrupting kernel: ${error.message}`
      });
    }
  }
}

functions["getCurrentNotebook"] = {
  "def": {
    "name": "getCurrentNotebook",
    "description": "Gets information about the currently open notebook",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.content) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Get notebook information
      const context = notebook.context;
      const model = notebook.model;
      const path = context.path;
      const name = path.split('/').pop() || '';
      const dirty = context.model.dirty;

      // Get basic metadata if available
      let metadata = {};
      if (model && (model as NotebookModel).metadata) {
        // Just include a simplified version of metadata
        try {
          const nbModel = model as NotebookModel;
          // Create a simple object with basic metadata properties
          metadata = {
            kernelName: nbModel.metadata.kernelName || '',
            kernelLanguage: nbModel.metadata.kernelLanguage || '',
            // Add other metadata properties as needed
          };
        } catch (err) {
          console.error('Error extracting notebook metadata:', err);
        }
      }

      return JSON.stringify({
        success: true,
        notebook: {
          path: path,
          name: name,
          dirty: dirty,
          metadata: metadata,
          cell_count: model.cells.length
        }
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error getting notebook information: ${error.message}`
      });
    }
  }
}

functions["getKernelState"] = {
  "def": {
    "name": "getKernelState",
    "description": "Get the state of the kernel and information about any currently executing cell",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.sessionContext) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      const session = notebook.sessionContext.session;
      const kernel = session?.kernel;

      if (!kernel) {
        return JSON.stringify({
          success: true,
          kernel_state: "no_kernel",
          executing: false
        });
      }

      // Get kernel status
      const status = kernel.status;

      // Check for executing cells
      const executingCells = [];
      const cells = notebook.content.widgets;

      for (let i = 0; i < cells.length; i++) {
        const cell = cells[i];
        if (cell instanceof CodeCell && cell.model.executionCount !== null && cell.hasClass('jp-mod-executing')) {
          executingCells.push({
            index: i,
            execution_count: cell.model.executionCount
          });
        }
      }

      return JSON.stringify({
        success: true,
        kernel_state: status,
        executing: status === 'busy',
        executing_cells: executingCells
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error getting kernel state: ${error.message}`
      });
    }
  }
}


// intraspection

/*

functions["getActiveTabInfo"] = {
  "def": {
    "name": "getActiveTabInfo",
    "description": "Get the info on current tab",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    const widget = app.shell.currentWidget;

    if (!widget) return null;

    // Debug information to understand widget properties
    console.log("Widget debug info:", {
      id: widget.id,
      constructorName: widget.constructor.name,
      hasContext: !!(widget as any).context,
      hasPath: !!(widget as any).context?.path,
      hasSession: !!(widget as any).sessionContext?.session,
      title: widget.title?.label || 'No title',
      className: widget.node?.className || 'No class',
      nodeType: widget.node?.nodeName || 'No node type'
    });

    // 📓 Notebook
    if (widget instanceof NotebookPanel) {
      return JSON.stringify({
        type: 'notebook',
        name: widget.context.path
      });
    }

    // 📝 Text/File Editor - Enhanced detection
    if (
      widget instanceof FileEditor ||
      widget.id.startsWith('editor') ||
      (widget as any).context?.path?.includes('.') || // Files typically have extensions
      ((widget as any).editor && (widget as any).context) // Editor widgets typically have both editor and context
    ) {
      const context = (widget as any).context;
      return JSON.stringify({
        type: 'file',
        name: context?.path ?? widget.id
      });
    }

    // 💻 Terminal - Enhanced detection
    if (
      widget.id.startsWith('terminal') ||
      widget.title?.label?.toLowerCase().includes('terminal') ||
      widget.node?.className?.includes('jp-Terminal') ||
      ((widget as any).session && !(widget as any).context?.path) // Terminals have sessions but no file paths
    ) {
      // Get all running terminals to find the matching one
      const terminals = app.serviceManager.terminals;
      const runningIterator = terminals.running();
      const running = Array.from(runningIterator);

      // Log available terminals for debugging
      console.log("Terminal widget detected:", {
        id: widget.id,
        title: widget.title?.label,
        className: widget.node?.className
      });

      console.log("Available terminals:", running.map(term => ({
        name: term.name
      })));

      // Extract terminal name/ID - try different methods
      let terminalName = '';

      // Method 1: Extract from widget.id (traditional method)
      if (widget.id.startsWith('terminal:')) {
        terminalName = widget.id.replace('terminal:', '');
        console.log("Terminal name from widget.id:", terminalName);
      }

      // Method 2: Use title label if available
      if (!terminalName && widget.title?.label) {
        // Sometimes the title contains the terminal number like "Terminal 1"
        const match = widget.title.label.match(/Terminal\s+(\d+)/i);
        if (match && match[1]) {
          terminalName = match[1];
          console.log("Terminal name from title label:", terminalName);
        }
      }

      // Method 3: Look for session name if available
      if (!terminalName && (widget as any).session?.name) {
        terminalName = (widget as any).session.name;
        console.log("Terminal name from session name:", terminalName);
      }

      // Method 4: If we have only one terminal running, use that
      if (!terminalName && running.length === 1) {
        terminalName = running[0].name;
        console.log("Using only available terminal:", terminalName);
      }

      // Fallback to a default if we couldn't determine the name
      if (!terminalName) {
        terminalName = '1'; // Default to first terminal as fallback
        console.log("Using fallback terminal name:", terminalName);
      }

      return JSON.stringify({
        type: 'terminal',
        name: terminalName
      });
    }

    // ❓ Other / Unknown widget - Include more debug info
    return JSON.stringify({
      type: widget.constructor.name.toLowerCase(),
      name: widget.id,
      debug: {
        className: widget.node?.className,
        title: widget.title?.label,
        hasContext: !!(widget as any).context,
        hasSession: !!(widget as any).sessionContext?.session
      }
    });
  }
}

functions["getActiveCell"] = {
  "def": {
    "name": "getActiveCell",
    "description": "Get the index and content of the currently selected cell",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.content) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Get the active cell index
      const activeCellIndex = notebook.content.activeCellIndex;

      // Validate the index
      if (!validateCellIndex(notebook, activeCellIndex)) {
        return JSON.stringify({ error: `Invalid active cell index: ${activeCellIndex}` });
      }

      // Get the active cell
      const activeCell = notebook.content.widgets[activeCellIndex];

      // Get the cell type and content
      let cellType = 'unknown';
      if (activeCell instanceof CodeCell) {
        cellType = 'code';
      } else if (activeCell instanceof MarkdownCell) {
        cellType = 'markdown';
      } else {
        cellType = 'raw';
      }

      const cellContent = activeCell.model.sharedModel.getSource();

      return JSON.stringify({
        success: true,
        active_cell: {
          index: activeCellIndex,
          type: cellType,
          content: cellContent
        }
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error getting active cell: ${error.message}`
      });
    }
  }
}

functions["getExecutedCells"] = {
  "def": {
    "name": "getExecutedCells",
    "description": "Get information about executed cells in the notebook, including their execution order. This funcion does not return the outputs of the cells!",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.content) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      const executedCells = [];
      const cells = notebook.content.widgets;

      // Collect all cells that have been executed (have an execution count)
      for (let i = 0; i < cells.length; i++) {
        const cell = cells[i];
        if (cell instanceof CodeCell) {
          const executionCount = cell.model.executionCount;

          // Only include cells that have been executed
          if (executionCount !== null) {
            executedCells.push({
              index: i,
              execution_count: executionCount,
              content: cell.model.sharedModel.getSource(),
              type: 'code'
            });
          }
        }
      }

      // Sort by execution count to get execution order
      executedCells.sort((a, b) => a.execution_count - b.execution_count);

      return JSON.stringify({
        success: true,
        executed_cells: executedCells,
        execution_order: executedCells.map(cell => cell.index)
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error getting executed cells: ${error.message}`
      });
    }
  }
  
}
*/
