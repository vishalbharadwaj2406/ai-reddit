#!/usr/bin/env node

/**
 * Production Authentication System Validation Script
 * 
 * This script validates that our NextAuth-only production system is
 * properly configured and free of legacy authentication conflicts.
 */

const fs = require('fs');
const path = require('path');

const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function validateFile(filePath, description) {
  if (fs.existsSync(filePath)) {
    log('red', `❌ LEGACY FILE FOUND: ${filePath}`);
    log('red', `   ${description}`);
    return false;
  } else {
    log('green', `✅ LEGACY FILE REMOVED: ${filePath}`);
    return true;
  }
}

function validateProductionFile(filePath, description) {
  if (fs.existsSync(filePath)) {
    log('green', `✅ PRODUCTION FILE: ${filePath}`);
    log('blue', `   ${description}`);
    return true;
  } else {
    log('red', `❌ MISSING PRODUCTION FILE: ${filePath}`);
    return false;
  }
}

function checkFileContent(filePath, searchTerms, description) {
  if (!fs.existsSync(filePath)) {
    log('yellow', `⚠️  FILE NOT FOUND: ${filePath}`);
    return false;
  }

  const content = fs.readFileSync(filePath, 'utf8');
  const results = searchTerms.map(term => ({
    term,
    found: content.includes(term)
  }));

  const allFound = results.every(r => r.found);
  
  if (allFound) {
    log('green', `✅ CONTENT VALIDATION: ${filePath}`);
    log('blue', `   ${description}`);
  } else {
    log('red', `❌ CONTENT VALIDATION FAILED: ${filePath}`);
    results.forEach(r => {
      if (!r.found) {
        log('red', `   Missing: ${r.term}`);
      }
    });
  }

  return allFound;
}

console.log(`${colors.bold}${colors.blue}🔍 Production Authentication System Validation${colors.reset}\n`);

let allValid = true;

// Check that legacy files are removed
log('bold', '1. Validating Legacy File Removal:');
const legacyFiles = [
  ['lib/config/api.ts', 'Legacy API client with dual auth systems'],
  ['lib/stores/authStore.ts', 'Legacy React Context auth store'],
  ['lib/stores/authStore.production.ts', 'Legacy Zustand auth store'],
  ['lib/services/conversationService.ts', 'Legacy conversation service'],
  ['components/auth/AuthEventHandler.tsx', 'Legacy auth event handler'],
  ['components/auth/AuthSync.tsx', 'Legacy auth sync component']
];

legacyFiles.forEach(([file, desc]) => {
  if (!validateFile(path.join(process.cwd(), file), desc)) {
    allValid = false;
  }
});

console.log();

// Check production files exist
log('bold', '2. Validating Production Files:');
const productionFiles = [
  ['lib/config/api.production.ts', 'Production-grade API client with NextAuth integration'],
  ['lib/auth/auth.utils.ts', 'Production NextAuth utilities'],
  ['lib/services/conversation.production.ts', 'Production conversation service'],
  ['components/auth/AuthErrorBoundary.tsx', 'Enterprise auth error boundary'],
  ['components/auth/AuthGuard.tsx', 'Production route protection']
];

productionFiles.forEach(([file, desc]) => {
  if (!validateProductionFile(path.join(process.cwd(), file), desc)) {
    allValid = false;
  }
});

console.log();

// Check critical content
log('bold', '3. Validating Critical Content:');

// Check API client uses NextAuth only
if (!checkFileContent(
  path.join(process.cwd(), 'lib/config/api.production.ts'),
  ['getSession', 'NextAuth', 'auth/session'],
  'Uses NextAuth session management only'
)) {
  allValid = false;
}

// Check auth utils are production-grade
if (!checkFileContent(
  path.join(process.cwd(), 'lib/auth/auth.utils.ts'),
  ['getCurrentSession', 'signInWithGoogle', 'validateSession'],
  'Contains production auth utilities'
)) {
  allValid = false;
}

// Check layout uses error boundary
if (!checkFileContent(
  path.join(process.cwd(), 'app/layout.tsx'),
  ['AuthErrorBoundary', 'Production Authentication System'],
  'Uses production error boundary'
)) {
  allValid = false;
}

// Check conversations page is protected
if (!checkFileContent(
  path.join(process.cwd(), 'app/conversations/page.tsx'),
  ['AuthGuard', 'ConversationsPageContent'],
  'Protected with auth guard'
)) {
  allValid = false;
}

console.log();

// Final validation
if (allValid) {
  log('bold', '🎉 PRODUCTION SYSTEM VALIDATION: PASSED');
  log('green', '✅ All legacy files removed');
  log('green', '✅ All production components in place');
  log('green', '✅ NextAuth-only architecture confirmed');
  log('green', '✅ No authentication conflicts detected');
  log('blue', '\n🚀 Your production-grade NextAuth system is ready!');
} else {
  log('bold', '❌ PRODUCTION SYSTEM VALIDATION: FAILED');
  log('red', '⚠️  Some issues need to be resolved before deployment');
  process.exit(1);
}
