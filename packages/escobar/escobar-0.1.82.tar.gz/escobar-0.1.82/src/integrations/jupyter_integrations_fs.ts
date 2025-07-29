import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, functions } from './jupyter_integrations';
import { streamingState } from "./jupyter_integrations";
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import * as DiffMatchPatch from 'diff-match-patch';
import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

// Import necessary CodeMirror modules
import { StateEffect, StateField, EditorState, Text } from '@codemirror/state';
import { Decoration, EditorView } from '@codemirror/view';
import { MergeView } from '@codemirror/merge';


export async function ensurePathExists(
    app: JupyterFrontEnd,
    fullPath: string,
    createFile: boolean = true,
    defaultContent: string = ''
): Promise<void> {
    const contents = app.serviceManager.contents;

    // Normalize path and split - handle Windows paths and multiple slashes
    const normalizedPath = fullPath.replace(/\\/g, '/').replace(/\/+/g, '/');
    const parts = normalizedPath.split('/').filter(part => part !== '' && part !== '.');

    // Extract filename and directory parts
    const filename = parts.pop(); // Remove and get the filename

    // Create directory structure if needed
    if (parts.length > 0) {
        let currentPath = '';
        for (const part of parts) {
            currentPath = currentPath ? `${currentPath}/${part}` : part;

            try {
                const stat = await contents.get(currentPath);
                if (stat.type !== 'directory') {
                    throw new Error(`${currentPath} exists but is not a directory`);
                }
            } catch (err: any) {
                if (err?.response?.status === 404 || /not found/i.test(err.message)) {
                    // Create the directory using contents.save()
                    await contents.save(currentPath, {
                        type: 'directory',
                        format: 'json',
                        content: null
                    });
                } else {
                    throw new Error(`Failed checking/creating directory ${currentPath}: ${err.message}`);
                }
            }
        }
    }

    // Create the file if requested and it doesn't exist
    if (createFile && filename) {
        try {
            // Check if file already exists
            await contents.get(normalizedPath);
            // File exists, do nothing
        } catch (err: any) {
            if (err?.response?.status === 404 || /not found/i.test(err.message)) {
                // File doesn't exist, create it
                await contents.save(normalizedPath, {
                    type: 'file',
                    format: 'text',
                    content: defaultContent
                });
            } else {
                throw new Error(`Failed checking file ${normalizedPath}: ${err.message}`);
            }
        }
    }
}






export function init_fs() {
    functions["listFiles"] = {
        "def": {
            "name": "listFiles",
            "description": "List files and directories at a specified relative path. Ignore rootPath if it exists",
            "arguments": {
                "path": {
                    "type": "string",
                    "name": "Relative path to list files from. Relative!",
                    "default": "/"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const path = args.path || '/';
            const contents = app.serviceManager.contents;

            try {
                const listing = await contents.get(path, { content: true });

                if (listing.type !== 'directory') {
                    return JSON.stringify({
                        error: `Path '${path}' is not a directory`
                    });
                }

                const files = listing.content.map(item => ({
                    name: item.name,
                    path: item.path,
                    type: item.type,
                    last_modified: item.last_modified
                }));

                return JSON.stringify({
                    success: true,
                    files: files
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error listing files: ${error.message}`
                });
            }
        }
    }



    functions["writeToFile"] = {
        "def": {
            "name": "writeToFile",
            "description": "Opens a non-notebook file for editing (code, text, etc) and write into it",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to write to. Relative! "
                },
                "content": {
                    "type": "string",
                    "name": "New content for the file. Entire file is being replaced by this!"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { contents } = app.serviceManager;
            const { filePath, content } = args;

            if (call_id == undefined) return JSON.stringify({ "status": "fail", "message": "no call_id received" });


            // create the file if necessary
            await ensurePathExists(app, filePath);

            let widget;
            try {
                widget = await app.commands.execute('docmanager:open', {
                    path: filePath,
                    factory: 'Editor'
                });
            } catch (err) {
                return JSON.stringify({
                    "status": "fail", "message": "could not open file",
                    "detail": `${err.message}`
                });
            }

            await contents.save(filePath, {
                type: 'file',
                format: 'text',
                content: content
            });


            if (streamingState[call_id] == undefined) {
                streamingState[call_id] = true;
            }



            try {
                await Promise.race([
                    widget.context.ready,
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout waiting for context.ready')), 1500))
                ]);
            } catch (err) {
                return JSON.stringify({ "status": "fail", "message": "could not open file" });
            }

            await widget.context.revert();

            // Scroll to the end of the content
            if (widget.content && widget.content.editor) {
                const editor = widget.content.editor;

                // Get the position at the end of the content
                const docLength = editor.model.sharedModel.source.length;
                const endPosition = editor.getPositionAt(docLength);

                if (endPosition) {
                    // Set cursor to the end of the document and reveal it
                    editor.setCursorPosition(endPosition);
                    editor.revealPosition(endPosition);
                }
            }

            return JSON.stringify({
                "status": "ok"
            })
        }
    }


    functions["openFile"] = {
        "def": {
            "name": "openFile",
            "description": `Opens a non-notebook file for editing (code, text, etc) and returns its contents. 
            Never open notebooks with this method!`,
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to open. Relative! "
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }
            const filePath = args["filePath"]

            // Check if file is a notebook (.ipynb)
            if (filePath.endsWith('.ipynb')) {
                return JSON.stringify({
                    "status": "fail",
                    "message": "Cannot open notebook files with this method"
                });
            }

            const { contents } = app.serviceManager;
            let fileContent;

            // Ensure file exists (create if it doesn't)
            await ensurePathExists(app, filePath);
            try {
                try {
                    fileContent = await contents.get(filePath);

                    // Check file size (> 16KB)
                    if (fileContent.content && typeof fileContent.content === 'string' &&
                        fileContent.content.length > 16384) {
                        return JSON.stringify({
                            "status": "fail",
                            "message": "File is too large (> 16KB)"
                        });
                    }
                } catch {
                    await contents.save(filePath, {
                        type: 'file',
                        format: 'text',
                        content: ''
                    });
                    fileContent = await contents.get(filePath);
                }
            } catch (err) {
                return JSON.stringify({
                    "status": "fail", "message": "could not open file",
                    "detail": `${err.message} `
                });
            }

            let widget;
            try {
                widget = await app.commands.execute('docmanager:open', {
                    path: filePath,
                    factory: 'Editor'
                });
            } catch (err) {
                return JSON.stringify({
                    "status": "fail", "message": "could not open file",
                    "detail": `${err.message} `
                });
            }

            try {
                await Promise.race([
                    widget.context.ready,
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout waiting for context.ready')), 500))
                ]);
            } catch (err) {
                return JSON.stringify({ "status": "fail", "message": "could not open file" });
            }

            const result = JSON.stringify({
                "status": "ok",
                "content": fileContent.content
            });

            return (result);
        }
    }

}
