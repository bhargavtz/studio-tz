import JSZip from 'jszip';

export async function downloadProject(html: string, css: string, js: string) {
  const zip = new JSZip();

  const documentHtml = `<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Next Inai Export</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            headline: ['Space Grotesk', 'sans-serif'],
          },
        },
      },
    };
  </script>
  <link rel="stylesheet" href="styles.css" />
</head>
<body class="bg-slate-950 text-slate-100">
${html}
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <script src="script.js"></script>
</body>
</html>`;

  zip.file('index.html', documentHtml);
  zip.file('styles.css', `/* Additional custom styles */\n${css}`);
  zip.file('script.js', js);

  zip.file('README.md', `# Next Inai Export

This project was generated with Tailwind CSS (via CDN) and optional Vue 3 enhancements.

## Getting started

1. Open \`index.html\` in your favourite browser.
2. All Tailwind utilities load from https://cdn.tailwindcss.com, so no build step is required.
3. Custom styles live in \`styles.css\` and scripts (including Vue 3 usage) live in \`script.js\`.

Feel free to edit the files directly and refresh the browser to see changes.
`);

  const content = await zip.generateAsync({ type: 'blob' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(content);
  link.download = 'next-inai-project.zip';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
}
