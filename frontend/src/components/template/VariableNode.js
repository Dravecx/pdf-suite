/**
 * TipTap custom inline node for {{variable}} placeholders.
 * Renders as an orange chip. Typing {{name}} auto-converts.
 */
import { Node, mergeAttributes, InputRule } from '@tiptap/core'

export const Variable = Node.create({
  name: 'variable',
  group: 'inline',
  inline: true,
  atom: true,
  selectable: true,
  draggable: false,

  addAttributes() {
    return {
      name: { default: '' },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-variable]',
        getAttrs: (el) => ({ name: el.getAttribute('data-variable') }),
      },
    ]
  },

  renderHTML({ node, HTMLAttributes }) {
    return [
      'span',
      mergeAttributes(HTMLAttributes, {
        'data-variable': node.attrs.name,
        class: 'variable-chip',
        contenteditable: 'false',
      }),
      `{{${node.attrs.name}}}`,
    ]
  },

  addNodeView() {
    return ({ node }) => {
      const dom = document.createElement('span')
      dom.className = 'variable-chip'
      dom.setAttribute('data-variable', node.attrs.name)
      dom.setAttribute('contenteditable', 'false')
      dom.textContent = `{{${node.attrs.name}}}`
      return { dom }
    }
  },

  addInputRules() {
    return [
      new InputRule({
        find: /\{\{([a-zA-Z0-9_]+)\}\}(\s?)$/,
        handler: ({ state, range, match }) => {
          const name = match[1]
          if (!name) return null
          const { tr } = state
          tr.replaceWith(range.from, range.to, this.type.create({ name }))
          return tr
        },
      }),
    ]
  },

  addCommands() {
    return {
      insertVariable:
        (name) =>
        ({ chain }) =>
          chain().insertContent({ type: this.name, attrs: { name } }).run(),
    }
  },
})
