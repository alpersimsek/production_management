const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  devServer: {
    port: 3000,
    host: 'localhost',
    open: false,
    client: {
      webSocketURL: {
        hostname: 'localhost',
        port: 3000,
        protocol: 'ws'
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  },
  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      Object.assign(definitions[0], {
        'process.env.VUE_APP_API_URL': JSON.stringify(process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000')
      })
      return definitions
    })
  }
})
