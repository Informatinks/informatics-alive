const debug = process.env.NODE_ENV !== 'production';
const webpack = require('webpack');
const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');


const API_URLS = {
  'debug': {
    'websocket': JSON.stringify('http://localhost:8080'),
  },
  'production': {
    'websocket': JSON.stringify('https://rmatics.info/api'),
  }
}


module.exports = {
  context: path.join(__dirname, 'src'),
  devtool: debug ? 'inline-sourcemap' : false,
  entry: './js/index.jsx',
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',
        query: {
          presets: [
            'react',
            'es2015',
            'stage-0',
          ],
          plugins: [
            'react-html-attrs',
            'transform-class-properties',
            'transform-decorators-legacy',
          ],
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.(jpe?g|png|gif|eot|ttf|woff)$/,
        loaders: [
          'file-loader?hash=sha512&digest=hex&name=[hash].[ext]',
          {
            loader: 'image-webpack-loader?bypassOnDebug&optimizationLevel=7&interlaced=false',
            query: {
              mozjpeg: {
                progressive: true,
              },
              gifsicle: {
                interlaced: false,
              },
              optipng: {
                optimizationLevel: 4,
              },
              pngquant: {
                quality: '75-90',
                speed: 3,
              },
            },
          }
        ],
      },
      {
        test: /\.svg$/,
        loader: 'svg-inline-loader'
      }
    ]
  },
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'app.min.js',
  },
  plugins: debug ? [
    new webpack.optimize.OccurrenceOrderPlugin(),
    new webpack.DefinePlugin({
      '__websocket__': API_URLS['debug']['websocket'],
    })
  ] : [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production'),
      '__websocket__': API_URLS['production']['websocket'],
    }),
    new webpack.optimize.OccurrenceOrderPlugin(),
    new UglifyJsPlugin(),
  ],
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  devServer: {
    port: 8080,
    contentBase: path.join(__dirname, 'dist'),
    compress: true,
    disableHostCheck: true,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://informatics.msk.ru:6349',
        pathRewrite: {'^/api': ''},
      },
      '/socket.io': {
        target: 'http://informatics.msk.ru:6349',
        ws: true,
      }
    },
  }
};
