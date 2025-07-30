const fs = require('fs');
const path = require('path');

// Find all source map files in the entities package
const entitiesDir = path.join(__dirname, 'node_modules', 'entities', 'lib', 'esm');
const sourceMapFiles = findSourceMapFiles(entitiesDir);

console.log(`Found ${sourceMapFiles.length} source map files to fix.`);

// Fix each source map file
sourceMapFiles.forEach(fixSourceMapFile);

console.log('All source map files fixed.');

/**
 * Find all source map files in a directory recursively
 * @param {string} dir - Directory to search
 * @returns {string[]} - Array of file paths
 */
function findSourceMapFiles(dir) {
    const files = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
            files.push(...findSourceMapFiles(fullPath));
        } else if (entry.name.endsWith('.map')) {
            files.push(fullPath);
        }
    }

    return files;
}

/**
 * Fix a source map file by removing the sourceRoot property
 * @param {string} filePath - Path to the source map file
 */
function fixSourceMapFile(filePath) {
    console.log(`Fixing ${filePath}`);

    try {
        // Read the file content
        let content = fs.readFileSync(filePath, 'utf8');

        // Add opening curly brace if missing
        if (!content.startsWith('{')) {
            content = '{' + content;
        }

        // Try to parse the JSON
        let sourceMap;
        try {
            sourceMap = JSON.parse(content);
        } catch (e) {
            // If parsing fails, try to fix common issues
            content = fixJsonFormat(content);
            sourceMap = JSON.parse(content);
        }

        // Remove the sourceRoot property
        if (sourceMap.sourceRoot) {
            delete sourceMap.sourceRoot;
        }

        // Write the fixed content back to the file
        fs.writeFileSync(filePath, JSON.stringify(sourceMap));

        console.log(`Fixed ${filePath}`);
    } catch (error) {
        console.error(`Error fixing ${filePath}:`, error);
    }
}

/**
 * Fix common JSON format issues in source map files
 * @param {string} content - Source map content
 * @returns {string} - Fixed content
 */
function fixJsonFormat(content) {
    // Add quotes around keys
    return content.replace(/([{,])(\s*)([a-zA-Z0-9_]+):/g, '$1$2"$3":');
}
