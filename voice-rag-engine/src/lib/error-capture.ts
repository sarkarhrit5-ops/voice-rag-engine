let lastCapturedError: unknown;

type ErrorCaptureGlobal = typeof globalThis & {
  __voiceRagErrorCaptureInstalled?: boolean;
};

function captureError(value: unknown) {
  lastCapturedError = value instanceof Error ? value : new Error(String(value));
}

function installErrorCapture() {
  const globalScope = globalThis as ErrorCaptureGlobal;
  if (globalScope.__voiceRagErrorCaptureInstalled) return;
  globalScope.__voiceRagErrorCaptureInstalled = true;

  const originalConsoleError = console.error.bind(console);
  console.error = (...args: unknown[]) => {
    if (args.length > 0) {
      captureError(args[0]);
    }
    originalConsoleError(...args);
  };

  const processLike = globalScope.process as
    | { on?: (event: string, listener: (error: unknown) => void) => void }
    | undefined;
  processLike?.on?.("uncaughtException", captureError);
  processLike?.on?.("unhandledRejection", captureError);
}

export function consumeLastCapturedError() {
  const error = lastCapturedError;
  lastCapturedError = undefined;
  return error;
}

installErrorCapture();
