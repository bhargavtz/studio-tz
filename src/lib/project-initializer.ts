import { ProjectManager } from './project-manager';
import { FileNode, ProjectStructure } from '@/types/project';

export function initializeDefaultProject(): void {
  const projectManager = ProjectManager.getInstance();
  
  // Check if project is already initialized
  const currentProject = projectManager.getProject();
  if (currentProject.root.children && currentProject.root.children.length > 0) {
    return; // Project already has files
  }

  // Create default project structure
  const defaultFiles = [
    {
      path: 'index.html',
      content: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Website</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Welcome to My Website</h1>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>
        
        <main>
            <section id="home">
                <h2>Home Section</h2>
                <p>This is the home section of your website.</p>
            </section>
            
            <section id="about">
                <h2>About Section</h2>
                <p>Learn more about what we do.</p>
            </section>
            
            <section id="contact">
                <h2>Contact Section</h2>
                <p>Get in touch with us!</p>
            </section>
        </main>
        
        <footer>
            <p>&copy; 2024 My Website. All rights reserved.</p>
        </footer>
    </div>
    
    <script src="scripts/main.js"></script>
</body>
</html>`,
      type: 'html' as const,
      description: 'Main HTML file'
    },
    {
      path: 'styles/main.css',
      content: `/* Main Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: #333;
    color: white;
    padding: 1rem 0;
    text-align: center;
}

header h1 {
    margin-bottom: 1rem;
}

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: #555;
}

main {
    padding: 2rem 0;
}

section {
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

section h2 {
    margin-bottom: 1rem;
    color: #333;
}

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 1rem 0;
    margin-top: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    section {
        padding: 1rem;
    }
}`,
      type: 'css' as const,
      description: 'Main stylesheet'
    },
    {
      path: 'scripts/main.js',
      content: `// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Website loaded successfully!');
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add active class to navigation based on scroll position
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('nav a[href^="#"]');
        
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (window.pageYOffset >= sectionTop - 60) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
    
    // Add some interactivity
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Utility functions
function showNotification(message, type = 'info') {
    // Create a simple notification system
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = \`
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        background: \${type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        border-radius: 4px;
        z-index: 1000;
        transition: opacity 0.3s;
    \`;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}`,
      type: 'javascript' as const,
      description: 'Main JavaScript file'
    }
  ];

  // Create folders and files
  try {
    // Create styles folder
    projectManager.createFolder('root', 'styles');
    
    // Create scripts folder  
    projectManager.createFolder('root', 'scripts');
    
    // Create files
    defaultFiles.forEach(file => {
      const parts = file.path.split('/');
      const fileName = parts.pop()!;
      const folderPath = parts.join('/');
      
      // Find or create folder
      let parentId = 'root';
      if (folderPath) {
        const folderParts = folderPath.split('/');
        for (const folderName of folderParts) {
          const existingFolder = projectManager.getProject().root.children?.find(
            child => child.type === 'folder' && child.name === folderName
          );
          
          if (existingFolder) {
            parentId = existingFolder.id;
          } else {
            const newFolder = projectManager.createFolder(parentId, folderName);
            parentId = newFolder.id;
          }
        }
      }
      
      // Create file
      projectManager.createFile(parentId, fileName, file.content, file.type);
    });
    
    // Set the main HTML file as active
    const indexFile = projectManager.getProject().root.children?.find(
      child => child.type === 'file' && child.name === 'index.html'
    );
    
    if (indexFile) {
      projectManager.setActiveFile(indexFile.id);
    }
    
    console.log('Default project initialized successfully');
  } catch (error) {
    console.error('Failed to initialize default project:', error);
  }
}

export function resetProject(): void {
  const projectManager = ProjectManager.getInstance();
  
  // Clear all files and folders
  const currentProject = projectManager.getProject();
  if (currentProject.root.children) {
    // Delete all children in reverse order to avoid issues
    const children = [...currentProject.root.children];
    for (let i = children.length - 1; i >= 0; i--) {
      const child = children[i];
      if (child.type === 'file') {
        projectManager.deleteFile(child.id);
      } else if (child.type === 'folder') {
        projectManager.deleteFolder(child.id);
      }
    }
  }
  
  // Reinitialize with default project
  initializeDefaultProject();
}
