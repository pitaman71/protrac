var path = require('path');
var ExtractTextPlugin = require("extract-text-webpack-plugin");

var config = {
    entry: path.join(__dirname,'scripts/client.js'),               // entry point
    output: {                     // output folder
        path: path.join(__dirname,'dist'),           // folder path
        filename: 'bundle.js'     // file name
    },
    resolve: {
      extensions: ['', '.scss', '.css', '.js', '.json'],
      modulesDirectories: [
        'node_modules',
        path.resolve(__dirname, './node_modules')
      ]
    },
    module: {
    loaders: [
        {
          test: /\.js$/,
          exclude: /(node_modules|bower_components|react-toolbox)/,
          loader: 'babel-loader',
          query: {
            presets: ['react']
          }
        },
        {
            test: /\.s?css$/,
            loaders: ['style', 'css', 'sass'],
            exclude: /(node_modules)\/react-toolbox/
        },
        {
            test    : /(\.scss|\.css)$/,
            include : /(node_modules)\/react-toolbox/,
            loaders : [
              require.resolve('style-loader'),
              require.resolve('css-loader') + '?sourceMap&modules&importLoaders=1&localIdentName=[name]__[local]___[hash:base64:5]',
              require.resolve('sass-loader') + '?sourceMap'
            ]
        }
      ]
    },
    plugins: [
        new ExtractTextPlugin("styles.css")
    ]
}
module.exports = config;

