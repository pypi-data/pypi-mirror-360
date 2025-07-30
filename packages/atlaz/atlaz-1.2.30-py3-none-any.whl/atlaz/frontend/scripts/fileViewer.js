// fileViewer.js

// File viewer functionality
fetch('files.json')
  .then(response => response.json())
  .then(files => {
    const createdFilesContainer = document.getElementById('created-files');
    const filePairsContainer = document.getElementById('file-pairs');
    
    // Group files by base name (strip the original-/replacing-/created- prefix)
    const fileGroups = {};
    files.forEach(file => {
      const baseName = file.full_name.replace(/^original-|^replacing-|^created-/, '');
      fileGroups[baseName] = fileGroups[baseName] || {};
      fileGroups[baseName][file.type] = file;
    });

    // 1) Render created-only files (same as before, if you want to keep that)
    for (const baseName in fileGroups) {
      const group = fileGroups[baseName];
      if (group['created'] && !group['original'] && !group['replacing']) {
                const createdFileBlock = document.createElement('div');
                createdFileBlock.classList.add('file-block');
                const fileNameDiv = document.createElement('div');
                fileNameDiv.classList.add('file-name');
                fileNameDiv.textContent = group['created'].full_name;
                const fileTypeDiv = document.createElement('div');
                fileTypeDiv.classList.add('file-type');
                fileTypeDiv.textContent = `Type: ${group['created'].type}`;
                const codeBlockDiv = document.createElement('div');
                codeBlockDiv.classList.add('code-block');
                const codePre = document.createElement('pre');
                const codeCode = document.createElement('code');
                codeCode.classList.add('language-python');
                codeCode.textContent = group['created'].content;
                codePre.appendChild(codeCode);
                codeBlockDiv.appendChild(codePre);
                createdFileBlock.appendChild(fileNameDiv);
                createdFileBlock.appendChild(fileTypeDiv);
                createdFileBlock.appendChild(codeBlockDiv);
                createdFilesContainer.appendChild(createdFileBlock);
                Prism.highlightElement(codeCode);
            }
        }
        // Render original and replacing file pairs
        for (const baseName in fileGroups) {
            const group = fileGroups[baseName];
            const originalObj = group['original'];
            const replacingObj = group['replacing'];
      
            // If we have an "original" and a "replacing", build a diff with preserved lines
            if (originalObj && replacingObj) {
              // Create the parent container
              const fileBlock = document.createElement('div');
              fileBlock.classList.add('file-block');
      
              // Show a filename (baseName or replacing name)
              const fileNameDiv = document.createElement('div');
              fileNameDiv.classList.add('file-name');
              fileNameDiv.textContent = baseName; 
              fileBlock.appendChild(fileNameDiv);
      
              // Generate the diff
              const diffHtml = generateLineByLineDiff(originalObj.content, replacingObj.content);
      
              // Wrap the diff in a code-block
              const codeBlockDiv = document.createElement('div');
              codeBlockDiv.classList.add('code-block');
              codeBlockDiv.innerHTML = diffHtml;
              
              fileBlock.appendChild(codeBlockDiv);
              filePairsContainer.appendChild(fileBlock);
            }
            
            // If only an original OR only a replacing is present, you can handle that 
            // scenario however you prefer (just show one or the other).
          }
        });
      
      // Function to generate line-by-line diff HTML
      function generateLineByLineDiff(originalText, newText) {
        const diffResult = Diff.diffLines(originalText, newText);
        // Build HTML with <span> or <div> tags + classes for line-by-line preservation
        let html = '<pre>';
        diffResult.forEach(part => {
          const lines = escapeHtml(part.value).split('\n');
          lines.forEach(line => {
            if (part.added) {
              html += `<div class="diff-added">${line}</div>`;
            } else if (part.removed) {
              html += `<div class="diff-removed">${line}</div>`;
            } else {
                html += `<div class="diff-unchanged">${line}</div>`;
            
            }
          });
        });
        html += '</pre>';
        return html;
      }
      
      // Helper to avoid injecting HTML special chars
      function escapeHtml(str) {
        return str
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;');
      }