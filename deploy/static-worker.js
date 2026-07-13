export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const routes = {
      "/": "/index.html",
      "/works": "/works.html",
      "/apparel": "/apparel.html"
    };
    url.pathname = routes[url.pathname] || url.pathname;

    const response = await env.ASSETS.fetch(new Request(url, request));
    if (response.status !== 404) return response;
    return env.ASSETS.fetch(new Request(new URL("/index.html", request.url), request));
  }
};
