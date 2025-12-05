#!/usr/bin/env node

/**
 * Static Site QA/Audit Script
 * 
 * Checks for:
 * - Broken local links and anchors
 * - Missing assets (images, CSS, JS)
 * - Basic HTML validity
 */

const fs = require('fs');
const path = require('path');

// Configuration
const PROJECT_ROOT = process.cwd();
const SCAN_DIR_ARG = process.argv[2];
const SCAN_DIR = SCAN_DIR_ARG ? path.resolve(PROJECT_ROOT, SCAN_DIR_ARG) : PROJECT_ROOT;

// Results storage
const results = {
  filesScanned: 0,
  missingFiles: [],
  missingAnchors: [],
  invalidStructure: []
};

/**
 * Recursively find all HTML files
 */
function findHtmlFiles(dir) {
  const files = [];
  
  if (!fs.existsSync(dir)) {
    return files;
  }
  
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    // Skip node_modules and other common ignore dirs
    if (entry.isDirectory()) {
      if (['node_modules', '.git'].includes(entry.name)) {
        continue;
      }
      files.push(...findHtmlFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

/**
 * Extract all href and src attributes from HTML
 */
function extractReferences(htmlContent) {
  const references = [];
  
  // Extract href from <a> and <link> tags
  const hrefRegex = /<(a|link)[^>]+href=["']([^"']+)["']/gi;
  let match;
  while ((match = hrefRegex.exec(htmlContent)) !== null) {
    references.push({ type: 'href', url: match[2], tag: match[1] });
  }
  
  // Extract src from <img>, <script>, <source>, <iframe>, <embed>
  const srcRegex = /<(img|script|source|iframe|embed)[^>]+src=["']([^"']+)["']/gi;
  while ((match = srcRegex.exec(htmlContent)) !== null) {
    references.push({ type: 'src', url: match[2], tag: match[1] });
  }
  
  return references;
}

/**
 * Extract all id attributes from HTML
 */
function extractIds(htmlContent) {
  const ids = new Set();
  const idRegex = /id=["']([^"']+)["']/gi;
  let match;
  while ((match = idRegex.exec(htmlContent)) !== null) {
    ids.add(match[1]);
  }
  return ids;
}

/**
 * Check if URL should be ignored (external, mailto, tel, etc.)
 */
function shouldIgnore(url) {
  return /^(https?|mailto|tel|javascript|data):/i.test(url);
}

/**
 * Resolve relative path
 */
function resolvePath(url, htmlFilePath) {
  if (url.startsWith('/')) {
    // Absolute from project root
    return path.join(PROJECT_ROOT, url.substring(1));
  } else {
    // Relative to HTML file
    return path.resolve(path.dirname(htmlFilePath), url);
  }
}

/**
 * Check HTML structure validity
 */
function checkHtmlStructure(htmlContent, filePath) {
  const issues = [];
  
  if (!htmlContent.includes('<!DOCTYPE html>') && !htmlContent.includes('<!doctype html>')) {
    issues.push('Missing <!DOCTYPE html>');
  }
  
  if (!htmlContent.includes('<html')) {
    issues.push('Missing <html> tag');
  }
  
  if (!htmlContent.includes('</html>')) {
    issues.push('Missing </html> closing tag');
  }
  
  if (!htmlContent.includes('<head')) {
    issues.push('Missing <head> tag');
  }
  
  if (!htmlContent.includes('<body')) {
    issues.push('Missing <body> tag');
  }
  
  if (issues.length > 0) {
    results.invalidStructure.push({
      file: path.relative(PROJECT_ROOT, filePath),
      issues
    });
  }
}

/**
 * Audit a single HTML file
 */
function auditFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const relativePath = path.relative(PROJECT_ROOT, filePath);
  
  results.filesScanned++;
  
  // Check HTML structure
  checkHtmlStructure(content, filePath);
  
  // Extract references and IDs
  const references = extractReferences(content);
  const ids = extractIds(content);
  
  // Check each reference
  for (const ref of references) {
    const url = ref.url;
    
    // Skip external URLs
    if (shouldIgnore(url)) {
      continue;
    }
    
    // Handle anchors
    if (url.startsWith('#') || url.includes('#')) {
      const anchorMatch = url.match(/#([^?#]+)/);
      if (anchorMatch) {
        const anchorId = anchorMatch[1];
        
        // For same-page anchors, check if ID exists
        if (url.startsWith('#')) {
          if (!ids.has(anchorId)) {
            results.missingAnchors.push({
              file: relativePath,
              anchor: anchorId,
              attribute: ref.type,
              tag: ref.tag
            });
          }
        }
        // For cross-page anchors (/#section), we can't easily verify
        // but we'll note them for manual review if needed
      }
      continue;
    }
    
    // Handle file references
    const resolvedPath = resolvePath(url, filePath);
    
    // Check if file exists
    if (!fs.existsSync(resolvedPath)) {
      results.missingFiles.push({
        file: relativePath,
        reference: url,
        resolvedPath: path.relative(PROJECT_ROOT, resolvedPath),
        attribute: ref.type,
        tag: ref.tag
      });
    }
  }
}

/**
 * Main audit function
 */
function runAudit() {
  console.log('🔍 Starting site audit...\n');
  
  // Determine scan directories
  const scanDirs = [];
  if (SCAN_DIR_ARG) {
    // If specific directory provided, scan only that
    scanDirs.push(SCAN_DIR);
    console.log(`📁 Scanning directory: ${path.relative(PROJECT_ROOT, SCAN_DIR)}\n`);
  } else {
    // Default: scan root and dist/ if it exists
    scanDirs.push(PROJECT_ROOT);
    const distDir = path.join(PROJECT_ROOT, 'dist');
    if (fs.existsSync(distDir)) {
      scanDirs.push(distDir);
    }
    console.log(`📁 Scanning: root${scanDirs.length > 1 ? ' + dist/' : ''}\n`);
  }
  
  // Find all HTML files
  let htmlFiles = [];
  for (const dir of scanDirs) {
    htmlFiles.push(...findHtmlFiles(dir));
  }
  
  // Remove duplicates
  htmlFiles = [...new Set(htmlFiles)];
  
  if (htmlFiles.length === 0) {
    console.log('⚠️  No HTML files found.');
    process.exit(1);
  }
  
  console.log(`Found ${htmlFiles.length} HTML file(s) to audit...\n`);
  
  // Audit each file
  for (const file of htmlFiles) {
    try {
      auditFile(file);
    } catch (error) {
      console.error(`❌ Error auditing ${path.relative(PROJECT_ROOT, file)}:`, error.message);
    }
  }
  
  // Print results
  console.log('\n' + '='.repeat(60));
  console.log('📊 AUDIT SUMMARY');
  console.log('='.repeat(60));
  console.log(`\n✅ Files scanned: ${results.filesScanned}`);
  console.log(`❌ Missing files: ${results.missingFiles.length}`);
  console.log(`🔗 Missing anchors: ${results.missingAnchors.length}`);
  console.log(`⚠️  Invalid HTML structure: ${results.invalidStructure.length}`);
  
  // Print details
  if (results.missingFiles.length > 0) {
    console.log('\n📁 MISSING FILES:');
    console.log('-'.repeat(60));
    for (const item of results.missingFiles) {
      console.log(`  File: ${item.file}`);
      console.log(`    Reference: ${item.reference}`);
      console.log(`    Resolved: ${item.resolvedPath}`);
      console.log(`    Attribute: ${item.attribute} (${item.tag} tag)`);
      console.log('');
    }
  }
  
  if (results.missingAnchors.length > 0) {
    console.log('\n🔗 MISSING ANCHORS:');
    console.log('-'.repeat(60));
    for (const item of results.missingAnchors) {
      console.log(`  File: ${item.file}`);
      console.log(`    Anchor: #${item.anchor}`);
      console.log(`    Attribute: ${item.attribute} (${item.tag} tag)`);
      console.log('');
    }
  }
  
  if (results.invalidStructure.length > 0) {
    console.log('\n⚠️  INVALID HTML STRUCTURE:');
    console.log('-'.repeat(60));
    for (const item of results.invalidStructure) {
      console.log(`  File: ${item.file}`);
      console.log(`    Issues: ${item.issues.join(', ')}`);
      console.log('');
    }
  }
  
  // Final verdict
  const totalIssues = results.missingFiles.length + results.missingAnchors.length + results.invalidStructure.length;
  
  if (totalIssues === 0) {
    console.log('\n✅ Audit passed: no broken local links or missing assets detected.');
    process.exit(0);
  } else {
    console.log(`\n❌ Audit failed: ${totalIssues} issue(s) found.`);
    process.exit(1);
  }
}

// Run audit
runAudit();

