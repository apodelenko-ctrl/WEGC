# WEGC Landing Pack

Two entry points:
- `index_cdn.html` — instant preview (Tailwind via CDN). Open directly in browser.
- `index.html` — production variant (Tailwind v4, local build at `/dist/output.css`).

## Build (Tailwind v4)
1) npm install -D @tailwindcss/cli
2) echo '@import "tailwindcss";' > src/input.css
3) Create tailwind.config.js with: module.exports = { content: ["./index.html","./src/**/*.{html,js}"] }
4) Dev:  npx @tailwindcss/cli --content "./index.html,./src/**/*.{html,js}" -i ./src/input.css -o ./dist/output.css --watch
5) Prod: NODE_ENV=production npx @tailwindcss/cli --content "./index.html,./src/**/*.{html,js}" -i ./src/input.css -o ./dist/output.css

Replace placeholder images in `/images` and PDFs in `/docs`.
