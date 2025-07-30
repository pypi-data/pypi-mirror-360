import { h, computed } from "vue";
import { marked } from "marked";

export default {
  props: ['content'],
  setup(props) {

    const md = computed(() => marked.parse(
      cleanMultilineString(props.content)
    ))

    return () => h("div", { class: 'markdown-body', innerHTML: md.value });
  }

}

function cleanMultilineString(text) {
  const lines = text.split(/\r?\n/);

  while (lines.length && lines[0].trim() === '') {
    lines.shift();
  }

  while (lines.length && lines[lines.length - 1].trim() === '') {
    lines.pop();
  }

  if (lines.length > 0) {
    lines[0] = lines[0].replace(/^[\t ]+/, '');
  }

  return lines.join('\n');
}