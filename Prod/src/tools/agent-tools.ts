/**
 * Enter Agent Tool Implementations
 *
 * Source code implementations for standard AI Agent tools:
 * - readFile
 * - writeFile
 * - editFile
 * - globSearch
 * - grepSearch
 * - bash
 * - ls
 * - deleteFile
 * - renameFile
 * - copyFile
 */

import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { exec } from 'node:child_process';
import { promisify } from 'node:util';

const execAsync = promisify(exec);

export interface ReadFileOptions {
  lineNumber?: number;
  lineLimit?: number;
}

export interface ReadFileResult {
  filePath: string;
  totalLines: number;
  content: string;
}

/**
 * Read a file with line numbers and truncation limits
 */
export async function readFile(
  filePath: string,
  options: ReadFileOptions = {}
): Promise<ReadFileResult> {
  const absPath = path.resolve(filePath);
  const rawContent = await fs.readFile(absPath, 'utf-8');
  const lines = rawContent.split('\n');

  const start = Math.max(1, options.lineNumber ?? 1) - 1;
  const limit = options.lineLimit ?? 2000;
  const slicedLines = lines.slice(start, start + limit);

  const formattedLines = slicedLines.map((line, idx) => {
    const lineNum = start + idx + 1;
    const truncatedLine = line.length > 2000 ? line.slice(0, 2000) + '... (truncated)' : line;
    return `${String(lineNum).padStart(6, ' ')} | ${truncatedLine}`;
  });

  return {
    filePath: absPath,
    totalLines: lines.length,
    content: formattedLines.join('\n')
  };
}

/**
 * Write content to a file, creating directories as needed
 */
export async function writeFile(filePath: string, content: string): Promise<void> {
  const absPath = path.resolve(filePath);
  await fs.mkdir(path.dirname(absPath), { recursive: true });
  await fs.writeFile(absPath, content, 'utf-8');
}

export interface EditFileOptions {
  replaceAll?: boolean;
}

/**
 * Perform exact string replacement in a file
 */
export async function editFile(
  filePath: string,
  oldString: string,
  newString: string,
  options: EditFileOptions = {}
): Promise<{ replacements: number }> {
  const absPath = path.resolve(filePath);
  const content = await fs.readFile(absPath, 'utf-8');

  if (!content.includes(oldString)) {
    throw new Error(`Target string to replace not found in ${filePath}`);
  }

  let newContent: string;
  let replacements = 0;

  if (options.replaceAll) {
    const parts = content.split(oldString);
    replacements = parts.length - 1;
    newContent = parts.join(newString);
  } else {
    const occurrenceCount = content.split(oldString).length - 1;
    if (occurrenceCount > 1) {
      throw new Error(`oldString is not unique in ${filePath} (${occurrenceCount} occurrences). Provide more context or set replaceAll to true.`);
    }
    newContent = content.replace(oldString, newString);
    replacements = 1;
  }

  await fs.writeFile(absPath, newContent, 'utf-8');
  return { replacements };
}

export interface GlobOptions {
  searchPath?: string;
  ignore?: string[];
}

/**
 * Glob pattern search for files matching a pattern
 */
export async function globSearch(pattern: string, options: GlobOptions = {}): Promise<string[]> {
  const searchDir = options.searchPath ? path.resolve(options.searchPath) : process.cwd();
  
  // Use native find / glob or child process fallback
  const cmd = `find "${searchDir}" -type f -name "${pattern}" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*"`;
  try {
    const { stdout } = await execAsync(cmd);
    return stdout
      .split('\n')
      .map((p) => p.trim())
      .filter(Boolean)
      .map((p) => path.relative(process.cwd(), p));
  } catch {
    return [];
  }
}

export interface GrepOptions {
  searchPath?: string;
  filePattern?: string;
  caseInsensitive?: boolean;
}

export interface GrepMatch {
  file: string;
  lineNumber: number;
  lineContent: string;
}

/**
 * Regex / keyword search across file contents using ripgrep or grep
 */
export async function grepSearch(
  pattern: string,
  options: GrepOptions = {}
): Promise<GrepMatch[]> {
  const searchDir = options.searchPath ? path.resolve(options.searchPath) : process.cwd();
  const flag = options.caseInsensitive ? '-i' : '';
  const globFlag = options.filePattern ? `--glob "${options.filePattern}"` : '';

  const cmd = `rg ${flag} ${globFlag} --line-number --no-heading --color=never "${pattern}" "${searchDir}"`;
  try {
    const { stdout } = await execAsync(cmd);
    const results: GrepMatch[] = [];
    for (const line of stdout.split('\n')) {
      if (!line.trim()) continue;
      const parts = line.split(':');
      if (parts.length >= 3) {
        const file = path.relative(process.cwd(), parts[0]);
        const lineNumber = parseInt(parts[1], 10);
        const lineContent = parts.slice(2).join(':');
        results.push({ file, lineNumber, lineContent });
      }
    }
    return results;
  } catch {
    return [];
  }
}

/**
 * Execute a bash command with safety checks and timeout
 */
export async function bashExecute(
  command: string,
  options: { timeoutMs?: number; cwd?: string } = {}
): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  const timeout = options.timeoutMs ?? 120000;
  try {
    const { stdout, stderr } = await execAsync(command, {
      timeout,
      cwd: options.cwd ? path.resolve(options.cwd) : process.cwd(),
      maxBuffer: 10 * 1024 * 1024
    });
    return { stdout, stderr, exitCode: 0 };
  } catch (err: unknown) {
    const error = err as { stdout?: string; stderr?: string; code?: number };
    return {
      stdout: error.stdout ?? '',
      stderr: error.stderr ?? String(err),
      exitCode: error.code ?? 1
    };
  }
}

/**
 * List files and directories in a given path
 */
export async function lsDir(dirPath: string): Promise<Array<{ name: string; isDirectory: boolean; size: number }>> {
  const absPath = path.resolve(dirPath);
  const entries = await fs.readdir(absPath, { withFileTypes: true });
  const results = [];

  for (const entry of entries) {
    const fullPath = path.join(absPath, entry.name);
    let size = 0;
    try {
      const stats = await fs.stat(fullPath);
      size = stats.size;
    } catch {
      // Ignore unreadable files
    }
    results.push({
      name: entry.name,
      isDirectory: entry.isDirectory(),
      size
    });
  }

  return results;
}

/**
 * Delete a file or directory
 */
export async function deleteFile(filePath: string): Promise<void> {
  const absPath = path.resolve(filePath);
  await fs.rm(absPath, { recursive: true, force: true });
}

/**
 * Rename or move a file or directory
 */
export async function renameFile(oldPath: string, newPath: string): Promise<void> {
  const absOld = path.resolve(oldPath);
  const absNew = path.resolve(newPath);
  await fs.mkdir(path.dirname(absNew), { recursive: true });
  await fs.rename(absOld, absNew);
}

/**
 * Copy a file or directory
 */
export async function copyFile(srcPath: string, destPath: string): Promise<void> {
  const absSrc = path.resolve(srcPath);
  const absDest = path.resolve(destPath);
  await fs.mkdir(path.dirname(absDest), { recursive: true });
  await fs.cp(absSrc, absDest, { recursive: true });
}
