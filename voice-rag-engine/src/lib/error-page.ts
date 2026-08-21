export function renderErrorPage() {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Voice RAG - Error</title>
    <style>
      :root {
        color-scheme: dark;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #042b1d;
        color: #fff4d6;
      }

      body {
        min-height: 100vh;
        margin: 0;
        display: grid;
        place-items: center;
        background:
          radial-gradient(circle at 20% 15%, rgba(255, 210, 26, 0.18), transparent 34rem),
          radial-gradient(circle at 85% 80%, rgba(245, 0, 122, 0.16), transparent 30rem),
          #042b1d;
      }

      main {
        width: min(90vw, 34rem);
        border: 1px solid rgba(255, 210, 26, 0.24);
        border-radius: 1.5rem;
        padding: 2rem;
        background: rgba(3, 24, 17, 0.78);
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
      }

      h1 {
        margin: 0;
        font-size: clamp(1.75rem, 4vw, 2.5rem);
        line-height: 1.1;
      }

      p {
        margin: 1rem 0 0;
        color: rgba(255, 244, 214, 0.72);
        line-height: 1.6;
      }

      a {
        display: inline-flex;
        margin-top: 1.5rem;
        border-radius: 999px;
        padding: 0.75rem 1rem;
        background: #ffd21a;
        color: #042b1d;
        font-weight: 700;
        text-decoration: none;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>This page did not load</h1>
      <p>The voice engine hit an unexpected server rendering error. Refresh the page, or return home and try again.</p>
      <a href="/">Go home</a>
    </main>
  </body>
</html>`;
}
