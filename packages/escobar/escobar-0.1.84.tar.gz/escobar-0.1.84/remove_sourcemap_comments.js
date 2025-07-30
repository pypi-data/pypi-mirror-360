const fs = require('fs');
const path = require('path');

// Find all JavaScript files in the entities package
const entitiesDir = path.join(__dirname, 'node_modules', 'entities', 'lib', 'esm');
const jsFiles = findJsFiles(entitiesDir);

console.log(`Found ${jsFiles.length} JavaScript files to fix.`);

// Fix each JavaScript file
jsFiles.forEach(removeSourceMapComment);

console.log('All JavaScript files fixed.');

/**
 * Find all JavaScript files in a directory recursively
 * @param {string} dir - Directory to search
 * @returns {string[]} - Array of file paths
 */
function findJsFiles(dir) {
    const files = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
            files.push(...findJsFiles(fullPath));
        } else if (entry.name.endsWith('.js')) {
            files.push(fullPath);
        }
    }

    return files;
}

/**
 * Remove source map comment from a JavaScript file
 * @param {string} filePath - Path to the JavaScript file
 */
function removeSourceMapComment(filePath) {
    console.log(`Fixing ${filePath}`);

    try {
        // Read the file content
        let content = fs.readFileSync(filePath, 'utf8');

        // Remove source map comment
        content = content.replace(/\/\/# sourceMappingURL=.*$/gm, '');

        // Write the fixed content back to the file
        fs.writeFileSync(filePath, content);

        console.log(`Fixed ${filePath}`);
    } catch (error) {
        console.error(`Error fixing ${filePath}:`, error);
    }
}
