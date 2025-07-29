import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, notebookTracker, functions } from './jupyter_integrations'
import {getActiveNotebook, validateCellIndex, } from "./jupyter_integrations"
import { Cell, CellModel, ICellModel, CodeCell, MarkdownCell } from '@jupyterlab/cells';
import { ensurePathExists } from './jupyter_integrations_fs';


export function init_output() {  
    functions["saveAllOutputImages"] = {
        "def": {
            "name": "saveAllOutputImages",
            "description": "Save all output images from a cell to a specified folder",
            "arguments": {
                "cellIndex": {
                    "type": "integer",
                    "name": "Index of the cell containing the images"
                },
                "folderPath": {
                    "type": "string",
                    "name": "Folder path where images should be saved"
                },
                "filePrefix": {
                    "type": "string",
                    "name": "Prefix for the image filenames",
                    "default": "image"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }
            
            const { cellIndex, folderPath, filePrefix = "image" } = args;
            const notebook = getActiveNotebook(app);
            
            if (!notebook || !notebook.content) {
                return JSON.stringify({ error: "No active notebook found" });
            }
            
            if (!validateCellIndex(notebook, cellIndex)) {
                return JSON.stringify({ error: `Invalid cell index: ${cellIndex}` });
            }
            
            try {
                // Get the cell
                const cell = notebook.content.widgets[cellIndex];
                
                // Only code cells have outputs
                if (!(cell instanceof CodeCell)) {
                    return JSON.stringify({ 
                        error: `Cell ${cellIndex} is not a code cell and has no output` 
                    });
                }
                
                // Get the outputs using the existing getCellOutput function
                const outputsResult = await functions["getCellOutput"].func({ index: cellIndex });
                console.log('[saveAllOutputImages] Raw getCellOutput result:', outputsResult);
                
                let outputs = [];
                
                // Parse the outputs - handle different return formats
                if (typeof outputsResult === 'string') {
                    console.log('[saveAllOutputImages] Parsing string output result');
                    try {
                        outputs = JSON.parse(outputsResult);
                        console.log('[saveAllOutputImages] Successfully parsed output JSON');
                    } catch (e) {
                        console.error('[saveAllOutputImages] Error parsing outputs:', e);
                        console.log('[saveAllOutputImages] Raw string output:', outputsResult);
                    }
                } else if (Array.isArray(outputsResult)) {
                    console.log('[saveAllOutputImages] Output result is already an array');
                    outputs = outputsResult;
                } else if (outputsResult && typeof outputsResult === 'object') {
                    console.log('[saveAllOutputImages] Output result is an object, checking for array properties');
                    // Try to find an array property in the result
                    for (const key in outputsResult) {
                        if (Array.isArray(outputsResult[key])) {
                            console.log(`[saveAllOutputImages] Found array in property '${key}'`);
                            outputs = outputsResult[key];
                            break;
                        }
                    }
                    
                    // If we still don't have an array, treat the object as a single output
                    if (outputs.length === 0 && outputsResult.data) {
                        console.log('[saveAllOutputImages] Treating object as a single output');
                        outputs = [outputsResult];
                    }
                } else {
                    console.log('[saveAllOutputImages] Unrecognized output format, using as is');
                    outputs = outputsResult;
                }
                
                console.log('[saveAllOutputImages] Processed outputs:', outputs);
                
                // Check if there are any outputs
                if (!outputs || !Array.isArray(outputs) || outputs.length === 0) {
                    return JSON.stringify({ 
                        error: `No outputs found for cell ${cellIndex}` 
                    });
                }
                
                // Ensure the directory exists - add a dummy file to the path since ensurePathExists removes the last part
                console.log(`[saveAllOutputImages] Ensuring directory exists: ${folderPath}`);
                try {
                    // Add a dummy filename to the path since ensurePathExists removes the last part
                    const dummyPath = `${folderPath}/dummy.txt`;
                    await ensurePathExists(app, dummyPath);
                    console.log(`[saveAllOutputImages] Directory ensured: ${folderPath}`);
                } catch (dirError) {
                    console.error(`[saveAllOutputImages] Error ensuring directory: ${dirError.message}`);
                    throw dirError;
                }
                
                // Get the contents service
                const contents = app.serviceManager.contents;
                
                // Look for image MIME types
                const imageMimeTypes = [
                    'image/png', 
                    'image/jpeg', 
                    'image/jpg', 
                    'image/gif', 
                    'image/svg+xml'
                ];
                
                const savedImages = [];
                let imageCount = 0;
                
                // Process each output
                for (let i = 0; i < outputs.length; i++) {
                    const output = outputs[i];
                    console.log(`[saveAllOutputImages] Processing output ${i}:`, output);
                    
                    // Skip outputs without data
                    if (!output || !output.data) {
                        console.log(`[saveAllOutputImages] Output ${i} has no data, skipping`);
                        continue;
                    }
                    
                    console.log(`[saveAllOutputImages] Output ${i} data:`, output.data);
                    console.log(`[saveAllOutputImages] Available MIME types in output ${i}:`, 
                        Object.keys(output.data || {}).filter(key => key.startsWith('image/')));
                    
                    // Check each MIME type for image data
                    for (const mimeType of imageMimeTypes) {
                        if (output.data[mimeType]) {
                            const imageData = output.data[mimeType];
                            console.log(`[saveAllOutputImages] Found image data in output ${i} with MIME type: ${mimeType}`);
                            console.log(`[saveAllOutputImages] Image data preview:`, 
                                typeof imageData === 'string' 
                                    ? `${imageData.substring(0, 50)}... (${imageData.length} chars)` 
                                    : 'Non-string data');
                            
                            // Generate a filename
                            const timestamp = Date.now();
                            const extension = mimeType.split('/')[1].replace('jpeg', 'jpg');
                            const fileName = `${filePrefix}_cell${cellIndex}_${imageCount}_${timestamp}.${extension}`;
                            const filePath = `${folderPath}/${fileName}`;
                            
                            // Directory already ensured at the beginning of the function
                            
                            // For most image types, the data is base64 encoded
                            // For SVG, it might be plain text
                            let format: 'base64' | 'text' = 'base64';
                            
                            if (mimeType === 'image/svg+xml' && typeof imageData === 'string' && !imageData.startsWith('data:')) {
                                format = 'text';
                                console.log(`[saveAllOutputImages] Using text format for SVG data`);
                            } else {
                                console.log(`[saveAllOutputImages] Using base64 format for ${mimeType} data`);
                            }
                            
                            console.log(`[saveAllOutputImages] Saving image to: ${filePath}`);
                            console.log(`[saveAllOutputImages] File format: ${format}`);
                            
                            // Save the file
                            try {
                                await contents.save(filePath, {
                                    type: 'file',
                                    format: format,
                                    content: imageData
                                });
                                console.log(`[saveAllOutputImages] Successfully saved image to ${filePath}`);
                            } catch (saveError) {
                                console.error(`[saveAllOutputImages] Error saving image to ${filePath}:`, saveError);
                                throw saveError;
                            }
                            
                            savedImages.push({
                                filePath: filePath,
                                mimeType: mimeType,
                                outputIndex: i
                            });
                            
                            imageCount++;
                        }
                    }
                }
                
                if (savedImages.length === 0) {
                    return JSON.stringify({ 
                        error: `No image data found in any outputs of cell ${cellIndex}` 
                    });
                }
                
                return JSON.stringify({ 
                    success: true, 
                    message: `Saved ${savedImages.length} images to ${folderPath}`,
                    savedImages: savedImages
                });
            } catch (error) {
                return JSON.stringify({ 
                    error: `Error saving images: ${error.message}` 
                });
            }
        }
    };

    functions["saveOutputImage"] = {
        "def": {
            "name": "saveOutputImage",
            "description": "Save an output image from a cell to a specified file",
            "arguments": {
                "cellIndex": {
                    "type": "integer",
                    "name": "Index of the cell containing the image"
                },
                "outputIndex": {
                    "type": "integer",
                    "name": "Index of the output to save (if cell has multiple outputs)",
                    "default": 0
                },
                "filePath": {
                    "type": "string",
                    "name": "Path where the image should be saved"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }
            
            const { cellIndex, outputIndex = 0, filePath } = args;
            const notebook = getActiveNotebook(app);
            
            if (!notebook || !notebook.content) {
                return JSON.stringify({ error: "No active notebook found" });
            }
            
            if (!validateCellIndex(notebook, cellIndex)) {
                return JSON.stringify({ error: `Invalid cell index: ${cellIndex}` });
            }
            
            try {
                // Get the cell
                const cell = notebook.content.widgets[cellIndex];
                
                // Only code cells have outputs
                if (!(cell instanceof CodeCell)) {
                    return JSON.stringify({ 
                        error: `Cell ${cellIndex} is not a code cell and has no output` 
                    });
                }
                
                // Get the outputs using the existing getCellOutput function
                const outputsResult = await functions["getCellOutput"].func({ index: cellIndex });
                console.log('[saveOutputImage] Raw getCellOutput result:', outputsResult);
                
                let outputs = [];
                
                // Parse the outputs - handle different return formats
                if (typeof outputsResult === 'string') {
                    console.log('[saveOutputImage] Parsing string output result');
                    try {
                        outputs = JSON.parse(outputsResult);
                        console.log('[saveOutputImage] Successfully parsed output JSON');
                    } catch (e) {
                        console.error('[saveOutputImage] Error parsing outputs:', e);
                        console.log('[saveOutputImage] Raw string output:', outputsResult);
                    }
                } else if (Array.isArray(outputsResult)) {
                    console.log('[saveOutputImage] Output result is already an array');
                    outputs = outputsResult;
                } else if (outputsResult && typeof outputsResult === 'object') {
                    console.log('[saveOutputImage] Output result is an object, checking for array properties');
                    // Try to find an array property in the result
                    for (const key in outputsResult) {
                        if (Array.isArray(outputsResult[key])) {
                            console.log(`[saveOutputImage] Found array in property '${key}'`);
                            outputs = outputsResult[key];
                            break;
                        }
                    }
                    
                    // If we still don't have an array, treat the object as a single output
                    if (outputs.length === 0 && outputsResult.data) {
                        console.log('[saveOutputImage] Treating object as a single output');
                        outputs = [outputsResult];
                    }
                } else {
                    console.log('[saveOutputImage] Unrecognized output format, using as is');
                    outputs = outputsResult;
                }
                
                console.log('[saveOutputImage] Processed outputs:', outputs);
                
                // Check if the specified output exists
                if (!outputs || !Array.isArray(outputs) || outputs.length <= outputIndex) {
                    return JSON.stringify({ 
                        error: `No output found at index ${outputIndex} for cell ${cellIndex}` 
                    });
                }
                
                const output = outputs[outputIndex];
                
                // Check if the output contains image data
                if (!output || !output.data) {
                    return JSON.stringify({ 
                        error: `Output at index ${outputIndex} does not contain data` 
                    });
                }
                
                // Look for image MIME types
                const imageMimeTypes = [
                    'image/png', 
                    'image/jpeg', 
                    'image/jpg', 
                    'image/gif', 
                    'image/svg+xml'
                ];
                
                console.log('[saveOutputImage] Output data:', output.data);
                console.log('[saveOutputImage] Available MIME types in output:', 
                    Object.keys(output.data || {}).filter(key => key.startsWith('image/')));
                
                let imageData = null;
                let mimeType = null;
                
                for (const type of imageMimeTypes) {
                    if (output.data[type]) {
                        imageData = output.data[type];
                        mimeType = type;
                        console.log(`[saveOutputImage] Found image data with MIME type: ${type}`);
                        console.log(`[saveOutputImage] Image data preview:`, 
                            typeof imageData === 'string' 
                                ? `${imageData.substring(0, 50)}... (${imageData.length} chars)` 
                                : 'Non-string data');
                        break;
                    }
                }
                
                if (!imageData || !mimeType) {
                    return JSON.stringify({ 
                        error: `No image data found in output ${outputIndex}` 
                    });
                }
                
                // Extract directory path from the file path
                const lastSlashIndex = filePath.lastIndexOf('/');
                const dirPath = lastSlashIndex !== -1 ? filePath.substring(0, lastSlashIndex) : '.';
                
                // Ensure the directory exists
                console.log(`[saveOutputImage] Ensuring directory exists: ${dirPath}`);
                try {
                    // Add a dummy filename to the path since ensurePathExists removes the last part
                    const dummyPath = `${dirPath}/dummy.txt`;
                    await ensurePathExists(app, dummyPath);
                    console.log(`[saveOutputImage] Directory ensured: ${dirPath}`);
                } catch (dirError) {
                    console.error(`[saveOutputImage] Error ensuring directory: ${dirError.message}`);
                    throw dirError;
                }
                
                // Get the contents service
                const contents = app.serviceManager.contents;
                
                // For most image types, the data is base64 encoded
                // For SVG, it might be plain text
                let format: 'base64' | 'text' = 'base64';
                let content = imageData;
                
                if (mimeType === 'image/svg+xml' && typeof imageData === 'string' && !imageData.startsWith('data:')) {
                    format = 'text';
                    console.log(`[saveOutputImage] Using text format for SVG data`);
                } else {
                    console.log(`[saveOutputImage] Using base64 format for ${mimeType} data`);
                }
                
                console.log(`[saveOutputImage] Saving image to: ${filePath}`);
                console.log(`[saveOutputImage] File format: ${format}`);
                
                // Save the file
                try {
                    await contents.save(filePath, {
                        type: 'file',
                        format: format,
                        content: content
                    });
                    console.log(`[saveOutputImage] Successfully saved image to ${filePath}`);
                } catch (saveError) {
                    console.error(`[saveOutputImage] Error saving image to ${filePath}:`, saveError);
                    throw saveError;
                }
                
                return JSON.stringify({ 
                    success: true, 
                    message: `Image saved to ${filePath}`,
                    mimeType: mimeType
                });
            } catch (error) {
                return JSON.stringify({ 
                    error: `Error saving image: ${error.message}` 
                });
            }
        }
    };

}