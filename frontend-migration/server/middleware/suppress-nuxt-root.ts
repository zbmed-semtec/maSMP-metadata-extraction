export default defineEventHandler((event) => {
  // Prevent harmless requests to the bare "/_nuxt/" path from showing as 404 errors in dev logs.
  const url = event.node.req.url

  if (url === '/_nuxt/' || url === '/_nuxt') {
    setResponseStatus(event, 204, 'No Content')
    return ''
  }
})

