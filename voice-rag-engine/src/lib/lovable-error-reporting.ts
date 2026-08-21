type ErrorContext = Record<string, unknown>;

export function reportLovableError(error: unknown, context: ErrorContext = {}) {
  if (import.meta.env.DEV) {
    console.error("Captured application error", { error, context });
  }
}
