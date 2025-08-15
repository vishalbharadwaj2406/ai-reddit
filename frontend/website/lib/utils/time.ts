// Lightweight relative time formatter using Intl.RelativeTimeFormat
// Accepts Date | string | number and returns values like "3h ago" or "in 2d"

const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });

const DIVISIONS: Array<[unit: Intl.RelativeTimeFormatUnit, amount: number]> = [
  ['year', 365 * 24 * 60 * 60],
  ['month', 30 * 24 * 60 * 60],
  ['week', 7 * 24 * 60 * 60],
  ['day', 24 * 60 * 60],
  ['hour', 60 * 60],
  ['minute', 60],
  ['second', 1],
];

export function formatRelativeTime(input: string | number | Date): string {
  const toMs = (v: string | number | Date) => (v instanceof Date ? v : new Date(v)).getTime();
  const diffSeconds = Math.round((toMs(input) - Date.now()) / 1000);
  const abs = Math.abs(diffSeconds);
  for (const [unit, amount] of DIVISIONS) {
    if (abs >= amount || unit === 'second') {
      const value = Math.round(diffSeconds / amount);
      return rtf.format(value, unit);
    }
  }
  return 'now';
}
