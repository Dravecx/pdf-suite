#!/usr/bin/env node
/**
 * Post-build script: writes pdf_suite/www/pdf-studio.html from the Vite dist/index.html.
 *
 * Frappe serves assets from /assets/pdf_suite/dist/ (maps to pdf_suite/public/dist/).
 * This script reads the built index.html, rewrites asset paths, and writes the
 * www page that Frappe renders at /pdf-studio.
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const distDir = path.resolve(__dirname, '../../pdf_suite/public/dist')
const wwwDir = path.resolve(__dirname, '../../pdf_suite/www')
const indexHtml = path.join(distDir, 'index.html')
const wwwHtml = path.join(wwwDir, 'pdf-studio.html')

if (!fs.existsSync(indexHtml)) {
  console.error('  ERROR: dist/index.html not found — run npm run build first')
  process.exit(1)
}

let html = fs.readFileSync(indexHtml, 'utf-8')

// Strip the <html>, <head>, <body> wrappers — Frappe provides those via base.html
// Extract just the asset tags we need
const scriptMatches = [...html.matchAll(/<script[^>]*src="([^"]+)"[^>]*><\/script>/g)]
const linkMatches = [...html.matchAll(/<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>/g)]

const scripts = scriptMatches.map((m) => `  <script type="module" crossorigin src="${m[1]}"></script>`).join('\n')
const links = linkMatches.map((m) => `  <link rel="stylesheet" crossorigin href="${m[1]}">`).join('\n')

// Write the Frappe www template
const wwwContent = `{%- block head_include %}
<title>PDF Studio</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
${links}
${scripts}
{%- endblock %}

{%- block page_content %}
<div id="app"></div>
{%- endblock %}
`

fs.mkdirSync(wwwDir, { recursive: true })
fs.writeFileSync(wwwHtml, wwwContent)
console.log('  WRITE pdf_suite/www/pdf-studio.html (generated from dist/index.html)')
