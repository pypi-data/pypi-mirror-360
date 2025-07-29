import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, notebookTracker, functions, debuggerService } from './jupyter_integrations'
import { getActiveNotebook, validateCellIndex } from "./jupyter_integrations"
import { Cell, CellModel, ICellModel, CodeCell, MarkdownCell } from '@jupyterlab/cells';
import { ensurePathExists } from './jupyter_integrations_fs';

import { Notebook, NotebookPanel, NotebookModel, NotebookActions } from '@jupyterlab/notebook';

import { streamingState } from "./jupyter_integrations"

import { voittal_call_log } from "../voitta/pythonBridge_browser"


import {
    JupyterFrontEndPlugin
} from '@jupyterlab/application';



function insert_cell(tracked_notebook: Notebook, cellType: string, index: number) {
    var newCellIndex = index;
    if (index <= 0) {
        tracked_notebook.activeCellIndex = 0;
        NotebookActions.insertAbove(tracked_notebook);
        newCellIndex = 0;
        tracked_notebook.activeCellIndex = newCellIndex;
        NotebookActions.changeCellType(tracked_notebook, cellType);
    } else {
        tracked_notebook.activeCellIndex = index - 1;
        NotebookActions.insertBelow(tracked_notebook);
        newCellIndex = index;
        tracked_notebook.activeCellIndex = newCellIndex;
        NotebookActions.changeCellType(tracked_notebook, cellType);
    }
    return newCellIndex;
}

function waitForEditorSync(activeCell: Cell): Promise<void> {
    return new Promise((resolve) => {
        // Wait for next animation frame to ensure DOM updates
        requestAnimationFrame(() => {
            // Then wait for next tick to ensure editor processing
            setTimeout(resolve, 0);
        });
    });
}


export function init_cells() {
    functions["insertExecuteCell"] = {
        "def": {
            "name": "insertExecuteCell",
            "description": "Index at which to place the new cell",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "New cel lindex"
                },
                "cellType": {
                    "type": "string",
                    "name": "Type of the cell being edited (code/markdown)"
                },
                "content": {
                    "type": "string",
                    "name": "New content for the cell"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            var { index, cellType, content } = args;
            const current = notebookTracker.currentWidget

            app.shell.activateById(current.id)

            const tracked_notebook = current.content;
            index = typeof index === "string" ? parseInt(index, 10) : index;

            // console.log(streaming, call_id, args, index)

            var newCellIndex = index <= 0 ? 0 : index;

            if (streamingState[call_id] == undefined) {
                streamingState[call_id] = index;
                insert_cell(tracked_notebook, cellType, index);
            } else {
                tracked_notebook.activeCellIndex = newCellIndex;
            }
            if (tracked_notebook.mode != "edit") {
                tracked_notebook.activate();
                tracked_notebook.mode = 'edit';
            }


            if (streaming) {
                const activeCell = tracked_notebook.activeCell;

                //if (streamingState[call_id] == undefined) {
                activeCell.node.scrollIntoView({ behavior: 'smooth', block: 'end' });
                //}


                activeCell.model.sharedModel.setSource(args["content"]);
                if (activeCell instanceof MarkdownCell) {
                    activeCell.rendered = true;
                }
            } else {
                const activeCell = tracked_notebook.activeCell;
                //tracked_notebook.activeCellIndex = newCellIndex;
                //const activeCell = tracked_notebook.activeCell;

                // Scroll to the cell being inserted
                if (voittal_call_log[call_id] == undefined) {
                    activeCell.node.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }

                activeCell.model.sharedModel.setSource(args["content"]);

                tracked_notebook.mode = "command"

                if (activeCell instanceof MarkdownCell) {
                    activeCell.rendered = true;
                    await current.context.save();
                    return "ok"
                } else {
                    const ststus = await NotebookActions.run(tracked_notebook, current.sessionContext)
                    const executionOutput = await functions["getCellOutput"].func({
                        index: index,
                        scroll: false
                    });

                    // Scroll to the output area after execution
                    if (activeCell instanceof CodeCell) {
                        activeCell.outputArea.node.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    }

                    await current.context.save();
                    return executionOutput;
                }

            }

            return "ok"
        }
    }

    functions["editExecuteCell"] = {
        "def": {
            "name": "editExecuteCell",
            "description": "Edit the content of a cell by index and execute (render) it. Do not use if no edits required",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to edit"
                },
                "cellType": {
                    "type": "string",
                    "name": "Type of the cell being edited"
                },
                "content": {
                    "type": "string",
                    "name": "New content for the cell"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            var { index, cellType, content } = args;
            index = typeof index === "string" ? parseInt(index, 10) : index;

            try {
                const current = notebookTracker.currentWidget

                app.shell.activateById(current.id)

                const tracked_notebook = current.content;
                tracked_notebook.activeCellIndex = index;

                const activeCell = tracked_notebook.activeCell;

                //if (voittal_call_log[call_id] == undefined) {
                activeCell.node.scrollIntoView({ behavior: 'smooth', block: 'end' });
                //}

                // Clear outputs if it's a code cell before making edits
                if (activeCell instanceof CodeCell) {
                    NotebookActions.clearOutputs(tracked_notebook);
                }

                NotebookActions.changeCellType(tracked_notebook, cellType);

                if (tracked_notebook.mode != "edit") {
                    tracked_notebook.activate();
                    tracked_notebook.mode = 'edit';
                }

                activeCell.model.sharedModel.setSource(args["content"]);

                if (activeCell instanceof MarkdownCell) {
                    activeCell.rendered = true;
                    return "ok"
                } else {
                    if (!(streaming)) {
                        await current.context.save();
                        const ststus = await NotebookActions.run(tracked_notebook, current.sessionContext)
                        const executionOutput = await functions["getCellOutput"].func({
                            index: index,
                            scroll: true
                        });

                        // Scroll to the output area after execution
                        //if (activeCell instanceof CodeCell) {
                        //    activeCell.outputArea.node.scrollIntoView({ behavior: 'smooth', block: 'end' });
                        //}

                        return executionOutput;
                    } else {
                        return "ok"
                    }
                }
            } catch (error) {
                return JSON.stringify({
                    error: `Error editing cell: ${error.message}`
                });

            }
        }
    }
    functions["executeCell"] = {
        "def": {
            "name": "executeCell",
            "description": "Execute a cell by index. Use when no code change were made to the cell",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to execute"
                },
                "maxWaitTime": {
                    "type": "integer",
                    "name": "Maximum time to wait for execution or breakpoint (ms)",
                    "optional": true
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            var { index, maxWaitTime } = args;
            index = typeof index === "string" ? parseInt(index, 10) : index;
            maxWaitTime = typeof maxWaitTime === "string" ? parseInt(maxWaitTime, 10) : maxWaitTime;

            const current = notebookTracker.currentWidget;
            if (!current) {
                return JSON.stringify({ error: "No active notebook" });
            }

            app.shell.activateById(current.id);
            const tracked_notebook = current.content;
            tracked_notebook.activeCellIndex = index;
            const activeCell = tracked_notebook.activeCell;

            // Scroll to the cell itself at the beginning of execution
            activeCell.node.scrollIntoView({ behavior: 'smooth', block: 'center' });

            if (activeCell instanceof MarkdownCell) {
                activeCell.rendered = true;
                return "ok";
            } else {
                // Start the execution
                NotebookActions.run(tracked_notebook, current.sessionContext);

                // Wait for execution to complete or breakpoint to be hit
                const waitResult = await functions["waitForDebugger"].func({
                    index,
                    maxWaitTime
                });

                // Parse the result
                const result = JSON.parse(waitResult);

                if (result.completed) {
                    // Execution completed normally, get the output
                    const executionOutput = await functions["getCellOutput"].func({
                        index: index,
                        scroll: false
                    });

                    // If it's a code cell, scroll to its output area
                    if (activeCell instanceof CodeCell) {
                        activeCell.outputArea.node.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }

                    return executionOutput;
                } else if (result.breakpointHit) {
                    // Breakpoint was hit, return status
                    return JSON.stringify({
                        success: true,
                        message: "Execution paused at breakpoint",
                        debuggerPaused: true,
                        elapsedTime: result.elapsedTime
                    });
                } else {
                    // Timed out
                    return JSON.stringify({
                        success: true,
                        message: "Execution started, but neither completed nor hit a breakpoint within timeout period",
                        debuggerPaused: false,
                        timedOut: true,
                        elapsedTime: result.elapsedTime
                    });
                }
            }
        }
    }

    functions["getCellOutput"] = {
        "def": {
            "name": "getCellOutput",
            "description": "Get the output of a cell by index",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to get output from"
                }
            }
        },
        "func": async (args: any): Promise<any> => {
            var { index, scroll } = args;
            index = typeof index === "string" ? parseInt(index, 10) : index;
            // Default scroll to true if not specified
            scroll = scroll === false ? false : true;

            const current = notebookTracker.currentWidget

            app.shell.activateById(current.id)

            const tracked_notebook = current.content;

            tracked_notebook.activeCellIndex = index;
            const activeCell = tracked_notebook.activeCell;

            // Scroll to the cell whose output is being inspected only if scroll is true
            if (scroll) {
                activeCell.node.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            if (activeCell instanceof CodeCell) {
                const outputArea = activeCell.outputArea;
                const outputs = [];
                for (let i = 0; i < outputArea.model.length; i++) {
                    const output = outputArea.model.get(i);
                    console.log(`Output is array: ${Array.isArray(output)}`)
                    console.log(JSON.stringify(output).substring(0, 200));
                    outputs.push(output);
                }
                return outputs;
            } else {
                return "markdown cells do not have outputs"
            }

        }

    }

    functions["listCells"] = {
        "def": {
            "name": "listCells",
            "description": "Lists all cells in the currently opened notebook with their content, type, and outputs. Open a notebook first!",
            "arguments": {}
        },
        "func": async (args: any): Promise<any> => {
            const current = notebookTracker.currentWidget;
            if (current == undefined) {
                return []
            }
            const content = current.content;
            const notebook = notebookTracker.currentWidget.content;
            const cellsInfo = [];

            for (let i = 0; i < notebook.widgets.length; i++) {
                const cellWidget = notebook.widgets[i];
                const model = cellWidget.model;
                const type = model.type;
                const content = model.sharedModel.getSource();

                const cellInfo: any = {
                    index: i,
                    type: type,
                    content: content
                };

                if (cellWidget instanceof CodeCell) {
                    const outputArea = cellWidget.outputArea;
                    const outputs = [];

                    for (let j = 0; j < outputArea.model.length; j++) {
                        const output = outputArea.model.get(j);
                        outputs.push(output);
                    }
                    cellInfo.outputs = outputs;
                }
                cellsInfo.push(cellInfo);
            }
            return { "cells": cellsInfo, "path": current.context.path };
        }
    }

    functions["deleteCell"] = {
        "def": {
            "name": "deleteCell",
            "description": "Delete a cell by index",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to delete"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { index } = args;
            const notebook = getActiveNotebook(app);

            if (!notebook || !notebook.content) {
                return JSON.stringify({ error: "No active notebook found" });
            }

            if (!validateCellIndex(notebook, index)) {
                return JSON.stringify({ error: `Invalid cell index: ${index}` });
            }

            try {
                // Select the cell to delete
                notebook.content.activeCellIndex = index;

                // Delete the cell using NotebookActions
                NotebookActions.deleteCells(notebook.content);

                return JSON.stringify({
                    success: true,
                    message: `Cell at index ${index} deleted`
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error deleting cell: ${error.message}`
                });
            }
        }
    }


}
