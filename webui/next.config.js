module.exports = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/ask',
        permanent: true,
      },
    ]
  },
}