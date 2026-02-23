/**
 * Composable for calling PDF Suite backend APIs.
 * All methods return { success, data?, error? } responses.
 */

const BASE_URL = '/api/method/pdf_suite.api'

async function callApi(endpoint, params = {}, method = 'POST') {
  try {
    const url = `${BASE_URL}.${endpoint}`

    const options = {
      method,
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': getCsrfToken() },
      credentials: 'include',
    }

    if (method === 'GET') {
      const searchParams = new URLSearchParams()
      for (const [key, value] of Object.entries(params)) {
        searchParams.set(key, typeof value === 'object' ? JSON.stringify(value) : value)
      }
      const fullUrl = searchParams.toString() ? `${url}?${searchParams}` : url
      const res = await fetch(fullUrl, options)
      const json = await res.json()
      return json.message || json
    }

    options.body = JSON.stringify(params)
    const res = await fetch(url, options)
    const json = await res.json()
    return json.message || json
  } catch (e) {
    return { success: false, error: e.message || 'Network error' }
  }
}

function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrf_token='))
  return cookie ? cookie.split('=')[1] : ''
}

export function usePdfApi() {
  return {
    // Extract
    getPdfInfo: (fileUrl) => callApi('extract.get_pdf_info', { file_url: fileUrl }),
    extractText: (fileUrl, pages) => callApi('extract.extract_text', { file_url: fileUrl, page_numbers: pages }),
    extractTables: (fileUrl, pages) => callApi('extract.extract_tables', { file_url: fileUrl, page_numbers: pages }),
    extractImages: (fileUrl, pages) => callApi('extract.extract_images', { file_url: fileUrl, page_numbers: pages }),

    // Merge
    mergePdfs: (fileUrls, outputName) => callApi('merge.merge_pdfs', { file_urls: fileUrls, output_filename: outputName }),
    mergePdfsWithOptions: (configs, outputName) => callApi('merge.merge_pdfs_with_options', { file_configs: configs, output_filename: outputName }),

    // Split
    splitPdf: (fileUrl, ranges) => callApi('split.split_pdf', { file_url: fileUrl, page_ranges: ranges }),
    splitEveryN: (fileUrl, n) => callApi('split.split_pdf_every_n', { file_url: fileUrl, n }),
    extractPages: (fileUrl, pages, outputName) => callApi('split.extract_pages', { file_url: fileUrl, page_numbers: pages, output_filename: outputName }),

    // Compress
    compressPdf: (fileUrl, quality, outputName) => callApi('compress.compress_pdf', { file_url: fileUrl, quality, output_filename: outputName }),

    // Watermark
    addTextWatermark: (fileUrl, opts) => callApi('watermark.add_text_watermark', { file_url: fileUrl, ...opts }),
    addImageWatermark: (fileUrl, opts) => callApi('watermark.add_image_watermark', { file_url: fileUrl, ...opts }),

    // Protect
    encryptPdf: (fileUrl, userPw, ownerPw, outputName) => callApi('protect.encrypt_pdf', { file_url: fileUrl, user_password: userPw, owner_password: ownerPw, output_filename: outputName }),
    decryptPdf: (fileUrl, password, outputName) => callApi('protect.decrypt_pdf', { file_url: fileUrl, password, output_filename: outputName }),

    // Flatten
    flattenPdf: (fileUrl, outputName) => callApi('flatten.flatten_pdf', { file_url: fileUrl, output_filename: outputName }),

    // Redact
    redactAreas: (fileUrl, redactions, outputName) => callApi('redact.redact_areas', { file_url: fileUrl, redactions, output_filename: outputName }),
    redactText: (fileUrl, searchText, outputName) => callApi('redact.redact_text', { file_url: fileUrl, search_text: searchText, output_filename: outputName }),

    // OCR
    ocrPdf: (fileUrl, lang, outputName) => callApi('ocr.ocr_pdf', { file_url: fileUrl, language: lang, output_filename: outputName }),
    ocrImage: (fileUrl, lang) => callApi('ocr.ocr_image_to_text', { file_url: fileUrl, language: lang }),

    // Convert
    pdfToDocx: (fileUrl, outputName) => callApi('convert.pdf_to_docx', { file_url: fileUrl, output_filename: outputName }),
    docxToPdf: (fileUrl, outputName) => callApi('convert.docx_to_pdf', { file_url: fileUrl, output_filename: outputName }),
    htmlToPdf: (html, outputName) => callApi('convert.html_to_pdf', { html_content: html, output_filename: outputName }),

    // Document sessions
    exportEdited: (fileUrl, textMods, outputName) => callApi('document.export_edited_pdf', { file_url: fileUrl, text_modifications: textMods, output_filename: outputName }),
    saveSession: (fileUrl, annotations, mods, name) => callApi('document.save_edit_session', { file_url: fileUrl, annotations, page_modifications: mods, session_name: name }),
    loadSession: (name) => callApi('document.load_edit_session', { session_name: name }),
    listSessions: () => callApi('document.list_edit_sessions', {}, 'GET'),

    // Templates
    saveTemplate: (name, schema, basePdf, desc) => callApi('template.save_template', { name, schema, base_pdf: basePdf, description: desc }),
    getTemplate: (name) => callApi('template.get_template', { template_name: name }, 'GET'),
    listTemplates: () => callApi('template.list_templates', {}, 'GET'),
    deleteTemplate: (name) => callApi('template.delete_template', { template_name: name }),
    generateHtmlPdf: (templateName, variableData, outputFilename) => callApi('template.generate_html_pdf', { template_name: templateName, variable_data: JSON.stringify(variableData), output_filename: outputFilename || '' }),

    // Batch
    startBatch: (operation, fileUrls, options) => callApi('batch.start_batch', { operation, file_urls: fileUrls, options }),
    getBatchStatus: (name) => callApi('batch.get_batch_status', { batch_name: name }, 'GET'),

    // Upload file
    uploadFile: async (file, isPrivate = 1) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_private', isPrivate)
      formData.append('folder', 'Home')

      try {
        const res = await fetch('/api/method/upload_file', {
          method: 'POST',
          headers: { 'X-Frappe-CSRF-Token': getCsrfToken() },
          credentials: 'include',
          body: formData,
        })
        const json = await res.json()
        if (json.message?.file_url) {
          return { success: true, data: { file_url: json.message.file_url, name: json.message.name } }
        }
        return { success: false, error: 'Upload failed' }
      } catch (e) {
        return { success: false, error: e.message }
      }
    },
  }
}
