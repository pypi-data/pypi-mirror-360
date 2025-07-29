import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, notebookTracker, functions, memoryBank } from './jupyter_integrations'
import { getActiveNotebook, validateCellIndex, } from "./jupyter_integrations"
import { Cell, CellModel, ICellModel, CodeCell, MarkdownCell } from '@jupyterlab/cells';
import { ensurePathExists } from './jupyter_integrations_fs';

export function init_settings() {
    functions["setValue"] = {
        "def": {
            "name": "setValue",
            "description": "Sets a session variable, aka settings vairable, setting, variable, etc",
            "arguments": {
                "key": {
                    "type": "string",
                    "name": "Name of the property to set"
                },
                "value": {
                    "type": "string",
                    "name": "The value to store"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            let key = args["key"] || "";
            let value = args["value"] || "";
            memoryBank[key] = value;
            return "ok"
        }
    },
        functions["getValue"] = {
            "def": {
                "name": "getValue",
                "description": "Gets a session variable, aka settings vairable, setting, variable, etc",
                "arguments": {
                    "key": {
                        "type": "string",
                        "name": "Name of the property to retrieve"
                    }
                }
            },
            "func": async (args: any): Promise<string> => {
                let key = args["key"] || "";
                let value = memoryBank[key] = memoryBank[key];
                return JSON.stringify({
                    key: key,
                    velue: value
                })
            }
        }
}