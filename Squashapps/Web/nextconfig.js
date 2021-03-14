
require('dotenv').config()
const path = require('path')
const Dotenv = require("dotenv-webpack");
const withSass = require('@zeit/next-sass')
module.exports = withSass()

module.exports = {
    env: {
        API_URL: process.env.API_URL
    },
    publicRuntimeConfig: {
        API_URL: process.env.API_URL,
    },

    webpack: config => {
        config.plugins = config.plugins || [];
        config.plugins = [
            ...config.plugins,
      
            // Read the .env file
            new Dotenv({
              path: path.join(__dirname, ".env"),
              systemvars: true
            })
          ];
        config.resolve.alias['components'] = path.join(__dirname, 'components')
        config.resolve.alias['public'] = path.join(__dirname, 'public')
        
        config.node = {
            fs: 'empty'
          }
          
        return config
    }
}