const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/renderer/index.js',
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'src/renderer')
    },
    port: 3000,
    hot: true
  }
};