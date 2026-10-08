"use client";

import { useState } from "react";

export default function CopyCommand({ command }: { command: string }) {
  const [status, setStatus] = useState<"idle" | "copied" | "error">("idle");

  async function copyCommand() {
    try {
      await navigator.clipboard.writeText(command);
      setStatus("copied");
      window.setTimeout(() => setStatus("idle"), 1800);
    } catch {
      setStatus("error");
    }
  }

  return (
    <button
      aria-label={status === "copied" ? "Command copied" : "Copy command"}
      className="copy-button"
      onClick={copyCommand}
      type="button"
    >
      {status === "copied" ? "Copied" : status === "error" ? "Copy failed" : "Copy"}
    </button>
  );
}
