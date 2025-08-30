"use client";

import React, { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import { defaultSchema } from "hast-util-sanitize";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import styles from "./MarkdownRenderer.module.css";

/* eslint-disable @typescript-eslint/no-explicit-any */
// Note: This file uses complex third-party markdown/sanitization libraries with difficult-to-type interfaces

// Extend sanitize schema to allow Prism classes and tables
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

export interface MarkdownRendererProps {
	content: string;
	className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className }) => {
	const [copied, setCopied] = useState<string | null>(null);

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
					const child: any = Array.isArray(children) ? children[0] : children;
					const className: string = child?.props?.className || "";
					const match = /language-(\w+)/.exec(className);
					const language = match ? match[1] : undefined;
					const raw = String(child?.props?.children || "").replace(/\n$/, "");

					const onCopy = async () => {
						try {
							await navigator.clipboard.writeText(raw);
							setCopied(language || "code");
							setTimeout(() => setCopied(null), 1500);
						} catch {}
					};

										return (
						<div className={styles.codeBlock}>
																					<div className={`${styles.codeHeader} ${language ? '' : styles.codeHeaderNoBorder}`}>
																							{language ? (
																								<span className={styles.codeLang}>{language}</span>
																							) : <span />}
																							<button className={styles.copyBtn} onClick={onCopy} aria-label={copied && copied === (language || 'code') ? 'Copied' : 'Copy code'} title={copied && copied === (language || 'code') ? 'Copied' : 'Copy code'}>
																								{/* simple two-sheets icon */}
																								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
																									<rect x="9" y="9" width="10" height="10" rx="2" stroke="currentColor" strokeWidth="1.5"/>
																									<rect x="5" y="5" width="10" height="10" rx="2" stroke="currentColor" strokeWidth="1.5" opacity="0.7"/>
																								</svg>
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
									{raw}
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
				},
			}), [copied]);

	return (
		<div className={[styles.markdownRoot, className].filter(Boolean).join(" ")}
			role="article" aria-label="Markdown content">
					<ReactMarkdown
						remarkPlugins={[remarkGfm]}
						rehypePlugins={[[rehypeSanitize, schema]]}
						components={components}
					>
				{content}
			</ReactMarkdown>
		</div>
	);
};

export default MarkdownRenderer;

