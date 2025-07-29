const path = require('path');
const webpack = require('webpack');
const packageJson = require('./package.json');

module.exports = {
    // Configure webpack to completely disable source maps for problematic packages
    module: {
        rules: [
            {
                test: /\.js$/,
                enforce: 'pre',
                use: ['source-map-loader'],
                exclude: [
                    // Completely exclude entities package from source map processing
                    /node_modules\/entities\//,
                    // Also exclude highlight.js which has source map issues
                    /node_modules\/highlight\.js\//
                ]
            }
        ]
    },
    plugins: [
        // Define global constants that can be used in the code
        new webpack.DefinePlugin({
            'PACKAGE_VERSION': JSON.stringify(packageJson.version)
        })
    ]
};
