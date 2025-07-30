// directoryTree.js
// Fetch and display the directory tree

// 1. Fetch tree & default_unmarked from the server
fetch('http://127.0.0.1:5050/api/directory_tree')
    .then(response => response.json())
    .then(data => {
        const directoryData = data.tree; // the directory tree (now with relative paths!)
        const defaultUnmarked = data.default_unmarked; 

        const directoryTreeContainer = document.getElementById('directory-tree');
        const treeRoot = buildDirectoryTree(directoryData, defaultUnmarked);
        directoryTreeContainer.appendChild(treeRoot);
    })
    .catch(error => {
        console.error('Error fetching directory tree:', error);
    });

/**
 * Build the directory tree <ul> from the data array
 * @param {Array} data - array of file/folder items
 * @param {Array} defaultUnmarked - items to leave unchecked
 */
function buildDirectoryTree(data, defaultUnmarked) {
    const ul = document.createElement('ul');
    ul.classList.add('directory-list');
    data.forEach(item => {
        const li = createTreeItem(item, defaultUnmarked);
        ul.appendChild(li);
    });
    return ul;
}

/**
 * Create a single <li> for a file or directory
 * @param {Object} item
 * @param {Array} defaultUnmarked
 * @returns {HTMLLIElement}
 */
function createTreeItem(item, defaultUnmarked) {
    const li = document.createElement('li');

    // 1) Create the checkbox
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    // If it's a file, we'll store 'data-path'
    // If it's a directory, we can still store 'data-type' for reference
    checkbox.dataset.type = item.type;

    // Only store the path if it's a file (skip subfolders)
    if (item.type === 'file') {
        checkbox.dataset.path = item.path; // relative path from the server
    } else {
        checkbox.dataset.path = ''; // or omit entirely
    }

    // We'll use item.path (relative) to build a unique ID
    checkbox.id = `checkbox-${item.path.replace(/[^a-zA-Z0-9_\-]/g, '-')}`;

    // 2) Everything checked by default
    checkbox.checked = true;

    // 3) If item.path or item.name is in defaultUnmarked, uncheck
    //    (Adjust logic for partial matches as needed)
    if (defaultUnmarked.some(u => item.path.includes(u))) {
        checkbox.checked = false;
    }

    // 4) Create label
    const label = document.createElement('label');
    label.htmlFor = checkbox.id;
    label.textContent = item.name;

    // Append checkbox & label
    li.appendChild(checkbox);
    li.appendChild(label);

    // If directory, build its children
    if (item.type === 'directory') {
        li.classList.add('directory');
        if (item.children && item.children.length > 0) {
            const childUl = document.createElement('ul');
            childUl.classList.add('nested-directory');

            item.children.forEach(childItem => {
                const childLi = createTreeItem(childItem, defaultUnmarked);
                childUl.appendChild(childLi);
            });

            li.appendChild(childUl);

            // If directory is unchecked by default, hide children
            if (!checkbox.checked) {
                childUl.style.display = 'none'; 
            }
        }
    } else {
        // It's a file
        li.classList.add('file');
    }

    // Listen for changes (user checks/unchecks)
    checkbox.addEventListener('change', handleCheckboxChange);

    return li;
}

/**
 * When user checks/unchecks a box:
 * - If it's a directory, hide/show its child <ul>.
 * - Mark/unmark all child checkboxes accordingly.
 * - Update the parent checkboxes (indeterminate/checked).
 */
function handleCheckboxChange(event) {
    const checkbox = event.target;
    const li = checkbox.closest('li');
    const isChecked = checkbox.checked;

    // If it's a directory, hide/show children
    if (li.classList.contains('directory')) {
        const childUl = li.querySelector('ul');
        if (childUl) {
            childUl.style.display = isChecked ? 'block' : 'none';
        }
        // Also mark/unmark child checkboxes
        const childCheckboxes = li.querySelectorAll('ul li input[type="checkbox"]');
        childCheckboxes.forEach(childCb => {
            childCb.checked = isChecked;
            childCb.indeterminate = false;
        });
    }

    // Update the parent chain for correct indeterminate/check state
    updateParentCheckboxes(li);
}

/**
 * Recursively update parent checkboxes (indeterminate logic).
 */
function updateParentCheckboxes(li) {
    const parentLi = li.parentElement.closest('li');
    if (!parentLi) return;

    const parentCheckbox = parentLi.querySelector('input[type="checkbox"]');
    if (!parentCheckbox) return;

    // Sibling checkboxes of the same parent
    const siblingCheckboxes = parentLi.querySelectorAll('ul > li > input[type="checkbox"]');

    const allChecked = Array.from(siblingCheckboxes).every(cb => cb.checked);
    const someChecked = Array.from(siblingCheckboxes).some(cb => cb.checked || cb.indeterminate);

    if (allChecked) {
        parentCheckbox.checked = true;
        parentCheckbox.indeterminate = false;
    } else if (someChecked) {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = true;
    } else {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = false;
    }

    updateParentCheckboxes(parentLi);
}

/**
 * Gather selected (checked) file paths (ignore directories).
 */
function gatherSelectedPaths() {
    const checkedBoxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const selectedPaths = [];

    checkedBoxes.forEach(cb => {
        // Only add if it's actually a file
        if (cb.dataset.type === 'file' && cb.dataset.path) {
            selectedPaths.push(cb.dataset.path);
        }
    });

    return selectedPaths;
}
