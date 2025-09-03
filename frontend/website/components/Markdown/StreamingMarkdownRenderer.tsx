"use client";

import React, { useMemo, useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import { defaultSchema } from "hast-util-sanitize";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import styles from "./MarkdownRenderer.module.css";
import { useDebouncedMarkdown } from "../../hooks/useDebounced";

/* eslint-disable @typescript-eslint/no-explicit-any */

// Same schema as regular markdown renderer
const schema = {
	...(defaultSchema as any),
	tagNames: [
		...((defaultSchema as any).tagNames || []),
		"table",
		"thead",
		"tbody",
		"tr",
		"th",
		"td",
		"del",
	],
	attributes: {
		...((defaultSchema as any).attributes || {}),
		code: [...(((defaultSchema as any).attributes?.code) || []), ["className"]],
		pre: [...(((defaultSchema as any).attributes?.pre) || []), ["className"]],
		span: [...(((defaultSchema as any).attributes?.span) || []), ["className"]],
		a: [
			...(((defaultSchema as any).attributes?.a) || []),
			["href"],
			["target"],
			["rel"],
		],
	},
} as const;

export interface StreamingMarkdownRendererProps {
	content: string;
	className?: string;
	isStreaming?: boolean;
}

/**
 * Streaming-aware markdown renderer that handles incomplete markdown gracefully
 */
export const StreamingMarkdownRenderer: React.FC<StreamingMarkdownRendererProps> = ({ 
	content, 
	className, 
	isStreaming = false 
}) => {
	const [copied, setCopied] = useState<string | null>(null);
	
	// Debounce content updates to reduce re-render frequency during streaming
	const debouncedContent = useDebouncedMarkdown(content, isStreaming);
	
	// Process content to handle incomplete markdown during streaming
	const processedContent = useMemo(() => {
		if (!isStreaming) {
			return debouncedContent;
		}

		// For streaming content, clean up incomplete markdown patterns
		let cleaned = debouncedContent;
		
		// Handle incomplete code blocks
		const codeBlockMatches = cleaned.match(/```[\s\S]*$/);
		if (codeBlockMatches && !codeBlockMatches[0].endsWith('```')) {
			// Add temporary closing to incomplete code block
			cleaned = cleaned + '\n```';
		}
		
		// Handle incomplete headers (# at end of line without text)
		cleaned = cleaned.replace(/#{1,6}\s*$/, '');
		
		// Handle incomplete lists (- or * at end without content)
		cleaned = cleaned.replace(/^[-*+]\s*$/gm, '');
		
		// Handle incomplete links
		cleaned = cleaned.replace(/\[[^\]]*$/g, '');
		cleaned = cleaned.replace(/\]\([^)]*$/g, '');
		
		return cleaned;
	}, [debouncedContent, isStreaming]);

	const components = useMemo(() => ({
		blockquote: (props: any) => <blockquote className={styles.blockquote} {...props} />,
		hr: () => <hr className={styles.hr} />,
		table: (props: any) => <table className={styles.table} {...props} />,
		a: ({ href, children, ...props }: any) => (
			<a href={href} target="_blank" rel="noopener noreferrer nofollow" {...props}>
				{children}
			</a>
		),
		pre: ({ children }: any) => {
			// Expect children[0] to be a <code> element with className like language-*
			const codeElement = React.isValidElement(children) ? children : null;
			
			if (!codeElement || !React.isValidElement(codeElement)) {
				return <pre className={styles.pre}>{children}</pre>;
			}

			const codeProps = codeElement.props as any;
			const className = codeProps?.className || "";
			const match = /language-(\w+)/.exec(className);
			const language = match ? match[1] : "";
			const code = String(codeProps?.children || "").replace(/\n$/, "");

			if (!language) {
				return <pre className={styles.pre}>{children}</pre>;
			}

			return (
				<div className={styles.codeBlockWrapper}>
					<div className={styles.codeBlockHeader}>
						<span className={styles.codeBlockLanguage}>{language}</span>
						<button
							className={styles.codeBlockCopy}
							onClick={() => {
								navigator.clipboard.writeText(code);
								setCopied(code);
								setTimeout(() => setCopied(null), 2000);
							}}
							aria-label="Copy code"
						>
							{copied === code ? "Copied!" : "Copy"}
						</button>
					</div>
					<div className={styles.pre}>
						<SyntaxHighlighter
							language={language}
							style={oneDark}
							PreTag="pre"
							wrapLongLines
							customStyle={{
								background: "transparent",
								margin: 0,
								padding: 0,
							}}
							codeTagProps={{
								style: {
									background: "transparent",
								},
							}}
						>
							{code}
						</SyntaxHighlighter>
					</div>
				</div>
			);
		},
		code({ inline, className, children, ...props }: any) {
			if (inline) {
				return (
					<code className={styles.inlineCode} {...props}>
						{children}
					</code>
				);
			}
			// Block code is handled by `pre`; fall back safely if needed
			return (
				<code className={className} {...props}>
					{children}
				</code>
			);
		}
	}), [copied]);

	return (
		<div className={[styles.markdownRoot, className].filter(Boolean).join(" ")}
			role="article" aria-label="Markdown content">
			<ReactMarkdown
				remarkPlugins={[remarkGfm]}
				rehypePlugins={[[rehypeSanitize, schema]]}
				components={components}
			>
				{processedContent}
			</ReactMarkdown>
			{isStreaming && (
				<span className="inline-block w-0.5 h-4 bg-blue-400 animate-pulse ml-1 align-middle"></span>
			)}
		</div>
	);
};

export default StreamingMarkdownRenderer;
