/**
 * Custom webpack configuration for JupyterLab
 * This file is used by JupyterLab's build system to configure webpack
 */

module.exports = {
    // Disable source maps completely
    devtool: false,

    // Configure webpack to ignore source maps for problematic packages
    module: {
        rules: [
            {
                test: /\.js$/,
                enforce: 'pre',
                use: ['source-map-loader'],
                exclude: [
                    // Exclude all node_modules from source map processing
                    /node_modules/
                ]
            }
        ]
    },

    // Ignore specific warnings
    ignoreWarnings: [
        // Ignore warnings about missing source maps
        /Failed to parse source map/,
        // Ignore warnings about invalid dependencies
        /Invalid dependencies have been reported/,
        // Ignore warnings about highlight.js
        /No version specified and unable to automatically determine one/
    ]
};
