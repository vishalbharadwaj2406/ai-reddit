/**
 * Layout System TypeScript Interfaces
 * Production-grade type definitions for layout hooks
 */

export interface BaseLayoutSystem {
  /** Page container - full viewport height */
  pageClass: string;
  
  /** Content container - scrollable area */
  contentClass: string;
  
  /** Panel container - positioning context */
  panelClass: string;
}

export interface HeaderLayoutSystem extends BaseLayoutSystem {
  /** Header clearance with content padding */
  headerClearance: React.CSSProperties;
}

export interface ChatLayoutSystem extends HeaderLayoutSystem {
  /** Content clearance for chat (header + input) */
  contentClearance: React.CSSProperties;
  
  /** Input container configuration */
  inputContainer: {
    className: string;
    style: React.CSSProperties;
  };
}

export interface ContentLayoutSystem extends HeaderLayoutSystem {
  /** Content padding for content-only pages */
  contentPadding: React.CSSProperties;
}

/**
 * Glass effect styling
 */
export interface GlassStyles {
  background: string;
  backdropFilter: string;
  WebkitBackdropFilter: string;
  borderTop: string;
  boxShadow: string;
}

/**
 * Typography scale definition
 */
export interface TypographyScale {
  fontSize: string;
  fontWeight: number;
  lineHeight: number;
}
