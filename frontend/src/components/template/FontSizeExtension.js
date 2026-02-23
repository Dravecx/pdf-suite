/**
 * TipTap font-size extension built on top of TextStyle.
 */
import { Extension } from '@tiptap/core'

export const FontSize = Extension.create({
  name: 'fontSize',

  addGlobalAttributes() {
    return [
      {
        types: ['textStyle'],
        attributes: {
          fontSize: {
            default: null,
            parseHTML: (el) => el.style.fontSize?.replace('pt', '') || null,
            renderHTML: (attrs) => {
              if (!attrs.fontSize) return {}
              return { style: `font-size: ${attrs.fontSize}pt` }
            },
          },
        },
      },
    ]
  },

  addCommands() {
    return {
      setFontSize:
        (size) =>
        ({ chain }) =>
          chain().setMark('textStyle', { fontSize: String(size) }).run(),

      unsetFontSize:
        () =>
        ({ chain }) =>
          chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run(),
    }
  },
})
