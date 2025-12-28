/**
 * Date utility functions for local timezone handling
 */

/**
 * Get today's date in YYYY-MM-DD format using LOCAL timezone
 * This avoids issues where toISOString() returns UTC date
 * (e.g., at 2:30 AM IST on Saturday, UTC would still be Friday)
 */
export function getLocalDateString(date: Date = new Date()): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Get date from N days ago in YYYY-MM-DD format using LOCAL timezone
 */
export function getLocalDateStringDaysAgo(daysAgo: number): string {
    const date = new Date();
    date.setDate(date.getDate() - daysAgo);
    return getLocalDateString(date);
}
